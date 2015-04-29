#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector
from ComssServiceDevelopment.service import Service, ServiceController

import os
import sys
import json
from GifConverter import GifConverter

OUT_DIR = 'out'

class GifConvertService(Service):
    
    def __init__(self):
        super(GifConvertService, self).__init__()

    def declare_outputs(self):
        pass

    def declare_inputs(self):
        self.declare_input("videoInput", InputMessageConnector(self)) 

    def run(self):
        import socket
        video_input = self.get_input("videoInput")

        ffmpeg_bin = sys.argv[1]
        script = GifConverter(ffmpeg_bin, OUT_DIR)
        while self.running():
            data = video_input.read()
            print data
            try:
                data = json.loads(data)
                req_keys = ['path','w','h','frames']
                if not all (k in data for k in req_keys):
                    raise Exception('Incorrect json keys')
                # print '>> OK !'
                file_path, w, h, frames = data['path'], int(data['w']), int(data['h']), int(data['frames'])
                print [file_path, w, h, frames]
                script(file_path,w,h,frames)
            except Exception as e:
                print 'Read/parse error  %s: "%s"' % (type(e), e)

if __name__=="__main__":
    if len(sys.argv) < 2:
        print 'Please provide ffmpeg executable path as first argument'
        exit()
    config_name = os.path.join( os.path.dirname(__file__), "service.json")
    sc = ServiceController(GifConvertService, config_name)
    sc.start()
