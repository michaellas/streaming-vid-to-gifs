#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
#import modułu klasy testowego kontrolera usługi
from ComssServiceDevelopment.development import DevServiceController

import sys
import cv2 #import modułu biblioteki OpenCV
import Tkinter as tk #import modułu biblioteki Tkinter -- okienka

#utworzenie obiektu kontroletra testowego,
#jako parametr podany jest plik konfiguracji usługi,
#do której "zaślepka" jest dołączana
service_controller = DevServiceController("src/input_descriptor.json")

#deklaracja interfejsu wyjściowego konektora msg_stream_connector,
#należy zwrócić uwagę, iż identyfikator musi być zgodny z WEJŚCIEM usługi,
#do której "zaślepka" jest podłączana
service_controller.declare_connection("videoInput", OutputMessageConnector(service_controller))

print '>starting input script'

def update_all(root, cam, filters):
    read_successful, frame = cam.read() #odczyt obrazu z kamery
    if read_successful:
        frame_dump = frame.dumps() #zrzut ramki wideo do postaci ciągu bajtów
        service_controller.get_connection("out1").send(frame_dump)
        service_controller.get_connection("out2").send(frame_dump)
    root.update()
    root.after(20, func=lambda: update_all(root, cam, filters))

print '>parsing args'
if len(sys.argv) < 2:
    print 'Please provide input video as first argument'
    exit()
video_path = sys.argv[1]
print '>selected video: %s' % video_path

# cam = cv2.VideoCapture("data/Big.hero.6.mp4")
cam = cv2.VideoCapture(video_path)
if not cam.isOpened():
    print 'could not open selected video, check provided path'
    exit()

print 'creating window'
root = tk.Tk()
root.title("Filters") #utworzenie okienka

#obsługa checkbox'a
check1 = tk.IntVar()
checkbox1 = tk.Checkbutton(root, text="--nope--", variable=check1)
checkbox1.pack()

#dołączenie metody update_all do głównej pętli programu, wynika ze specyfiki TKinter
root.after(0, func=lambda: update_all(root, cam, set())) 

print 'starting the main loop'
root.mainloop()