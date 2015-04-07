#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as tk
import threading

#import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector
#import modułu klasy testowego kontrolera usługi
from ComssServiceDevelopment.development import DevServiceController

import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy

#utworzenie obiektu kontroletra testowego, jako parametr podany
#jest plik konfiguracji usługi, do której "zaślepka" jest dołączana
service_controller = DevServiceController("src/filter1service.json")
#deklaracja interfejsu wejściowego konektora msg_stream_connector,
#należy zwrócić uwagę, iż identyfikator musi być zgodny z WYJŚCIEM usługi,
#do której "zaślepka" jest podłączana
service_controller.declare_connection("videoOutput", InputMessageConnector(service_controller))


#utworzenie połączenia wejściwoego należy zwrócić uwagę,
#iż identyfikator musi być zgodny z WYJŚCIEM usługi,
#do której "zaślepka" jest podłączana
connection = service_controller.get_connection("videoOutput")

print 'starting output script'

#główna pętla programu
while True:
    obj = connection.read() #odczyt danych z interfejsu wejściowego
    frame = np.loads(obj) #załadownaie ramki do obiektu NumPy
    cv2.imshow('Camera',frame) #wyświetlenie ramki na ekran
    cv2.waitKey(1)