# onvif-camera-mocking
This project started is a fork from [kate-goldenring/onvif-camera-mocking](https://github.com/kate-goldenring/onvif-camera-mocking)
This project consists of tools and instructions for mocking an ONVIF compliant IP camera and passing an RTSP stream through it.

## Steps
> Note: these steps only work on Linux and have only been tested on Ubuntu 22.04LTS

### 1. Set up your developer machine

1. Install building dependencies
    ```sh
    sudo apt update
    sudo apt install flex bison byacc make m4 autoconf unzip \
        git g++ wget -y
    ```

1. Install gstreamer depdencies
    ```sh
    sudo apt update
    sudo apt install gstreamer-1.0 libgstrtspserver-1.0-dev gstreamer1.0-rtsp \
        gstreamer1.0-plugins-ugly python3-gi
    ```

1. Clone the repository
    ```sh
    git clone https://github.com/fcabrera23/onvif-camera-mock
    ```

### 2. Build the ONVIF server

The [onvif_srvd](./onvif_srvd/) project was forked and update original depdencies to keep it up to date with [gsoap](https://github.com/Genivia/gsoap) version and fix broken dependencies.

1. Build the **onvif_srvd**    
    ```sh
    cd onvif_srvd
    make release
    ```

1. Ensure the build was created - Using `ls` command, check the **onvif_srvd** is available. You should see something like this:

    ```sh
    ubuntu@NUC-Ubuntu:/home/ubuntu/onvif-camera-mocking/onvif_srvd# ls
    generated  gsoap-2.8  LICENSE  Makefile  onvif_srvd  README.md  SDK  src  start_scripts  wsdl
    ```

### 3. Build the WS-Discovery Service

The [wsdd](https://github.com/KoynovStas/wsdd) project was forked and update original depdencies to keep it up to date with [gsoap](https://github.com/Genivia/gsoap) version and fix broken dependencies.

1. Move to the project root folder and build the **wsdd**    
    ```sh
    cd wssd
    make release
    ```

1. Ensure the build was created - Using `ls` command, check the **wssd** is available. You should see something like this:

    ```sh
    ubuntu@NUC-Ubuntu:/home/ubntu/onvif-camera-mocking/wsdd# ls
    CHANGELOG.md  generated  gsoap-2.8  LICENSE  Makefile  README.md  SDK  src  start_scripts  wsdd  wsdl
    ```

### 4. Start the ONVIF and Discovery services with the RTSP feed

1. Run `ifconfig` or `ipconfig` to determine your network interface. Then, pass your interface (such as `eno1`,`eth0`, `eth1`, etc) to the script. The following assumes `eth0`. 

1. Run the **main.py** python script to start the discovery services and RTSP feed.  You can specify the network interface and optionally the resources directory, firmware version of the camera and path to the MP4 streaming video file. The script uses the following environmental variables and defaults: 

    | Argument | Defaults | Description |
    | -------- | -------- | ----------- |
    | INTERFACE | No - Mandatory | Network interface to expose discovery service | 
    | DIRECTORY | Defaults to `$PWD` | The directory of the project | 
    | FIRMWARE | Default to 1.0 |  The "mock" firmware version of the camera |
    | MP4FILE | Default to mocking color stripe video | sPath to the video mp4 location |

    Run the mocking camera using the following command

    ```sh
    export INTERFACE=<interface>
    python3 main.py
    ```

### 5. Ensure that the ONVIF camera service is running and discoverable

Use one of the [tools recommended by onvif_srvd for testing the ONVIF service](https://github.com/KoynovStas/onvif_srvd#testing). 

| Program | OS | 
| ------- | -- | 
| [ONVIF Device Manager](https://sourceforge.net/projects/onvifdm/) | Windows | 
| [ONVIF Device Tool (GUI)](https://lingodigit.com/onvif_nvc.html) | Linux | 
| [gsoap-onvif](https://github.com/consensyx/gsoap-onvif) | Linux |

Ensure to run the tool in the same device or same network as your newly mocked camera. In the tool look for a new camera called **TestDev**.


### Pass an rstp feed through the "camera" (ONVIF service) 
Now that we have a camera connected to the network, lets pass some footage through it. This step can be be run as a container or locally.

1. Run the Python program that uses `videotestsrc` to pass a fake stream through the camera of a vertical bar moving horizonally. The implementation was modified from this [StackOverflow discussion](https://stackoverflow.com/questions/59858898/how-to-convert-a-video-on-disk-to-a-rtsp-stream).
    ```sh
    sudo ./rtsp-feed.py 
    ```

    Optionally, configure the color of the feed by passing a color [in decimal format](https://www.mathsisfun.com/hexadecimal-decimal-colors.html) as an argument, such as the following for blue.
    ```sh
    sudo ./rtsp-feed.py 3093194
    ```

### 5. Cleanup
1. Terminate the ONVIF and Discovery services
    ```sh
    ./scripts/stop-onvif-camera.sh
    ```
    Or if you'd rather 
    ```sh
    curl https://raw.githubusercontent.com/kate-goldenring/onvif-camera-mocking/main/scripts/stop-onvif-camera.sh > ./stop-onvif-camera.sh
    chmod +x ./stop-onvif-camera.sh
    ./stop-onvif-camera.sh
    ```