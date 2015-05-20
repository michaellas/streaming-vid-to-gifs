#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector
from ComssServiceDevelopment.development import DevServiceController

import sys
import cv2
import json
from Tkinter import *

service_controller = DevServiceController("src/input_descriptor.json")
service_controller.declare_connection("out1", OutputMessageConnector(service_controller))

hosts = {
    # "resize"        :"localhost:11113",
    "loop_detection":"localhost:11115",
    "gif_encoder"   :"localhost:11116"
}

fields = ('max_gif_length [s]',
          'min_gif_length [s]',
          'min_time_between_gifs [s]',
          'max_acceptable_distance',
          'smudge_length [frames]',
          'smudge_opacity [0-1]')

start_vals = ('3',
              '1.5',
              '0.5',
              '1000',
              '5',
              '0.3')

print '>starting input script'

def _send_params_to_host(host_str, new_params):
    import socket
    import json
    print "send to: %s msg: changed !" % host_str
    
    host, port = host_str.split(':')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.sendall(json.dumps(new_params) + '\n')
    s.close()

def get_param_name(text):
    if(text.find(" ") != -1):
        text = text[0:text.find(" ")]
    return text

def update_params(entries):
    # print entries
    s1_params = (0,1,2,3)
    s1_params_dict = {}
    for param_id in s1_params:
        param_name = fields[param_id]
        param_val = entries[param_name].get()
        param_name = get_param_name(param_name)
        print param_name + ":"+param_val
        s1_params_dict[param_name] = param_val
    print ""
    s2_params = (4,5)
    s2_params_dict = {}
    for param_id in s2_params:
        param_name = fields[param_id]
        param_val = entries[param_name].get()
        param_name = get_param_name(param_name)
        print param_name + ":"+param_val
        s2_params_dict[param_name] = param_val
    # send
    _send_params_to_host(hosts['loop_detection'], s1_params_dict)
    # _send_params_to_host(hosts['gif_encoder'], s2_params_dict)

def update_all(root, cam, filters, frame_id):
    from src.utils import print_progress

    read_successful, frame = cam.read()
    if read_successful:
        frame_dump = frame.dumps()
        service_controller.get_connection("out1").send(frame_dump)

        # print progress
        total_frames = cam.get( cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        print_progress(x=frame_id, max=total_frames)

        root.update()
        root.after(20, func=lambda: update_all(root, cam, filters, frame_id+1))
    else:
        print '\nthe show is over'
        print '---end---'
        root.destroy()

def makeform(root, fields):
    # http://www.python-course.eu/tkinter_entry_widgets.php
    entries = {}
    for field,val in zip(fields,start_vals):
        row = Frame(root)
        lab = Label(row, width=22, text=field+": ", anchor='w')
        ent = Entry(row)
        ent.insert(0,val)
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        entries[field] = ent
    return entries

if __name__ == '__main__':
    #read args
    print '>parsing args'
    if len(sys.argv) < 2:
        print 'Please provide input video as first argument'
        exit()
    video_path = sys.argv[1]
    print '>selected video: %s' % video_path

    # read video
    cam = cv2.VideoCapture(video_path)
    if not cam.isOpened():
        print 'could not open selected video, check provided path'
        exit()

    # create UI
    print 'creating window'
    root = Tk()
    root.title("Params")
    ents = makeform(root, fields)
    b1 = Button(root, text='Send params', command=(lambda e=ents: update_params(e)))
    b1.pack(side=LEFT, padx=5, pady=5)

    root.after(0, func=lambda: update_all(root, cam, set(), 0)) 

    print 'starting the main loop'
    root.mainloop()