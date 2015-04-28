#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
#import modułów klasy bazowej Service oraz kontrolera usługi
from ComssServiceDevelopment.service import Service, ServiceController

import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy
import os
import threading
from time import time

OPACITY = 0.4 # rectangle opacity
SIZE = 0.25 # occupied by rectangle
RECT_DISPLAY_LEN = 3 # seconds?

class MarkFrameService(Service):
    """klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service"""
    
    def __init__(self):
        """"nie"konstruktor, inicjalizator obiektu usługi"""
        #wywołanie metody inicjalizatora klasy nadrzędnej
        super(MarkFrameService, self).__init__()
        self.filters_lock = threading.RLock()
        self.last_rect_shown_time = None

    def declare_outputs(self):
        """deklaracja wyjść"""
        #deklaracja wyjścia "videoOutput" będącego interfejsem
        #wyjściowym konektora msg_stream_connector
        self.declare_output("videoOutput", OutputMessageConnector(self)) 

    def declare_inputs(self):
        """deklaracja wejść"""
        #deklaracja wejścia "videoInput" będącego interfejsem wyjściowym konektora msg_stream_connector
        self.declare_input("videoInput", InputMessageConnector(self)) 

    def run(self):
        """główna metoda usługi"""
        video_input = self.get_input("videoInput")	#obiekt interfejsu wejściowego
        video_output = self.get_output("videoOutput") #obiekt interfejsu wyjściowego

        #pętla główna usługi
        while self.running():
            frame_obj = video_input.read()  #odebranie danych z interfejsu wejściowego
            frame = np.loads(frame_obj)     #załadowanie ramki do obiektu NumPy
            
            # filters
            time_now = time()
            with self.filters_lock:
                current_filters = self.get_parameter("filtersOn")
            if 1 in current_filters:
                # self.set_parameter("filtersOn", [])
                self.update_parameters({"filtersOn": []}) # reset filters
                self.last_rect_shown_time = time_now
                self.__draw_rectangle(frame)
            elif self.last_rect_shown_time and (time_now - self.last_rect_shown_time) < RECT_DISPLAY_LEN:
                self.__draw_rectangle(frame)

            # forward
            video_output.send(frame.dumps()) #przesłanie ramki za pomocą interfejsu wyjściowego

    def __draw_rectangle(self, frame):
        height, width, _ = frame.shape
        overlay = frame.copy()
        cv2.rectangle(overlay,(0,0),(int(width*SIZE),int(height*SIZE)),(255,0,0),-1)
        cv2.addWeighted(overlay, OPACITY, frame, 1 - OPACITY, 0, frame)


if __name__=="__main__":
    #utworzenie obiektu kontrolera usługi
    config_name = os.path.join( os.path.dirname(__file__), "service.json") # f.e. src\mark_frame_service\service.json
    sc = ServiceController(MarkFrameService, config_name)
    sc.start() #uruchomienie usługi
