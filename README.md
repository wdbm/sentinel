# sentinel

This program is a security monitoring program that uses video to detect motion, that records motion video, can express speech alerts, can express alarms and attempts to communicate alerts as configured.

![](https://raw.githubusercontent.com/wdbm/sentinel/master/media/motion_detection.gif)

# setup (Ubuntu 16.04 LTS)

Python 2 and OpenCV 2 are required. Specifically, this program has been tested with OpenCV 2.4.9.1 and 2.4.13.5.

Install dependencies.

```Bash
sudo apt update
sudo apt install   \
    libasound-dev  \
    python-dev     \
    python-pyaudio \
    portaudio19-dev\
    python-tk
```

Install OpenCV 2 using the following procedure, which was defined [here](https://gist.github.com/arthurbeggs/06df46af94af7f261513934e56103b30).

```Bash
sudo apt install                     \
    build-essential                  \
    cmake                            \
    libgtk2.0-dev                    \
    pkg-config                       \
    python-dev                       \
    checkinstall                     \
    libavcodec-dev                   \
    libavcodec-dev                   \
    libavformat-dev                  \
    libavformat-dev                  \
    libdc1394-22-dev                 \
    libgstreamer0.10-dev             \
    libgstreamer-plugins-base0.10-dev\
    libgtk2.0-dev                    \
    libjasper-dev                    \
    libjasper-dev                    \
    libjpeg-dev                      \
    libjpeg-dev                      \
    libmp3lame-dev                   \
    libopencore-amrnb-dev            \
    libopencore-amrwb-dev            \
    libopencv-dev                    \
    libpng12-dev                     \
    libqt4-dev                       \
    libswscale-dev                   \
    libswscale-dev                   \
    libtbb-dev                       \
    libtheora-dev                    \
    libtiff5-dev                     \
    libv4l-dev                       \
    libvorbis-dev                    \
    libxine2                         \
    libxvidcore-dev                  \
    python-dev                       \
    python-numpy                     \
    v4l-utils                        \
    x264                             \
    yasm
```

```Bash
wget https://github.com/opencv/opencv/archive/2.4.13.5.zip -O opencv-2.4.13.5.zip
unzip opencv-2.4.13.5.zip
cd opencv-2.4.13.5
mkdir release
cd release
cmake                                \
    -G "Unix Makefiles"              \
    -DCMAKE_CXX_COMPILER=/usr/bin/g++\
    CMAKE_C_COMPILER=/usr/bin/gcc    \
    -DCMAKE_BUILD_TYPE=RELEASE       \
    -DCMAKE_INSTALL_PREFIX=/usr/local\
    -DWITH_TBB=ON                    \
    -DBUILD_NEW_PYTHON_SUPPORT=ON    \
    -DWITH_V4L=ON                    \
    -DINSTALL_C_EXAMPLES=ON          \
    -DINSTALL_PYTHON_EXAMPLES=ON     \
    -DBUILD_EXAMPLES=ON              \
    -DWITH_QT=ON                     \
    -DWITH_OPENGL=ON                 \
    -DBUILD_FAT_JAVA_LIB=ON          \
    -DINSTALL_TO_MANGLED_PATHS=ON    \
    -DINSTALL_CREATE_DISTRIB=ON      \
    -DINSTALL_TESTS=ON               \
    -DENABLE_FAST_MATH=ON            \
    -DWITH_IMAGEIO=ON                \
    -DBUILD_SHARED_LIBS=OFF          \
    -DWITH_GSTREAMER=ON ..
make all -j"$(nproc)"
sudo make install
cd ../../
rm -rf ./opencv-2.4.13.5
sudo apt install python-opencv
echo -e "OpenCV version:"
pkg-config --modversion opencv
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

Migration from OpenCV 2 to OpenCV 3 or 4 is under consideration.
