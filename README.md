# sentinel

This program is a security monitoring program that uses video to detect motion, that records motion video, can express speech alerts, can express alarms and attempts to communicate alerts as configured.

![](https://raw.githubusercontent.com/wdbm/sentinel/master/media/motion_detection.gif)

# setup (Ubuntu 16.04)

Python 2 is assumed.

Install OpenCV 2.4.9.1 (`python-opencv=2.4.9.1+dfsg-1.5ubuntu1`, `libopencv-dev=2.4.9.1+dfsg-1.5ubuntu1`).

```Bash
sudo apt install        \
    libasound-dev       \
    libopencv-legacy-dev\
    python-dev          \
    python-opencv       \
    python-pyaudio      \
    portaudio19-dev     \
    python-tk
```

Install sentinel.

```Bash
sudo pip install python_sentinel
```

Manually create an account on a Matrix homeserver. Add the credentials to the scalar configuration file, as described [here](https://github.com/wdbm/scalar).

# usage

```Bash
sentinel --help
```

```Bash
sentinel --display_windows=false --launch_delay=120 --record_duration=15 --message=true
```

In case of connections problems or other problems that might cause a crash, It may be sensible to have `sentinel` restart in the case of a crash. This could be done in a way like the following, perhaps with the function described added to `.bashrc`:

```Bash
run_sentinel(){
    while true; do
        sentinel --display_windows=false --launch_delay=120 --record_duration=15 --message=true
        sleep 5
    done
}

run_sentinel
```

# future

Migration from OpenCV 2 to OpenCV 3 or 4 is under consideration (which would result in compatibility with Ubuntu 18.04).

There are some issues with Ubuntu 16.04.5 LTS. Some possible procedures to advance to a working setup are as follows.

```Bash
sudo apt install     \
    python3.6-dev    \
    python3-distutils\
    portaudio19-dev
```

```Bash
sudo apt install                         \
    libopencv-legacy-dev                 \
    python-opencv=2.4.9.1+dfsg-1.5ubuntu1\
```
