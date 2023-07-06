#!/usr/bin/env python3
# Run privileged: `sudo /usr/bin/python3 rtsp-feed.py`
import os
import sys
import gi
import subprocess
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib

# Ask wsdd nicely to terminate.
interface = os.environ.get('INTERFACE')
if interface is None:
    print("No interface such as 'eth0' or 'eno1' provided")
    sys.exit(1)

directory = os.environ.get('DIRECTORY')
if directory is None:
    print("No scripts directory provided. Using the directory the script was executed from: {}".format(os.getcwd()))
    directory = os.getcwd() 
else:
    print("Using provided directory. The script was executed from:: {}".format(directory))

firmware_ver = os.environ.get('FIRMWARE')
if firmware_ver is None:  
    print("No firmware version provided. Using default 1.0")
    firmware_ver = "1.0" 
else:
    print("Using provided firmware version: {}".format(firmware_ver))
    
if os.system("pgrep wsdd > /dev/null") == 0:
    print("Killing previous wssd instances")
    os.system("sudo pkill wsdd")

# Forcibly terminate.
if os.system("pgrep wsdd > /dev/null") == 0:
    os.system("sudo pkill -9 wsdd")

# Ask onvif server nicely to terminate.
if os.system("pgrep onvif_srvd > /dev/null") == 0:
    print("Killing previous onvif_srvd instance")
    os.system("sudo pkill onvif_srvd")

# Forcibly terminate.
if os.system("pgrep onvif_srvd > /dev/null") == 0:
    os.system("sudo pkill -9 onvif_srvd")

# Ask onvif server nicely to terminate.
if os.system("pgrep rtsp-feed.py > /dev/null") == 0:
    print("Killing rtsp-feed.py instance")
    os.system("sudo pkill rtsp-feed.py")

# Forcibly terminate.
if os.system("pgrep rtsp-feed.py > /dev/null") == 0:
    os.system("sudo pkill -9 rtsp-feed.py")

ip4 = subprocess.check_output(["/sbin/ip", "-o", "-4", "addr", "list", interface]).decode().split()[3].split('/')[0]
os.system("sudo {}/onvif_srvd/onvif_srvd --ifs {} --scope onvif://www.onvif.org/name/TestDev --scope onvif://www.onvif.org/Profile/S --name RTSP --width 800 --height 600 --url rtsp://{}:8554/stream1 --type MPEG4 --firmware_ver {}".format(directory, interface, ip4, firmware_ver))
os.system("{}/wsdd/wsdd --if_name {} --type tdn:NetworkVideoTransmitter --xaddr http://%s:1000/onvif/device_service --scope \"onvif://www.onvif.org/name/Unknown onvif://www.onvif.org/Profile/Streaming\"".format(directory, interface))

loop = GLib.MainLoop()
Gst.init(None)

class TestRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        GstRtspServer.RTSPMediaFactory.__init__(self)

    def do_create_element(self, url):
        global mp4File
        if (mp4File == ""):
            mock_pipeline = "videotestsrc pattern=bar horizontal-speed=2 background-color=9228238 foreground-color={0} ! x264enc ! queue ! rtph264pay name=pay0 config-interval=1 pt=96".format(mp4File) 
        else:
            #set mp4 file path to filesrc's location property
            src_demux = "filesrc location={} ! qtdemux name=demux".format(mp4File)
            h264_transcode = "demux.video_0"
            mock_pipeline = "{0} {1} ! queue ! rtph264pay name=pay0 config-interval=1 pt=96".format(src_demux, h264_transcode)
 
        print ("Pipeling launching: " + mock_pipeline)
        return Gst.parse_launch(mock_pipeline)

class GstreamerRtspServer():
    def __init__(self):
        self.rtspServer = GstRtspServer.RTSPServer()
        factory = TestRtspMediaFactory()
        factory.set_shared(True)
        mountPoints = self.rtspServer.get_mount_points()
        mountPoints.add_factory("/stream1", factory)
        self.rtspServer.attach(None)

# Optionally pass in video bar color in decimal format
# Choose a color: https://www.mathsisfun.com/hexadecimal-decimal-colors.html
if __name__ == '__main__':
    global mp4File
    mp4File = os.environ.get('MP4FILE')
    if mp4File is None:
        mp4File = 4080751
        print ("Default video bar color is " + str(mp4File))
    else:
        print ("Using provided video file: " + str(mp4File))

    s = GstreamerRtspServer()
    loop.run()