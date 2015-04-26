#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

ffmpeg docs:
	https://ffmpeg.org/ffmpeg.html
	https://ffmpeg.org/ffmpeg-filters.html

	common options:
	-y : yes to all
	-i filename (input)
	-r : framerate?
	-f fmt (input/output)
	-c[:stream_specifier] codec (input/output,per-stream) / -codec[:stream_specifier] codec (input/output,per-stream)
	-t duration (input/output)
	-s WxH : resize
	-ss position (input/output) : seek

TODO ffserver(https://ffmpeg.org/ffserver.html)
	OR: https://github.com/vbence/stream-m

	stream send:
	ffmpeg -f vfwcap -r 16 -i 0 -i http://localhost:8089/ -g 52 -acodec libvorbis -ab 64k -vcodec libvpx -vb 448k -f matroska http://example.com:8080/publish/first?password=secret
	ffmpeg -r 16 -i out.webm -g 52 -acodec libvorbis -ab 64k -vcodec libvpx -vb 448k -f matroska http://localhost:8080/publish/first?password=secret

other process call:
	http://stackoverflow.com/questions/10400556/how-do-i-use-ffmpeg-with-python-by-passing-file-objects-instead-of-locations-to
	http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/

cmds cheatsheet:
	to gif:
	ffmpeg -y -i IN_FILE -r 20 -pix_fmt rgb8 OUT_FILE

	to webm:
	ffmpeg -y -i IN_FILE -c:v libvpx -crf 4 -b:v 2M OUT_FILE

	loop webms in browser:
	https://support.mozilla.org/en-US/questions/993718
'''

from subprocess import call
import os

class GifConverter:

	fade_len = 5        # fade last 5 seconds
	fade_alpha = 0.33   # on last frame overlayed first frame should have 33% visibility
	first_frame_name = 'first_frame.png'
	out_ext = '.gif'

	def __init__(self, ffmpeg_bin, out_dir, verbose=False):
		self.ffmpeg_bin = ffmpeg_bin
		self.out_dir = out_dir
		self.first_frame = os.path.join(out_dir, GifConverter.first_frame_name)
		self.verbose = verbose

	def __call__(self, file_path, w, h, total_frames):
		# print file_path
		base = os.path.basename(file_path)
		file_name, ext = os.path.splitext(base)
		out_path = os.path.join(out_dir, file_name + GifConverter.out_ext)
		# print out_path

		# f.e. will fade over last 10s guaranteeing 33% alpha on clip end
		fade_start, real_fade_len = int(total_frames - GifConverter.fade_len), int(GifConverter.fade_len / GifConverter.fade_alpha)
		# print(fade_start, real_fade_len)

		# extract first frame
		self.__create_first_frame_image(file_path)

		# exec
		self.__cross_fade(file_path,out_path, fade_start,real_fade_len, w,h)


	def __create_first_frame_image(self, video_path):
		cmd = [self.ffmpeg_bin,
			'-y',                  # allow output file override
			'-i', video_path,      # input0 - video to extract the frame from
			'-t', '1',             # only first second
			'-r', '1',             # one frame per second
			self.first_frame
			]
		cmd = ' '.join(cmd)
		self.__os_call(cmd, self.verbose)

	def __cross_fade(self, video_path, out_path, fade_start, fade_len, w, h):
		overlay_image_over_last_frames_filter = ';'.join([
			'color=white,fade=in:%d:%d[alpha]' % (fade_start, fade_len), # animated alpha channel
			'[alpha]scale=%d:%d[alpha1]' % (w,h),           # scale alpha channel
			'[1:v][alpha1]alphamerge[am]',                  # fade in first frame
			'[0:v][am]overlay=x=0:y=0:repeatlast=0'         # overlay fading first frame over base video
			])
		cmd = [self.ffmpeg_bin,
			'-y',                                # allow output file override
			'-i', video_path,                    # input0 - base video
			'-loop', '1','-i', self.first_frame, # input1 - first frame of the video (needs to be looped)
			'-filter_complex', '"'+overlay_image_over_last_frames_filter+'"', # apply filter
			# '-preset', 'slow',                 # max quality (not needed)
			'-pix_fmt', 'rgb8',                  # result pixel format
			'-b:v', '2M',                        # bitrate (should be high enough)
			out_path
			]
		cmd = ' '.join(cmd)
		self.__os_call(cmd, self.verbose)

	@staticmethod
	def __os_call(cmd_str, verbose):
		# print( cmd_str)
		if verbose:
			ret_code = call(cmd_str, shell=True)
		else:
			with open(os.devnull, "w") as fnull:
				ret_code = call(cmd_str, stdout = fnull, stderr = fnull, shell=True)
		if(ret_code != 0):
			print('ERROR in:')
			print(cmd_str)

	#class end

def read_cmd_args():
	FFMPEG_DIR = 'C:\\Users\\Marcin\\Desktop\\ffmpeg-20150215-git-2a72b16-win64-static\\bin'
	# os.chdir(FFMPEG_DIR)
	FFMPEG_BIN = 'ffmpeg'
	return os.path.join(FFMPEG_DIR,FFMPEG_BIN), 'out', os.path.join(FFMPEG_DIR,'eugene.avi')


if __name__ == '__main__':
	ffmpeg_bin, out_dir, file_path = read_cmd_args()
	script = GifConverter(ffmpeg_bin, out_dir)
	w,h = 800,448
	script(file_path,w,h,55)
