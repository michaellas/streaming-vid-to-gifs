#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import threading

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.development import DevServiceController

from GifConverter import video_info


ffmpeg_bin = 'C:\\Users\\Marcin\\Desktop\\ffmpeg-20150215-git-2a72b16-win64-static\\bin\\ffmpeg'
file_path = 'out\\SSPP-gif.avi'

print 'starting stub input script'

config_name = os.path.join( os.path.dirname(__file__), "service.json")
service_controller = DevServiceController(config_name)
service_controller.declare_connection("videoInput", OutputMessageConnector(service_controller))

timer = 2.0 # seconds
send_val = 1
def send_msg():
  global send_val
  print send_val
  # send
  if send_val == 3:
    print '\tsend cmd !'
    msg_obj = {
      'path': file_path,
      'w': w,
      'h': h,
      'frames': frames
    }
    msg = json.dumps(msg_obj)
  else:
    msg = "--Nope--"
  service_controller.get_connection("videoInput").send(msg)
  # schedule next
  threading.Timer(timer, send_msg).start()
  send_val += 1

print 'reading video info'
w,h,frames = video_info(ffmpeg_bin, file_path)

print 'starting the main loop'
send_msg()
