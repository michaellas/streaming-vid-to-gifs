#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
#import modułów klasy bazowej Service oraz kontrolera usługi
from ComssServiceDevelopment.service import Service, ServiceController

import cv2
import numpy as np
import os

THUMB_WIDTH = 120

class FrameResizeService(Service):
    """klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service"""
    
    def __init__(self):
        """"nie"konstruktor, inicjalizator obiektu usługi"""
        #wywołanie metody inicjalizatora klasy nadrzędnej
        super(FrameResizeService, self).__init__()

    def declare_outputs(self):
        """deklaracja wyjść"""
        #deklaracja wyjścia "videoOutput" będącego interfejsem
        #wyjściowym konektora msg_stream_connector
        self.declare_output("videoOutput", OutputMessageConnector(self)) 
        self.declare_output("videoOutputResized", OutputMessageConnector(self)) 

    def declare_inputs(self):
        """deklaracja wejść"""
        #deklaracja wejścia "videoInput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_input("videoInput", InputMessageConnector(self)) 

    def run(self):
        video_input = self.get_input("videoInput")
        video_output_resized = self.get_output("videoOutputResized")
        video_output = self.get_output("videoOutput")

        while self.running():
            # read frame object
            frame_obj = video_input.read()
            frame = np.loads(frame_obj)
            # resize
            frame_resized = FrameResizeService.__resize_frame(frame)
            # send both normal and resized version
            video_output_resized.send(frame_resized.dumps())
            video_output.send(frame.dumps())

    @staticmethod
    def __resize_frame(frame, expected_w):
        h, width, channels = frame.shape
        scale_factor = expected_w * 1.0 / width
        frame_thumb = cv2.resize( frame, dsize=(0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        return frame_thumb

if __name__=="__main__":
    config_name = os.path.join( os.path.dirname(__file__), "service.json") # f.e. src\mark_frame_service\service.json
    sc = ServiceController(FrameResizeService, config_name)
    sc.start()
