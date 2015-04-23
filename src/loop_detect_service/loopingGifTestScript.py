#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import numpy
import cv2

from FrameComparator import FrameComparator
from RingBuffer import RingBuffer
from Utils import *

'''
TODO use ffmpeg to convert avi to gif
'''

class FrameAnalyzer:
	# config
	max_gif_length = 3 # in seconds
	min_gif_length = 0.8 # in seconds
	min_time_between_gifs = 0.5 # in seconds (min time between gifs)
	thumbnail_frame_width = 150 # in px (compare frames using 150px wide miniature versions)
	max_acceptable_distance = 1000 # used when determining if frames are the same

	# const
	std_fps = 24.0
	max_gif_length_f = int(max_gif_length * std_fps) # in frames
	min_gif_length_f = int(min_gif_length * std_fps) # in frames
	min_time_between_gifs_f = int(min_time_between_gifs * std_fps) # in frames

	def __init__(self):
		self.__frame_id = 0
		self.__id_of_last_anim_end = 0 # id of the last frame of the saved animation
		self.__frame_cache = RingBuffer(self.max_gif_length_f)
		self.__frame_thumbs_cache = RingBuffer(self.max_gif_length_f)
		self.__stats = { 'frames_saved_as_anim': 0, 'frames_dist': [] }

	def run(self, frame_data):
		width, height = FrameAnalyzer.__read_frame_dimensions(frame_data)

		frame_id = self.__frame_id
		thumb = self.__generate_thumb(frame_data) # TODO remove this and use one generated from indep. service
		seq_start, frame_dist = self.__get_frame_from_the_past(thumb)
		if frame_dist:
			self.__stats['frames_dist'].append( frame_dist)

		if seq_start and frame_dist and (seq_start < frame_id) and ( (frame_id-seq_start > self.min_gif_length_f )) and (frame_dist < self.max_acceptable_distance):
			self.__stats['frames_saved_as_anim'] += frame_id - seq_start
			# write anim to file
			# TODO use seq_start + 1
			frames = [ self.__frame_cache[i][1] for i in range(seq_start, frame_id)]
			name = 'out/fragment_{}'.format(frame_id)
			print 'Saving: "%s", total of frames: %d' % (name, frame_id - seq_start)
			write_movie( name, frames, int(width), int(height))
			self.__id_of_last_anim_end = frame_id

		# put frame into buffer
		self.__frame_thumbs_cache[frame_id] = thumb
		self.__frame_cache[frame_id] = frame_data
		self.__frame_id = frame_id + 1

	def __generate_thumb(self, frame):
		'''create thumbnail to speed up comparison'''
		width, _ = FrameAnalyzer.__read_frame_dimensions(frame)
		scale_factor = self.thumbnail_frame_width * 1.0 / width
		# TODO use separate buffer image to not allocate mem. on every frame
		frame_thumb = cv2.resize( frame, dsize=(0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

		# convert frame to CIELUV color space
		#frameLUV = frame_thumb
		frameLUV = cv2.cvtColor(frame_thumb, cv2.COLOR_RGB2LUV)
		
		return frameLUV

	def __get_frame_from_the_past(self, frame):
		# wait some time between recording the gifs
		if self.__frame_id < self.__id_of_last_anim_end + self.min_time_between_gifs_f:
			return None,None

		# get the most similar frame from the past
		frame_id = self.__frame_id
		frame_cmp = FrameComparator(frame)
		frames_to_check_count = self.max_gif_length_f - self.min_gif_length_f
		for dx in range(1, frames_to_check_count):
			# (we have to go forward in the buffer)
			cmp_frame_id, cmp_frame_data = self.__frame_thumbs_cache[frame_id + dx]
			if cmp_frame_id and (cmp_frame_data is not None):
				frame_cmp( cmp_frame_id, cmp_frame_data)
		return frame_cmp.result()

	@staticmethod
	def __read_frame_dimensions(frame):
		h, w, channels = frame.shape
		return w,h

	def _stats(self):
		return self.__stats

	def _current_frame_id(self):
		return self.__frame_id


def main(movie):
	to_percent = lambda x,max: x*100.0/max
	total_frames = movie.get( cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	script = FrameAnalyzer()

	# for every frame
	read_successful = True
	while read_successful:
		read_successful, frame_raw = movie.read()
		if not read_successful: break # either error or last frame

		script.run(frame_raw)
		print_progress( to_percent(script._current_frame_id(), total_frames))

	# print end stats
	print ''
	stats = script._stats()
	frames_saved_as_anim = stats['frames_saved_as_anim']
	percent_stored = to_percent(frames_saved_as_anim, total_frames)
	avg_frame_dist = sum(stats['frames_dist']) / len(stats['frames_dist'])

	log.info( "saved {0}/{1} frames -> {2:.2f}% of movie stored in gifs".format(
		frames_saved_as_anim, total_frames, percent_stored))
	log.info( "avg frame difference: {:.2f}".format( avg_frame_dist))


log = createLogger()
log.info("---start---")

# read file
log.debug("opening movie file")
# movie = read_movie( "data/Big.hero.6.mp4")
movie = read_movie( "data/TheForceAwakensOfficialTeaser-1.mp4")
# movie = read_movie( "data/Tangled2010-1.mp4")

log.debug("\t> success")

# invoke script
main( movie)

# end
cv2.destroyAllWindows()
log.info("---end---")