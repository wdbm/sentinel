#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# sentinel                                                                     #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is a security monitoring program that uses video to detect      #
# motion, that records motion video and attempts to communicate alerts if an   #
# e-mail address is specified.                                                 #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help                      display help message
    --version                       display version and exit
    -v, --verbose                   verbose logging
    -s, --silent                    silent
    -u, --username=USERNAME         username
    --launchdelay=INT               delay (s) before run       [default: 5]
    --recordduration=INT            record time (s)            [default: 20]
    --fps=INT                       camera frames per second   [default: 30]
    --detectionthreshold=INT        detection threshold        [default: 2]
    --recordonmotiondetection=BOOL  record on motion detection [default: true]
    --displaywindows=BOOL           display windows            [default: true]
    --speak=BOOL                    speak on motion detection  [default: true]
    --alarm=BOOL                    alarm on motion detection  [default: true]
    --email=ADDRESS                 e-mail address for alerts  [default: none]
"""

name    = "sentinel"
version = "2017-02-20T1858Z"
logo    = None

import datetime
import docopt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import smtplib
import sys
import threading
import time

import cv2.cv as cv
import propyte
import shijian
import tonescale

def main(options):

    global program
    program = propyte.Program(
        options = options,
        name    = name,
        version = version,
        logo    = logo
    )
    global log
    from propyte import log

    delay_launch               = int(options["--launchdelay"])
    duration_record            = int(options["--recordduration"])
    FPS                        = int(options["--fps"])
    detection_threshold        = int(options["--detectionthreshold"])
    record_on_motion_detection =\
        options["--recordonmotiondetection"].lower() == "true"
    display_windows            = options["--displaywindows"].lower() == "true"
    speak                      = options["--speak"].lower() == "true"
    alarm                      = options["--alarm"].lower() == "true"
    email                      =\
        None if options["--email"].lower() == "none" else options["--email"]

    log.info(
        "\nlaunch in {time} s\n\nPress Escape to exit.\n".format(
            time = delay_launch
        )
    )
    if email is not None:
        log.info(
            "alerts address: {email}\n".format(
                email = email
            )
        )
    else:
        log.info("alerts not to be sent (no e-mail specified)\n")

    detect = motion_detector(
        delay_launch               = delay_launch,
        duration_record            = duration_record,
        detection_threshold        = detection_threshold,
        FPS                        = FPS,
        record_on_motion_detection = True,
        display_windows            = display_windows,
        speak                      = speak,
        alarm                      = alarm,
        email                      = email
    )
    detect.run()

    log.info("")

    program.terminate()

class motion_detector():
    
    def change_detection_threshold(
        self,
        value
        ):

        self.detection_threshold = value
    
    def __init__(
        self,
        delay_launch               = 3,
        duration_record            = 20,
        detection_threshold        = 2,
        FPS                        = 30,
        record_on_motion_detection = True,
        display_windows            = True,
        speak                      = True,
        alarm                      = True,
        email                      = None
        ):

        self.delay_launch               = delay_launch
        self.duration_record            = duration_record
        self.detection_threshold        = detection_threshold
        self.FPS                        = FPS
        self.record_on_motion_detection = record_on_motion_detection
        self.display_windows            = display_windows
        self.speak                      = speak
        self.alarm                      = alarm
        self.email                      = email
        self.video_saver                = None
        self.font                       = None
        self.frame                      = None

        self.capture = cv.CaptureFromCAM(0)
        self.frame   = cv.QueryFrame(self.capture)

        if record_on_motion_detection:
            self.recorder()

        self.frame_grayscale = cv.CreateImage(
                                   cv.GetSize(self.frame), # size
                                   cv.IPL_DEPTH_8U,        # depth
                                   1                       # channels
                               )
        self.average_frame   = cv.CreateImage(
                                   cv.GetSize(self.frame), # size
                                   cv.IPL_DEPTH_32F,       # depth
                                   3                       # channels
                               )
        self.frame_absolute_difference = None
        self.frame_previous            = None
        self.area_frame                = self.frame.width * self.frame.height
        self.area_contours_current     = 0
        self.contours_current          = None
        self.recording                 = False
        self.trigger_time              = 0

        if display_windows:
            cv.NamedWindow(program.name)
            cv.CreateTrackbar(
                "detection threshold: ",
                program.name,
                self.detection_threshold,
                100,
                self.change_detection_threshold
            )

    def recorder(
        self
        ):

        filename = shijian.filename_time_UTC(extension = ".avi")
        codec = cv.CV_FOURCC("D", "I", "V", "X") # MPEG-4 4-character codec code

        log.info(
            "record to {filename}\n".format(
                filename = filename
            )
        )

        self.video_saver = cv.CreateVideoWriter(
            filename,               # filename
            codec,                  # codec
            self.FPS,               # FPS
            cv.GetSize(self.frame), # size
            1                       # bool color
        )
        self.font = cv.InitFont(
            cv.CV_FONT_HERSHEY_PLAIN, # font: font object
            1,                        # font_face: font identifier
            1,                        # hscale: scale horizontal
            0,                        # vscale: scale vertical
            2,                        # shear: tangent to vertical
            5                         # thickness
        )

    def run(
        self
        ):

        time_start = time.time()

        while True:

            frame_current = cv.QueryFrame(self.capture)
            timestamp = time.time()

            self.process_image(frame_current)

            if not self.recording:
                # If motion is detected, depending on configuration, send an
                # alert, start recording and speak an alert.
                if self.movement():
                    self.trigger_time = timestamp
                    if timestamp > time_start + self.delay_launch:
                        log.info(
                            "{timestamp} motion detected".format(
                                timestamp = shijian.time_UTC(
                                    style = "YYYY-MM-DD HH:MM:SS UTC"
                                )
                            )
                        )
                        if self.email is not None:
                            thread_alert = threading.Thread(
                                target = self.alert
                            )
                            thread_alert.daemon = True
                            thread_alert.start()
                        if self.speak:
                            propyte.say(
                                text = "motion detected"
                            )
                        if self.alarm:
                            thread_play_alarm = threading.Thread(
                                target = self.play_alarm
                            )
                            thread_play_alarm.daemon = True
                            thread_play_alarm.start()
                        if self.record_on_motion_detection:
                            log.info("start recording")
                            self.recording = True
                cv.DrawContours(
                    frame_current,         # image
                    self.contours_current, # contours
                    (0, 0, 255),           # external (external contour) color
                    (0, 255, 0),           # hole (internal contour) color
                    1,                     # maximum level
                    2,                     # line thickness
                    cv.CV_FILLED           # line connectivity
                )
            else:
                if timestamp >= self.trigger_time + self.duration_record:
                    log.info("stop recording")
                    self.recording = False
                else:
                    cv.PutText(
                        frame_current,                        # frame
                        shijian.time_UTC(                     #
                            style = "YYYY-MM-DD HH:MM:SS UTC" # text
                        ),                                    # 
                        (25, 30),                             # coordinates
                        self.font,                            # font object
                        0                                     # font scale
                    )
                    cv.WriteFrame(
                        self.video_saver,
                        frame_current
                    )

            if self.display_windows:
                cv.ShowImage(
                    program.name,
                    frame_current
                )

            # Break if Escape is encountered.
            code_key = cv.WaitKey(1) % 0x100
            if code_key == 27 or code_key == 10:
                break

    def process_image(
        self,
        frame
        ):

        cv.Smooth(frame, frame)
        
        if not self.frame_absolute_difference:
            # Create initial values for absolute difference, temporary frame and
            # moving average.
            self.frame_absolute_difference = cv.CloneImage(frame)
            self.frame_previous = cv.CloneImage(frame)
            cv.Convert(
                frame,
                self.average_frame
            )
        else:
            # Calculate the moving average.
            cv.RunningAvg(
                frame,
                self.average_frame,
                0.05
            )
        
        cv.Convert(
            self.average_frame,
            self.frame_previous
        )

        # Calculate the absolute difference between the moving average and the
        # frame.
        cv.AbsDiff(
            frame,
            self.frame_previous,
            self.frame_absolute_difference
        )

        # Convert to grayscale and set threshold.
        cv.CvtColor(
            self.frame_absolute_difference,
            self.frame_grayscale,
            cv.CV_RGB2GRAY
        )
        cv.Threshold(
            self.frame_grayscale, # input array
            self.frame_grayscale, # output array
            50,                   # threshold value
            255,                  # maximum value of threshold types
            cv.CV_THRESH_BINARY   # threshold type
        )

        cv.Dilate(
            self.frame_grayscale, # input array
            self.frame_grayscale, # output array
            None,                 # kernel
            15                    # iterations
        )
        cv.Erode(
            self.frame_grayscale, # input array
            self.frame_grayscale, # output array
            None,                 # kernel
            10                    # iterations
        )

    def movement(
        self
        ):
        
        # Find contours.
        storage  = cv.CreateMemStorage(0)
        contours = cv.FindContours(
            self.frame_grayscale,     # image
            storage,                  # contours
            cv.CV_RETR_EXTERNAL,      # mode: external contours
            cv.CV_CHAIN_APPROX_SIMPLE # method
        )

        self.contours_current = contours

        # Calculate the area for all contours.
        while contours:
            self.area_contours_current += cv.ContourArea(contours)
            contours = contours.h_next()

        # Calculate the percentage of the frame area that is contour area.
        percentage_of_frame_area_that_is_contour_area =\
            (self.area_contours_current * 100) / self.area_frame

        self.area_contours_current = 0
        
        if percentage_of_frame_area_that_is_contour_area >\
            self.detection_threshold:
            return True
        else:
            return False

    def alert(
        self
        ):

        # Create an alert message.

        message = MIMEMultipart("alternative")
        message["Subject"] = program.name + "alert: motion detected"
        message["From"]    = program.name + "@localhost"
        message["To"]      = self.email
        text = """
        motion detected at {timestamp}
        """.format(
            timestamp = self.trigger_time
        )
        message.attach(MIMEText(text, "plain"))

        # Attempt to send the alert message.

        try:
            log.info("send message to {to}".format(
                to = message["To"]
            ))
            server = smtplib.SMTP("localhost")
            server.sendmail(
                message["From"],
                message["To"],
                message.as_string()
            )
            server.quit()
        except smtplib.SMTPException:
           print("e-mail send error")
        time.sleep(5)

    def play_alarm(
        self
        ):
        sound = tonescale.access_sound(
            name = "DynamicLoad_BSPNostromo_Ripley.023"
        )
        sound.repeat(number = 5)
        sound.play(background = True)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
