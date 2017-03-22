# sentinel

This program is a security monitoring program that uses video to detect motion, that records motion video, can express speech alerts, can express alarms and attempts to communicate alerts as configured.

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

Sentinel interacts with a lot of infrastructure. It could be sensible to run sentinel in a loop such that it is restarted in case of crashes.

```Bash
while true; do
    ./sentinel.py                       \
        --telegram=true                 \
        --speak=false                   \
        --alarm=false                   \
        --launchdelay=200               \
        --recipientstelegram=@mulderfbi
    sleep 1200
done
```
