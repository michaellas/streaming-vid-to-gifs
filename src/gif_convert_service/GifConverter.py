#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

ffmpeg docs:
https://ffmpeg.org/ffmpeg.html

-y : yes to all
-i filename (input)
-r 
-f fmt (input/output)
-c[:stream_specifier] codec (input/output,per-stream) / -codec[:stream_specifier] codec (input/output,per-stream)
-t duration (input/output)
-s WxH : resize
-ss position (input/output) : seek

other process call:
http://stackoverflow.com/questions/10400556/how-do-i-use-ffmpeg-with-python-by-passing-file-objects-instead-of-locations-to
http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/


TODO crossfade begining/end
need: fps,total_frame_count
~55 frames
~24fps
=blend last 0.5 s -> 12 frames

first:
# ffmpeg -y -ss 2 -i eugene.avi -i eugene2.avi -filter_complex "color=white,fade=out:start_time=1:duration=1[alpha];[0:v][alpha]alphamerge[am];[1:v][am]overlay=0:0" -r 20 -pix_fmt rgb8 out_cross.gif
executing:
ffmpeg -y -ss 2 -i eugene.avi -i eugene2.avi -filter_complex "color=white,fade=out:45:15[alpha];[alpha]scale=800:448[alpha1];[0:v][alpha1]alphamerge[am];[1:v][am]overlay=0:0" -r 20 -pix_fmt rgb8 out_cross.avi

ffmpeg -y -i eugene.avi -i SSPP-gif.avi -filter_complex "color=white,fade=out:45:15[alpha];[alpha]scale=800:448[alpha1];[0:v][alpha1]alphamerge[am];[1:v][am]overlay=0:0" -r 20 -pix_fmt rgb8 out_cross.avi
filter_ = ';'.join([
	# 'color=white,fade=out:%d:%d[alpha]' % (len2-SSPPsec,SSPPsec), # (start,duration)
	# 'color=white,fade=out:30:10[alpha]', # (start,duration)
	'color=white,fade=out:10:10[alpha]', # (start,duration)
	'[alpha]scale=%d:%d[alpha1]' % (w,h),
	'[1:v]scale=%d:%d[over]' % (w,h),
	'[over][alpha1]alphamerge[am]',
	'[0:v][am]overlay=50:0' # 2nd over first
	# '[0:v][over]overlay=50:0'
	# '[0:v][alpha1]overlay=50:0'
	])



TODO use ffserver instead of separate service ? (https://ffmpeg.org/ffserver.html)
OR: https://github.com/vbence/stream-m
looping webms: https://support.mozilla.org/en-US/questions/993718



to gif:
ffmpeg -y -i IN_FILE -r 20 -pix_fmt rgb8 OUT_FILE
f.e. ffmpeg -y -i SSPP-gif.avi -r 20 -s 960x540 -pix_fmt rgb8 out_resized.gif

to webm:
ffmpeg -y -i IN_FILE -c:v libvpx -crf 4 -b:v 2M OUT_FILE
TODO lower bitrate



ffmpeg -f vfwcap -r 16 -i 0 -i http://localhost:8089/ -g 52 -acodec libvorbis -ab 64k -vcodec libvpx -vb 448k -f matroska http://example.com:8080/publish/first?password=secret
ffmpeg -r 16 -i out.webm -g 52 -acodec libvorbis -ab 64k -vcodec libvpx -vb 448k -f matroska http://localhost:8080/publish/first?password=secret
'''

# https://ffmpeg.org/ffmpeg-filters.html#fade
# https://ffmpeg.org/ffmpeg-filters.html#overlay
from subprocess import call
import os


class GifConverter:
	def __init__(self, ffmpeg_bin, out_dir):
		self.ffmpeg_bin = ffmpeg_bin
		self.out_dir = out_dir

	def __call__(self, file_path):#, crossfade_len, crossfade_alpha):
		len1,len2 = 55,20
		fade_start, fade_len = 50,15 # will end 10s after first video guaranteeing 33& alpha on clip end
		# fade_start, fade_len = 45,10
		w,h = 800,448
		
		# extract first frame
		first_frame_path = self.__create_first_frame_image(file_path)
		self.__cross_fade(file_path, first_frame_path, fade_start, fade_len,w,h)

	def __create_first_frame_image(self, video_path):
		frame_path = 'first_frame.png'
		cmd = [self.ffmpeg_bin,
			'-y', # allow override
			'-i', video_path,
			'-t', '1', # only 1 second
			'-r', '1', # one frame per second
			frame_path
			]
		ret_code = call(cmd, shell=True) # should be 0
		return frame_path

	def __cross_fade(self, video_path, first_frame_path, fade_start, fade_len, w, h):
		OUT_FILE = 'out_cross.avi'
		filter_ = ';'.join([
			'color=white,fade=in:%d:%d[alpha]' % (fade_start, fade_len), # (start,duration)
			'[alpha]scale=%d:%d[alpha1]' % (w,h),
			'[1:v]scale=w=%d:h=%d:sws_flags=bicubic[over]' % (w,h),
			'[over][alpha1]alphamerge[am]', # TODO apply to repeated first frame

			'[0:v][am]overlay=x=0:y=0:repeatlast=0' # 2nd over first
			# '[0:v][over]overlay=50:0'
			# '[0:v][alpha1]overlay=50:0'
			])
		cmd = [self.ffmpeg_bin,
			'-y', # allow override
			'-i', video_path,
			# '-i', 'eugene.avi',
			# '-loop', '1','-i', 'img.jpg',
			'-loop', '1','-i', first_frame_path,
			# '-i', 'SSPP-gif.avi',
			'-filter_complex', '"'+filter_+'"',
			#'-r', '20',  # frames per second
			'-preset', 'slow',
			'-pix_fmt', 'rgb8',
			'-b:v', '2M',
			OUT_FILE
			]
		cmd = ' '.join(cmd)
		print( cmd)
		print('*'*15)
		ret_code = call(cmd, shell=True) # should be 0

def read_cmd_args():
	FFMPEG_DIR = 'C:\\Users\\Marcin\\Desktop\\ffmpeg-20150215-git-2a72b16-win64-static\\bin'
	# os.chdir(FFMPEG_DIR)
	FFMPEG_BIN = 'ffmpeg'
	return os.path.join(FFMPEG_DIR,FFMPEG_BIN), 'out', 'out', os.path.join(FFMPEG_DIR,'eugene.avi')


if __name__ == '__main__':
	ffmpeg_bin, tmp_dir, out_dir, file_path = read_cmd_args()
	script = GifConverter(ffmpeg_bin, out_dir)
	script(file_path)
