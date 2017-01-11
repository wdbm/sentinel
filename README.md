# sentinel

This program is a security monitoring program that uses video to detect motion, that records motion video and attempts to communicate alerts if an e-mail address is specified.

# setup

```Bash
sudo apt-get install mailutils
sudo pip install python_sentinel
```

# usage

```Bash
./sentinel.py --help
```

```Bash
./sentinel.py --email="mulder@fbi.g0v"
```
