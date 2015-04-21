# TODO 
#import collections # http://stackoverflow.com/questions/4151320/efficient-circular-buffer
# d = collections.deque(maxlen=10)

class RingBuffer:
    def __init__(self, size):
        self.__size = size
        self.__cache = [(None,None)] * self.__size

    def __setitem__(self, frame_id, frame):
        self.__cache.insert(self.__wrap_index(frame_id), (frame_id, frame))

    def __getitem__(self, frame_id):
        return self.__cache[self.__wrap_index(frame_id)]

    def __wrap_index(self, index):
        return index % self.__size
