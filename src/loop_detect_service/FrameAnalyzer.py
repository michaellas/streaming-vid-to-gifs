#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import cv2

from FrameComparator import FrameComparator
from RingBuffer import RingBuffer
from src.utils import log_called_times_decorator, print_progress

class FrameAnalyzer:
	# config
	out_dir = os.path.join('out','avi')
	max_gif_length = 3 # in seconds
	min_gif_length = 1.5 # in seconds
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

	def change_settings(self,
						max_gif_length = None,
						min_gif_length = None,
						min_time_between_gifs = None,
						max_acceptable_distance = None):
		print "max: %s, min: %s, bet: %s, dist: %s" % (max_gif_length,min_gif_length,min_time_between_gifs,max_acceptable_distance)

		try:
			if max_acceptable_distance:
				self.max_acceptable_distance = float(max_acceptable_distance)

			recalc_const_based_settings = False
			if max_gif_length:
				self.max_gif_length = float(max_gif_length)
				recalc_const_based_settings = True
			if min_gif_length:
				self.min_gif_length = float(min_gif_length)
				recalc_const_based_settings = True
			if min_time_between_gifs:
				self.min_time_between_gifs = float(min_time_between_gifs)
				recalc_const_based_settings = True

			if recalc_const_based_settings:
				self.max_gif_length_f = int(self.max_gif_length * std_fps)
				self.min_gif_length_f = int(self.min_gif_length * std_fps)
				self.min_time_between_gifs_f = int(self.min_time_between_gifs * std_fps)
		except:
			pass

	@log_called_times_decorator
	def __call__(self, frame_data, thumb=None):
		loop_data = None
		width, height = FrameAnalyzer.__read_frame_dimensions(frame_data)
		frame_id = self.__frame_id

		# thumb version of frame
		if thumb is None:
			thumb = self.__generate_thumb(frame_data)

		# algo
		seq_start, frame_dist = self.__get_frame_from_the_past(thumb)
		if frame_dist:
			self.__stats['frames_dist'].append( frame_dist)

		# generate & write loop data # TODO use seq_start + 1 as loop start
		if (seq_start and frame_dist
			and (seq_start < frame_id) # well, would be weird otherwise
			and (frame_id-seq_start > self.min_gif_length_f) # check min length
			and (frame_dist < self.max_acceptable_distance)): # first and last frame are ~same
			
			total_frames = int(frame_id - seq_start)
			self.__stats['frames_saved_as_anim'] += total_frames
			# file path
			out_filename = os.path.join(self.out_dir,'fragment_%d.avi' % frame_id)
			print 'Saving: "%s", #frames: %d' % (out_filename, total_frames)
			# frames data
			frames = [ self.__frame_cache[i][1] for i in range(seq_start, frame_id)]
			# write
			FrameAnalyzer.__write_movie( out_filename, frames, width, height)
			# end
			self.__id_of_last_anim_end = frame_id
			loop_data = (out_filename, width, height, total_frames)

		# put frame into buffer
		self.__frame_thumbs_cache[frame_id] = thumb
		self.__frame_cache[frame_id] = frame_data
		self.__frame_id = frame_id + 1
		return loop_data

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
		return int(w),int(h)

	@staticmethod
	def __write_movie(out_filename, frames, width, height):
		layers = 1
		fourcc = cv2.cv.CV_FOURCC(*'XVID')
		out = cv2.VideoWriter( out_filename, fourcc, 24, (width,height))
		for frame in frames:
			out.write(frame)
		out.release()

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

		script(frame_raw)
		print_progress( to_percent(script._current_frame_id(), total_frames))

	# print end stats
	print ''
	stats = script._stats()
	frames_saved_as_anim = stats['frames_saved_as_anim']
	percent_stored = to_percent(frames_saved_as_anim, total_frames)
	avg_frame_dist = sum(stats['frames_dist']) / len(stats['frames_dist'])
	print("saved {0}/{1} frames -> {2:.2f}% of movie stored in gifs".format(
		frames_saved_as_anim, total_frames, percent_stored))
	print( "avg frame difference: {:.2f}".format( avg_frame_dist))


if __name__ == '__main__':
	print "---start---"

	# first arg should be video path
	print '>parsing args'
	if len(sys.argv) < 2:
		print 'Please provide input video as first argument'
		exit()
	video_path = sys.argv[1]
	print '>selected video: %s' % video_path

	# open movie file
	print("opening movie file: \""+video_path+"\"")
	movie = cv2.VideoCapture(video_path)
	if not movie.isOpened():
		print 'could not open selected video, check provided path'
		exit()
	print ">success"

	# invoke script
	main( movie)

	# end
	cv2.destroyAllWindows()
	print "---end---"
