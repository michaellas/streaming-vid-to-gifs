#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

import numpy as np
import os
import sys

class DemultiplexerService(Service):
    
    def __init__(self):
        super(DemultiplexerService, self).__init__()

    def declare_outputs(self):
        self.declare_output("out1", OutputMessageConnector(self)) 
        self.declare_output("out2", OutputMessageConnector(self)) 

    def declare_inputs(self):
        self.declare_input("videoInput", InputMessageConnector(self)) 

    def run(self):
        video_input = self.get_input("videoInput")
        out1 = self.get_output("out1")
        out2 = self.get_output("out2")

        while self.running():
            frame_obj = video_input.read()
            frame = np.loads(frame_obj)

            out1.send(frame.dumps())
            out2.send(frame.dumps())


if __name__=="__main__":
    if len(sys.argv) < 2:
        print "Please provide config file as first and only argument"
        exit(1)

    cfg_file = sys.argv[1]
    config_name = os.path.join( os.path.dirname(__file__), cfg_file)
    sc = ServiceController(DemultiplexerService, config_name)
    sc.start()
