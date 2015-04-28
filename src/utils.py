import time

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

if __name__ == '__main__':
    @log_called_times_decorator
    def ff():
        print 'f'
    
    while True:
        ff()
        time.sleep(1)
