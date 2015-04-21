class RingBuffer:
    def __init__(self, size):
        self.__size = size
        self.__cache = [(None,None)] * self.__size

    def __setitem__(self, frame_id, frame):
        idx = self.__wrap_index( frame_id)
        self.__cache[idx] = (frame_id, frame)

    def __getitem__(self, frame_id):
        idx = self.__wrap_index( frame_id)
        return self.__cache[idx]

    def __wrap_index(self, index):
        return index % self.__size

    def __str__(self):
        return self.__cache.__str__()

if __name__ == '__main__':
    rb = RingBuffer(5)
    rb[1] = 'f1'
    rb[2] = 'f2'
    
    rb[3] = 'f3'
    rb[4] = 'f4'
    rb[5] = 'f5'
    rb[6] = 'f6'
    rb[7] = 'f7'
    assert(rb[7][1]=='f7')
