#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

import cv2
import numpy as np
import os
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

            script(frame) # TODO check what it returns
            # TODO send output
            # gif_data_output

if __name__=="__main__":
    config_name = os.path.join( os.path.dirname(__file__), "service.json")
    sc = ServiceController(LoopDetectService, config_name)
    sc.start()
