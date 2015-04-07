#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading

#import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
#import modułów klasy bazowej Service oraz kontrolera usługi
from ComssServiceDevelopment.service import Service, ServiceController

import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy

class Filter1Service(Service):
    """klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service"""
    
    def __init__(self):
        """"nie"konstruktor, inicjalizator obiektu usługi"""
        #wywołanie metody inicjalizatora klasy nadrzędnej
        super(Filter1Service, self).__init__()
        #obiekt pozwalający na blokadę wątku
        self.filters_lock = threading.RLock()

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
            with self.filters_lock:     #blokada wątku
                current_filters = self.get_parameter("filtersOn") #pobranie wartości parametru "filtersOn"

            #sprawdzenie czy parametr "filtersOn" ma wartość 1, czyli czy ma być stosowany filtr
            if 1 in current_filters:
                #zastosowanie filtru COLOR_BGR2GRAY z biblioteki OpenCV na ramce wideo
                frame = cv2.resize(frame,(120,50))
            video_output.send(frame.dumps()) #przesłanie ramki za pomocą interfejsu wyjściowego

if __name__=="__main__":
    #utworzenie obiektu kontrolera usługi
    sc = ServiceController(Filter1Service, "src/filter1service.json")
    sc.start() #uruchomienie usługi
