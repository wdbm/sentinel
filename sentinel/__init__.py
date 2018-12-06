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
# motion, that records motion video, can express speech alerts, can express    #
# alarms and attempts to communicate alerts as configured.                     #
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
    -h, --help                         display help message
    --version                          display version and exit

    --fps=INT                          camera frames per second            [default: 30]
    --detection_threshold=INT          detection threshold                 [default: 4]
    --record_on_motion_detection=BOOL  record on motion detection          [default: true]
    --display_windows=BOOL             display windows                     [default: true]
    --record_directory=TEXT            record directory                    [default: ./record]
                                                                           
    --speak=BOOL                       speak on motion detection           [default: false]
    --alarm=BOOL                       alarm on motion detection           [default: false]
    --message=BOOL                     alert via message                   [default: true]
    --instance=BOOL                    add instance identifier to messages
                                       consisting of the node name plus
                                       the first 8 characters of a UUID4   [default: true]

    --launch_delay=INT                 delay (s) before run                [default: 5]
    --record_duration=INT              record time (s)                     [default: 20]
    --day_run_time=TEXT                HHMM--HHMM                          [default: none]
"""

import sys
import datetime
import docopt
import logging
import os
if sys.version_info[0] <= 2:
    from pathlib2 import Path
else:
   from pathlib import Path
import platform
import signal
import threading
import time
import uuid

import cv2.cv as cv
import propyte
import pyprel
import scalar
import shijian
import technicolor
import tonescale

name         = "sentinel"
__version__  = "2018-12-06T0117Z"

global log

def main():
    global log
    log = logging.getLogger(name)
    log.addHandler(technicolor.ColorisingStreamHandler())
    log.setLevel(logging.INFO)
    options = docopt.docopt(__doc__, version = __version__)

    FPS                        =     int(options["--fps"])
    detection_threshold        =     int(options["--detection_threshold"])
    record_on_motion_detection =         options["--record_on_motion_detection"].lower() == "true"
    display_windows            =         options["--display_windows"].lower() == "true"
    record_directory           =         options["--record_directory"]
    speak                      =         options["--speak"].lower() == "true"
    alarm                      =         options["--alarm"].lower() == "true"
    message                    =         options["--message"].lower() == "true"
    instance                   =         options["--instance"].lower() == "true"
    delay_launch               =     int(options["--launch_delay"])
    duration_record            =     int(options["--record_duration"])
    day_run_time               = None if options["--day_run_time"].lower() == "none" else options["--day_run_time"]

    if instance:
        ID = "{node}_{UUID4}: ".format(node = platform.node(), UUID4 = str(uuid.uuid4())[:8])
    else:
        ID = ""

    pyprel.print_line()
    log.info(pyprel.center_string(text = pyprel.render_banner(text = name.upper())))
    pyprel.print_line()
    log.info(name + " " + __version__)
    if message: scalar.alert(message = "{ID}{name} monitoring and alerting started".format(ID = ID, name = name))
    log.info("\n^c to stop\n")
    log.info("\nlaunch motion detection in {time} s\n".format(time = delay_launch))
    detect = motion_detector(
        delay_launch               = delay_launch,
        duration_record            = duration_record,
        detection_threshold        = detection_threshold,
        FPS                        = FPS,
        record_on_motion_detection = record_on_motion_detection,
        display_windows            = display_windows,
        record_directory           = record_directory,
        speak                      = speak,
        alarm                      = alarm,
        message                    = message,
        ID                         = ID,
        day_run_time               = day_run_time
    )
    detect.run()

class motion_detector(object):
    
    def change_detection_threshold(
        self,
        value
        ):
        self.detection_threshold = value
    
    def __init__(
        self,
        delay_launch               = 5,
        duration_record            = 20,
        detection_threshold        = 2,
        FPS                        = 30,
        record_on_motion_detection = True,
        display_windows            = True,
        record_directory           = "./record",
        speak                      = True,
        alarm                      = True,
        message                    = True,
        ID                         = "",
        day_run_time               = None
        ):
        self.delay_launch               = delay_launch
        self.duration_record            = duration_record
        self.detection_threshold        = detection_threshold
        self.FPS                        = FPS
        self.record_on_motion_detection = record_on_motion_detection
        self.display_windows            = display_windows
        self.record_directory           = Path(record_directory).expanduser()
        self.speak                      = speak
        self.alarm                      = alarm
        self.message                    = message
        self.ID                         = ID
        self.day_run_time               = day_run_time
        self.video_saver                = None
        self.font                       = None
        self.frame                      = None
        self.last_image_send_time       = datetime.datetime.utcnow() - datetime.timedelta(days = 1)

        self.capture = cv.CaptureFromCAM(0)
        self.frame   = cv.QueryFrame(self.capture)

        if not self.record_directory.exists():
            log.info("make directory {directory}".format(directory = self.record_directory))
            self.record_directory.mkdir(parents = True)
        if record_on_motion_detection: self.recorder()
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
            cv.NamedWindow(name)
            cv.CreateTrackbar(
                "detection threshold: ",
                name,
                self.detection_threshold,
                100,
                self.change_detection_threshold
            )

    def recorder(
        self
        ):
        filepath = str(self.record_directory) + "/" + shijian.filename_time_UTC(extension = ".avi")
        codec = cv.CV_FOURCC("D", "I", "V", "X") # MPEG-4 4-character codec code
        log.info("record to {filepath}\n".format(filepath = filepath))
        self.video_saver = cv.CreateVideoWriter(
            filepath,               # filepath
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
        time_start = datetime.datetime.utcnow()
        while shijian.in_daily_time_range(time_range = self.day_run_time) in [True, None]:
            frame_current = cv.QueryFrame(self.capture)
            time_current  = datetime.datetime.utcnow()
            self.process_image(frame_current)
            if not self.recording and self.day_run_time is None or shijian.in_daily_time_range(time_range = self.day_run_time):
                # If motion is detected, depending on configuration, send an alert, start recording and speak an alert.
                if self.movement():
                    self.trigger_time = time_current
                    if time_current > time_start + datetime.timedelta(seconds = self.delay_launch):
                        log.info("{timestamp} motion detected".format(timestamp = shijian.time_UTC(style = "YYYY-MM-DD HH:MM:SS UTC")))
                        if self.message: scalar.alert(message = "{ID}motion detected at {timestamp}".format(ID = self.ID, timestamp = self.trigger_time))
                        if self.speak: propyte.say(text = "motion detected")
                        if self.alarm:
                            thread_play_alarm = threading.Thread(target = self.play_alarm)
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
                if time_current >= self.trigger_time + datetime.timedelta(seconds = self.duration_record):
                    log.info("stop recording, watch for motion")
                    self.recording = False
                else:
                    cv.PutText(
                        frame_current,                                       # frame
                        shijian.time_UTC(style = "YYYY-MM-DD HH:MM:SS UTC"), # text
                        (25, 30),                                            # coordinates
                        self.font,                                           # font object
                        0                                                    # font scale
                    )
                    if (datetime.datetime.utcnow() - self.last_image_send_time).total_seconds() >= 60:
                        # Save and, if specified, send an image.
                        filename_image = shijian.filename_time_UTC(extension = ".png")
                        cv.SaveImage(str(self.record_directory) + "/" + filename_image, frame_current)
                        if self.message: scalar.send_image(str(self.record_directory) + "/" + filename_image)
                        self.last_image_send_time = datetime.datetime.utcnow()
                    cv.WriteFrame(self.video_saver, frame_current)
            if self.display_windows:
                cv.ShowImage(name, frame_current)
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
            # Create initial values for absolute difference, temporary frame and moving average.
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
        cv.Convert(self.average_frame, self.frame_previous)
        # Calculate the absolute difference between the moving average and the frame.
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
        if percentage_of_frame_area_that_is_contour_area > self.detection_threshold:
            return True
        else:
            return False

    def play_alarm(self):
        try:
            sound = tonescale.access_sound(name = "DynamicLoad_BSPNostromo_Ripley.023")
            sound.repeat(number = 1)
            sound.play(background = True)
        except:
            pass

def signal_handler(signal, frame):
    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    main()
