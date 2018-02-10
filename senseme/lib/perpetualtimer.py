"""
PerpetualTimer: Run a function every x seconds until PerpetualTimer.cancel().

Source:
https://stackoverflow.com/questions/12435211/python-threading-timer-repeat-function-every-n-seconds

Example usage:
 def printer():
     print('ipsem lorem')

 t = PerpetualTimer(3, printer)
 t.start()
 time.sleep(8)
 t.cancel()

There is an issue of concern with this code. If the interval is relatively low
compared to the time it takes the handler_function to run much of the time will
be spent in the blocking function and .cancel will not work. Cancel will only
work while a timer is active and nothing is going on.

For example, if seconds=30 and handler_function is blocking for 10 seconds the
Timer will start for 30 seconds, then the handler_function will block for
twenty. The Timer, which is not blocked, will execute again 20 seconds after
the blocking function is done.

One potential solution is to have handler_function be a function that spawns a
thread.

"""

import time
from threading import Timer


class PerpetualTimer:
    def __init__(self, seconds=30, handler_function=None):
        self.time = seconds
        self.h_func = handler_function
        self.thread = Timer(self.time, self.handle_function)

    def handle_function(self):
        self.h_func()
        self.thread = Timer(self.time, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        # TODO: this won't cancel a timer if it is currently executing the h_function
        self.thread.cancel()


if __name__ == '__main__':
    # Example usage:
    def printer():
        print('ipsem lorem')


    t = PerpetualTimer(3, printer)
    t.start()
    time.sleep(8)
    t.cancel()
