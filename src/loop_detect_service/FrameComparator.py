import numpy
import cv2

class FrameComparator:
    def __init__(self, cmp_target):
        self.source_frame = cmp_target
        self.most_similar_frame = None # <frame_index, frames_distance>
        #TODO hardcoded
        self.dist_scale_factor = 256.0 / (800 * 334) # normalization / (width * height)

    def __call__(self, frame_id, frame):
        dist = FrameComparator.frames_distance(self.source_frame, frame)
        #dist *= self.dist_scale_factor
        self.__try_set( frame_id, dist)
        pass

    def __try_set( self, compared_frame_id, frame_distance):
        if (not self.most_similar_frame) or frame_distance < self.most_similar_frame[1]:
        #if (not self.most_similar_frame) and frame_distance ==0:
            self.most_similar_frame = (compared_frame_id, frame_distance)

    @staticmethod
    def frames_distance(frame1, frame2):
        return cv2.norm( frame1, frame2, cv2.NORM_L2)
