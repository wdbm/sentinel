# sentinel

This program is a security monitoring program that uses video to detect motion, that records motion video, can express speech alerts, can express alarms and attempts to communicate alerts as configured.

![](https://raw.githubusercontent.com/wdbm/sentinel/master/media/motion_detection.gif)

# setup (Ubuntu 16.04)

Install OpenCV 2.4.9.1.

```Bash
sudo apt install python-opencv=2.4.9.1+dfsg-1.5ubuntu1
sudo apt install libopencv-dev=2.4.9.1+dfsg-1.5ubuntu1
```

Install sentinel.

```Bash
sudo pip2 install python_sentinel
```

Manually create an account on a Matrix homeserver. Add the credentials to the scalar configuration file, as described [here](https://github.com/wdbm/scalar).

# usage

```Bash
sentinel --help
```

# future

Migration from OpenCV 2 to OpenCV 3 or 4 is under consideration (which would result in compatibility with Ubuntu 18.04).
