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
    """A Timer class that does not stop, unless you want it to."""

    def __init__(self, seconds, target):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        print('handled target')
        self._start_timer()

    def _start_timer(self):
        # Code could have been running when cancel was called.
        if self._should_continue:
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()

    def cancel(self):
        if self.thread is not None:
            # Just in case thread is running and cancel fails.
            self._should_continue = False
            self.thread.cancel()

if __name__ == '__main__':
    # Example usage:
    def printer():
        print('ipsem lorem')

    t = PerpetualTimer(3, printer)
    t.start()
    time.sleep(8)
    t.cancel()
