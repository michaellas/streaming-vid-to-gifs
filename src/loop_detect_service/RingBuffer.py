# TODO 
#import collections # http://stackoverflow.com/questions/4151320/efficient-circular-buffer
# d = collections.deque(maxlen=10)

class RingBuffer:
    def __init__(self, size):
        self.size = size
        self.cache = [None] * self.size

    def __setitem__(self, frame_id, frame):
        self.cache.insert(self.__wrap_index(frame_id), (frame_id, frame))

    def __getitem__(self, frame_id):
        return self.cache[self.__wrap_index(frame_id)]

    def __wrap_index(self, index):
        return index % self.size
