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

def __update_params_for_host(host_str, new_params):
    import socket
    import json
    print "send to: %s msg: changed !" % host_str
    
    host, port = host_str.split(':')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.sendall(json.dumps(new_params) + '\n')
    s.close()

def update_all(root, cam, filters):
    read_successful, frame = cam.read() #odczyt obrazu z kamery
    new_filters = set()
    
    for i in range(3):
        checked_now = checks[i].get() == 1
        checked_previously = i in filters
        # print "prev: %s, now: %s" % (checked_previously, checked_now)
        host = hosts[i]
        if( checked_previously != checked_now):
            # checked change
            print "changed: %d" % i
            to_send = checked_now and [1] or []
            __update_params_for_host( host, {"filtersOn": to_send })
        if checked_now:
            new_filters.add(i)
    filters.clear()
    filters.update(new_filters)

    if read_successful:
        frame_dump = frame.dumps() #zrzut ramki wideo do postaci ciągu bajtów
        service_controller.get_connection("videoInput").send(frame_dump) #wysłanie danych
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
check1=tk.IntVar()
checkbox1 = tk.Checkbutton(root, text="Mark frame", variable=check1)
checkbox1.pack()

check2=tk.IntVar()
checkbox2 = tk.Checkbutton(root, text="LUV conversion", variable=check2)
checkbox2.pack()

check3=tk.IntVar()
checkbox3 = tk.Checkbutton(root, text="Resize", variable=check3)
checkbox3.pack()

checks = [check1,check2,check3]
hosts = ["localhost:11111","localhost:11112","localhost:11113"]

#dołączenie metody update_all do głównej pętli programu, wynika ze specyfiki TKinter
root.after(0, func=lambda: update_all(root, cam, set())) 

print 'starting the main loop'
root.mainloop()