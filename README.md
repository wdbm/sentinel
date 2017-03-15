# sentinel

This program is a security monitoring program that uses video to detect motion, that records motion video and attempts to communicate alerts if an e-mail address is specified.

![](https://raw.githubusercontent.com/wdbm/sentinel/master/media/motion_detection.gif)

# setup

```Bash
sudo apt-get install libopencv-dev
sudo apt-get install python-opencv
sudo apt-get install mailutils
sudo pip install python_sentinel
```

Install OpenCV 2.4.9.1.

Install and set up [propyte](https://github.com/wdbm/propyte) and its dependencies (such as those related to Telegram).

# usage

```Bash
./sentinel.py --help
```

```Bash
./sentinel.py --email="mulder@fbi.g0v"
```
