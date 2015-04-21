#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import numpy
import cv2
import sys

def read_movie(path):
    return cv2.VideoCapture(path)

def write_gif(movie, seq_start, seq_end):
    pass

def write_movie(name, frames):
    #TODO hardcoded
    height, width, layers =  336, 800, 1
    fourcc = cv2.cv.CV_FOURCC(*'XVID')
    out = cv2.VideoWriter( name + '.avi', fourcc, 24, (width,height))
    for frame in frames:
        out.write(frame)
    out.release()

def createLogger():
    consoleLogger = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)5s] %(name)s: %(message)s')
    consoleLogger.setFormatter(formatter)
    logger = logging.getLogger('main')
    logger.addHandler(consoleLogger)
    logger.setLevel(logging.DEBUG)
    return logger

def print_progress( percent):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    bars = int(percent / 5)
    sys.stdout.write("[%-20s] %d%% " % ('='*bars, int(percent)))
    sys.stdout.flush()


'''
# write gif
if frame_id > best_gif_sequence_HARDCODE[0] and frame_id < best_gif_sequence_HARDCODE[1]:
    frames_HARDCODE.append(frame)
    # cv2.imshow('frame',frame)
    # cv2.waitKey(1)
'''