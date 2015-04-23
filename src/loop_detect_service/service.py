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
        pass

    def declare_inputs(self):
        self.declare_input("videoInput", InputMessageConnector(self)) 

    def run(self):
        video_input = self.get_input("videoInput")
        script = FrameAnalyzer()

        while self.running():
            frame_obj = video_input.read()
            frame = np.loads(frame_obj)
            script(frame)

if __name__=="__main__":
    config_name = os.path.join( os.path.dirname(__file__), "service.json")
    sc = ServiceController(LoopDetectService, config_name)
    sc.start()
