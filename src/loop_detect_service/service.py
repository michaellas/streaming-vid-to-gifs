#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

import cv2
import numpy as np
import os
import json
from FrameAnalyzer import FrameAnalyzer

class LoopDetectService(Service):
    
    def __init__(self):
        super(LoopDetectService, self).__init__()
        self.filters_lock = threading.RLock()

    def declare_outputs(self):
        self.declare_output("gifData", OutputMessageConnector(self)) 

    def declare_inputs(self):
        self.declare_input("videoInput", InputMessageConnector(self)) 
        self.declare_input("videoInputResized", InputMessageConnector(self)) 

    def run(self):
        video_input = self.get_input("videoInput")
        video_input_resized = self.get_input("videoInputResized")
        gif_data_output = self.get_output("gifData")
        script = FrameAnalyzer()

        while self.running():
            # read frames - full scale and thumb
            frame_obj = video_input.read()
            frame_obj_resized = video_input_resized.read()
            frame = np.loads(frame_obj)
            frame_resized = np.loads(frame_obj_resized)

            loop_data = script(frame, frame_resized)
            if loop_data and len(loop_data)==4:
                file_path, w, h, frames_count = loop_data
                self.__send_to_next_service(gif_data_output, file_path, w, h, frames_count)
                self.__push_notification()

    def __send_to_next_service(self, out_stream, file_path, w, h, frames_count):
        msg_obj = {
            'path': file_path,
            'w': w,
            'h': h,
            'frames': frames_count
        }
        msg = json.dumps(msg_obj)
        out_stream.send(msg)

    def __push_notification(self):
        '''push notification: "hey, I've just written loop video !" '''
        try:
            import socket
            to_send = [1]
            new_params = {"filtersOn": to_send }
            host, port = 'localhost', 11112
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.sendall(json.dumps(new_params) + '\n')
            s.close()
        except Exception as e:
            print 'push notification error: %s' % type(e)


if __name__=="__main__":
    config_name = os.path.join( os.path.dirname(__file__), "service.json")
    sc = ServiceController(LoopDetectService, config_name)
    sc.start()
