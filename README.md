## Overview

This project provides a set of tools and instructions for mocking an ONVIF-compliant IP camera and passing an RTSP stream to simulate a live video stream. It can be run as a Docker container or built locally. Users can also mount a volume or folder with the container to simulate the RTSP camera with the mounted video file.

> [!NOTE]  
> This project started as a fork from [kate-goldenring/onvif-camera-mocking](https://github.com/kate-goldenring/onvif-camera-mocking)

If you want to use the container without building it, you can download it using the following command:
```bash
docker pull winiotsaleskit.azurecr.io/onvif-camera-mocking:latest
```

## Prerequsites

> [!NOTE]
> These steps only work on Linux and have only been tested on Ubuntu 22.04LTS

1. Install building dependencies
    ```sh
    sudo apt update
    sudo apt install flex bison byacc make m4 autoconf unzip \
        git g++ wget -y
    ```

1. Install gstreamer dependencies
    ```sh
    sudo apt update
    sudo apt install gstreamer-1.0 libgstrtspserver-1.0-dev gstreamer1.0-rtsp \
        gstreamer1.0-plugins-ugly python3-gi
    ```

1. Clone the repository
    ```sh
    git clone https://github.com/fcabrera23/onvif-camera-mock
    ```


## Getting started

#### Build the ONVIF server

The [onvif_srvd](./onvif_srvd/) project was forked, and the updated original dependencies to keep it up to date with [gsoap](https://github.com/Genivia/gsoap) version and fix broken dependencies.

1. Build the **onvif_srvd**    
    ```sh
    cd onvif_srvd
    make release
    ```

1. Ensure the build was created - Using the `ls` command, check the **onvif_srvd** is available. You should see something like this:

    ```sh
    ubuntu@NUC-Ubuntu:/home/ubuntu/onvif-camera-mocking/onvif_srvd# ls
    generated  gsoap-2.8  LICENSE  Makefile  onvif_srvd  README.md  SDK  src  start_scripts  wsdl
    ```

#### Build the WS-Discovery Service

The [wsdd](https://github.com/KoynovStas/wsdd) project was forked, and the updated original dependencies to keep it up to date with [gsoap](https://github.com/Genivia/gsoap) version and fix broken dependencies.

1. Move to the project root folder and build the **wsdd**    
    ```sh
    cd wssd
    make release
    ```

1. Ensure the build was created - Using the `ls` command, check the **used** is available. You should see something like this:

    ```sh
    ubuntu@NUC-Ubuntu:/home/ubuntu/onvif-camera-mocking/wsdd# ls
    CHANGELOG.md  generated soap-2.8 LICENSE  Makefile  README.md  SDK  src  start_scripts  wsdd  wsdl
    ```

#### Start the ONVIF and Discovery services with the RTSP feed

1. Run `ifconfig` or `ipconfig` to determine your network interface. Then, pass your interface (such as `eno1`,`eth0`, `eth1`, etc) to the script. The following assumes `eth0`. 

1. Run the **main.py** python script to start the discovery services and RTSP feed. You can specify the network interface and optionally the resources directory, firmware version of the camera, and path to the MP4 streaming video file. The script uses the following environment variables and defaults: 

    | Argument | Defaults | Description |
    | -------- | -------- | ----------- |
    | INTERFACE | No - Mandatory | Network interface to expose discovery service | 
    | DIRECTORY | Defaults to `$PWD` | The directory of the project | 
    | FIRMWARE | Default to 1.0 |  The "mock" firmware version of the camera |
    | MP4FILE | Default to mocking color stripe video | sPath to the video mp4 location |

    Run the mocking camera using the following command:

    ```sh
    export INTERFACE=<interface>
    python3 main.py
    ```

#### Ensure that the ONVIF camera service is running and discoverable

Use one of the [tools recommended by onvif_srvd for testing the ONVIF service](https://github.com/KoynovStas/onvif_srvd#testing). 

| Program | OS | 
| ------- | -- | 
| [ONVIF Device Manager](https://sourceforge.net/projects/onvifdm/) | Windows | 
| [ONVIF Device Tool (GUI)](https://lingodigit.com/onvif_nvc.html) | Linux | 
| [gsoap-onvif](https://github.com/consensyx/gsoap-onvif) | Linux |

Run the tool on the same device or network as your newly mocked camera. In the tool, look for a new camera called **TestDev**.

### Build Docker container and run it with Kubernetes

You can build this as a container using the [Dockerfile.onvif-camera].

> [!NOTE]
> Building the container can take up to 20-30 minutes

Once built, make sure to run it with the appropriate environment variables mentioned previously.

- If you are using [K3s](https://k3s.io/) on a Linux device, please follow the [ONVIF for IP cameras guide](https://docs.akri.sh/discovery-handlers/onvif).

    Once you have your Kubernetes cluster running and Akri installed, run the following command to enable the ONVIF discovery:
    ```bash
    sudo ip route add 239.255.255.250/32 dev cni0
    ```
    _Note: If you're not using **Flannel**, you may need to check the Kubernetes network interface name and change it above._
    1. Find the IP of the mock ONVIF container:
    ```bash
    kubectl get pods -o wide
    ```
    2. Run `route` and find the network interface name that matches the IP of the ONVIF pod (i.e. `cali909b8c65537`).
    3. Now enable the ONVIF discovery:
    ```bash
    sudo ip route add 239.255.255.250/32 dev <insert interface name>
    ```

- If you are using [AKS Edge Essentials](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-edge-overview), please follow the [Discover ONVIF cameras with Akri](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-edge-how-to-akri-onvif) guide.

     Once you have your Kubernetes cluster running and Akri installed, run the following PowerShell command to enable the ONVIF discovery:
    ```powershell
    Invoke-AksEdgeNodeCommand -command "sudo ip route add 239.255.255.250/32 dev cni0"
    ```
    _Note: If you're not using **Flannel**, you may need to check the Kubernetes network interface name and change it above._
    1. Find the IP of the mock ONVIF container:
    ```powershell
    kubectl get pods -o wide
    ```
    2.Find the network interface name that matches the IP of the ONVIF pod (i.e. `cali909b8c65537`):

    ```powershell
    Invoke-AksEdgeNodeCommand -NodeType "Linux" -command "route"
    ```

    3. Now enable the ONVIF discovery:
    ```powershell
    Invoke-AksEdgeNodeCommand -NodeType "Linux" -command "sudo ip route add 239.255.255.250/32 dev <insert interface name>"
    ```
    
    If you're using **Scalable-cluster** with an **External virtual switch**, you will need to enable the `--dport 3702` and `--sport 3702` firewall rule using the following command:

    ```powershell
    Invoke-AksEdgeNodeCommand -NodeType "Linux" -command "sudo iptables -A INPUT -p udp --dport 3702 -j ACCEPT"
    Invoke-AksEdgeNodeCommand -NodeType "Linux" -command "sudo sed -i '/-A OUTPUT -j ACCEPT/i-A INPUT -p udp -m udp --dport 3702 -j ACCEPT' /etc/systemd/scripts/ip4save"   
    Invoke-AksEdgeNodeCommand -NodeType "Linux" -command "sudo iptables -A INPUT -p udp --sport 3702 -j ACCEPT"
    Invoke-AksEdgeNodeCommand -NodeType "Linux" -command "sudo sed -i '/-A OUTPUT -j ACCEPT/i-A INPUT -p udp -m udp --sport 3702 -j ACCEPT' /etc/systemd/scripts/ip4save" 
    ```

    If you everything was correctly set up, you should see the mocked camera discovered by Akri.

    ```powershell
    PS C:\Users\Administrator\Desktop> kubectl get akrii
    NAME                CONFIG       SHARED   NODES             AGE
    akri-onvif-c9582f   akri-onvif   true     ["node1-ledge"]   7m28s
    PS C:\Users\Administrator\Desktop>
    ```

    #### Using a custom video RTSP feed

    Finally, if you want to create an RTSP feed with a custom video, copy the video file into the AKS-EE host first. For example, if you want to use the *sample.mp4* file from your directory `C:\Users\Admin\sample.mp4`, copy it to the AKS-EE Linux node `/home/aksedge-user/sample.mp4` file using the following cmd:

    ```powershell
    Copy-AksEdgeNodeFile -FromFile C:\Users\fcabrera\Downloads\sample-15s.mp4 -toFile /home/aksedge-user/sample.mp4 -PushFile
    ```

    For more information, see [Copy-AksEdgeNodeFile](https://learn.microsoft.com/en-us/azure/aks/hybrid/reference/aks-edge-ps/copy-aksedgenodefile).

    Last step is to modify your Pod deployment to mount the necessary file and use that file in the RTSP streamer server. The following example uses the public docker container and mounts the file *sample.mp4* to create the RSTP stream, but you can change the deployment for your environment.

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: onvif-camera-mocking
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: onvif-camera-mocking
    strategy:
      type: RollingUpdate
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 1
    minReadySeconds: 5    
    template:
      metadata:
        labels:
          app: onvif-camera-mocking
      spec:
        nodeSelector:
          "kubernetes.io/os": linux
        containers:
        - name: azure-vote-front
          image: winiotsaleskit.azurecr.io/onvif-camera-mocking:latest
          ports:
          - containerPort: 8554
          - containerPort: 1000
          - containerPort: 3702
          env:
          - name: INTERFACE
            value: "eth0"
          - name: DIRECTORY
            value: "/onvif-camera-mock"
          - name: MP4FILE
            value: /mnt/sample.mp4
          volumeMounts:
          - name: sample-volume
            mountPath: /mnt
        volumes:
        - name: sample-volume
          hostPath:
            path: /home/aksedge-user
            type: Directory
    ```

## Resources

- [WSDD - ONVIF WS-Discovery server](https://github.com/KoynovStas/wsdd)
- [ONVIF Device(IP camera) Service server](https://github.com/KoynovStas/onvif_srvd)
- [ONVIF-rs](https://github.com/lumeohq/onvif-rs)
- [ONVIF Org](https://www.onvif.org/)
- [AKS Edge Essentials](https://learn.microsoft.com/en-us/azure/aks/hybrid/aks-edge-overview)