#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import threading

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.development import DevServiceController

from GifConverter import video_info


print 'starting stub input script'
if len(sys.argv) < 3:
  print 'provide FFMPEG_BIN and video file as args'
  print 'provided: ' + str(sys.argv[1:])
  exit()
ffmpeg_bin = sys.argv[1]
file_path = sys.argv[2]

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
