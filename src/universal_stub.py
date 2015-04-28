#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as tk
import threading

from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector
from ComssServiceDevelopment.development import DevServiceController

import cv2
import sys
import numpy as np

'''
Quick and dirty service to end the stream gracefuly.
10075/10070
'''

if len(sys.argv) < 2:
	print "please provide port to stub"
	exit()
ports = map(int, sys.argv[1:])
print 'starting universal sub on port: ' + str(ports)


# replace controller's config on the fly
service_controller = DevServiceController("src/output_descriptor.json")
cfg = service_controller.service_conf
cons = []
for port in ports:
	con_name = 'con_' + str(port)
	cfg['outputs'][con_name] = {
		"port": port,
		"ip": "127.0.0.1"
	}
	service_controller.declare_connection(con_name, InputMessageConnector(service_controller))
	connection = service_controller.get_connection(con_name)
	cons.append(connection)


#
print 'start.. now !'
while True:
	for c in cons:
		data = c.read()
		# print data
