import threading

class Debouncer:
    '''
        A simple debouncer class that delays the execution of a function until after a specified delay.
        If the function is called again before the delay has passed, the previous call is cancelled.
    '''

    def __init__(self, func, delay):
        self.func = func
        self.delay = delay
        self.timer = None

    def __call__(self, *args, **kwargs):
        # Cancel the previous timer if it exists
        if self.timer is not None:
            self.timer.cancel()
        
        # Set a new timer that will execute the function after the delay
        self.timer = threading.Timer(self.delay, self.func, args, kwargs)
        self.timer.start()

