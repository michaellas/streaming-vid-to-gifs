import numpy
import cv2

class FrameComparator:
    def __init__(self, cmp_target):
        self.__source_frame = cmp_target
        self.__result_id = None
        self.__result_distance = None

    def __call__(self, frame_id, frame):
        dist = FrameComparator.frames_distance(self.__source_frame, frame)
        self.__try_set( frame_id, dist)

    def __try_set( self, compared_frame_id, frame_distance):
        #if (not self.__result_id) and frame_distance ==0:
        if (not self.__result_id) or frame_distance < self.__result_distance:
            self.__result_id = compared_frame_id
            self.__result_distance = frame_distance

    def result(self):
        return (self.__result_id, self.__result_distance)

    @staticmethod
    def frames_distance(frame1, frame2):
        return cv2.norm( frame1, frame2, cv2.NORM_L2)
