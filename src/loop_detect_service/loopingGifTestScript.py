#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BH6: 18.17 -19.48
# T: 28.32 28.57

import logging
import numpy
import cv2

from FrameComparator import FrameComparator
from RingBuffer import RingBuffer
from Utils import *

'''
http://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python/
http://docs.opencv.org/trunk/doc/py_tutorials/py_video/py_lucas_kanade/py_lucas_kanade.html#lucas-kanade
http://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html
PIL vs FreeImage vs ImageMagick
'''


# config
MAX_RECORDING_TIME = 3 # in seconds
MIN_GIF_LENGTH = 0.8 # in seconds
GIF_SEPARATION = 0.5 # in seconds (min time between gifs)
THUMBNAIL_FRAME_WIDTH = 150 # in px (compare frames using 150px wide miniature versions)
MAX_ACCEPTABLE_DISTANCE = 1000 # wtf ?! (experimental) used when determining if frames are the same

# const
STD_FPS = 24.0
MAX_RECORDING_TIME_f = int(MAX_RECORDING_TIME * STD_FPS) # in frames
MIN_GIF_LENGTH_f = int(MIN_GIF_LENGTH * STD_FPS) # in frames
GIF_SEPARATION_f = int(GIF_SEPARATION * STD_FPS) # in frames


last_anim_frame = 0 # id of the last frame of the saved animation

def analize_frame(frame_thumbs_cache, frame_id, frame):
	global last_anim_frame
	
	# wait some time between recording the gifs
	if frame_id < last_anim_frame + GIF_SEPARATION_f:
		return None,None

	# get the most similar frame from the past
	frame_cmp = FrameComparator(frame)
	frames_to_check_count = MAX_RECORDING_TIME_f - MIN_GIF_LENGTH_f # TODO move to outer scope
	for dx in range(1, frames_to_check_count):
		# (we have to go forward in the buffer)
		frame_to_check_data = frame_thumbs_cache[frame_id + dx]
		#if frame_to_check_data is not None:
		if frame_to_check_data:
			frame_cmp( frame_to_check_data[0], frame_to_check_data[1])
	return frame_cmp.result()

def main(movie):
	width = movie.get( cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
	height = movie.get( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
	length = movie.get( cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	scale_factor = THUMBNAIL_FRAME_WIDTH * 1.0 / width # used in thumbnail resize
	#scale_factor_giffed = 400.0 / width # used in thumbnail resize

	frame_id = 0
	stats = { 'frames_saved_as_anim': 0, 'frames_dist': [] }
	frame_cache = RingBuffer(MAX_RECORDING_TIME_f)
	frame_thumbs_cache = RingBuffer(MAX_RECORDING_TIME_f)

	# for every frame
	read_successful = True
	while read_successful:
		read_successful, frame_raw = movie.read()
		if not read_successful: break
		if frame_id > 2000: break

		# load frame to numpy array (use only when frame_raw is string )
		# frame = numpy.loads(frame_raw) # movie read through network
		frame = frame_raw # movie read from the disc

		# create thumbnail to speed up comparison
		# TODO use separate image to not allocate mem. on every frame
		frame_thumb = cv2.resize( frame, dsize=(0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
		#frame_to_gif = cv2.resize( frame, dsize=(0,0), fx=scale_factor_giffed, fy=scale_factor_giffed, interpolation=cv2.INTER_CUBIC)
		frame_to_gif = frame
		
		# convert frame to CIELUV color space
		# frameLUV = cv2.cvtColor(frame_thumb, cv2.COLOR_RGB2LUV)
		frameLUV = frame_thumb

		seq_start, frame_dist = analize_frame(frame_thumbs_cache, frame_id, frameLUV) # either None or id of the frame from the past
		if seq_start:
			stats['frames_dist'].append( frame_dist)
			if frame_dist < MAX_ACCEPTABLE_DISTANCE and seq_start < frame_id:
				#print seq_start, frame_id
				stats['frames_saved_as_anim'] += frame_id - seq_start
				# write anim to file
				frames = [ frame_cache[i][1] for i in range(seq_start, frame_id)]
				name = 'out/fragment_{}'.format(frame_id)
				write_movie( name, frames)
				last_anim_frame = frame_id

		# put frame into buffer
		frame_thumbs_cache[frame_id] = frameLUV
		frame_cache[frame_id] = frame_to_gif
		frame_id = frame_id + 1
		print_progress( frame_id * 100 / length)

	print ''
	log.info( "{0}/{1} = {2:.2f}% of movie stored in gifs".format(
		stats['frames_saved_as_anim'], frame_id,
		( stats['frames_saved_as_anim'] * 100.0 / frame_id)))
	avg = sum(stats['frames_dist']) / len(stats['frames_dist'])
	log.info( "avg frame difference: {:.2f}".format( avg))


log = createLogger()
log.info("---start---")

# read file
log.debug("opening movie file")
# movie = read_movie( "data/Big.hero.6-1.m4v")
movie = read_movie( "data/Big.hero.6.mp4")
log.debug("\t> success")

# invoke script
main( movie)

# end
cv2.destroyAllWindows()
log.info("---end---")