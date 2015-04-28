import time
import sys

def log_called_times_decorator(func):
    def wrapper(*args):
        wrapper.count += 1
        # print "The function I modify has been called {0} times(s).".format(wrapper.count)
        now = time.time()
        if now - wrapper.last_log > wrapper.dt:
            print '[DEBUG] In last %ds %s() was called %d times' % (wrapper.dt,func.__name__,wrapper.count)
            wrapper.count = 0
            wrapper.last_log = now
        func(*args)
    wrapper.count = 0
    wrapper.last_log = time.time()
    wrapper.dt = 3
    return wrapper

def print_progress( percent=None, x=0, max=100):
    if not percent:
        percent = x*100.0/max
    sys.stdout.write('\r')
    bars = int(percent / 5)
    sys.stdout.write("[%-20s] %d%% " % ('='*bars, int(percent)))
    sys.stdout.flush()

if __name__ == '__main__':
    '''
    @log_called_times_decorator
    def ff():
        print 'f'
    
    while True:
        ff()
        time.sleep(1)
    '''
    
    print_progress(45)
    print ''
    print_progress(x=20,max=200)