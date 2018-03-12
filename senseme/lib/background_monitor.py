"""Background Loop for running a monitor process

Uses a daemon thread, so no delays in exiting.
Don't use this for things that involve writing data, as weird things
may happen if the daemon dies while writing.
"""
import time
import threading


class BackgroundLoop:
    def __init__(self, interval=45, action=None):
        """
        Don't forget to .start() the loop after init.

        :param interval: time to sleep in seconds
        :param action: function to run at interval
        """
        self.interval = interval
        self.action = action
        self.thread = None

    def _loop(self):
        while self.should_continue:
            self.action()
            time.sleep(self.interval)

    def start(self):
        """Start monitor execution."""
        self.should_continue = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop monitor execution."""
        self.should_continue = False


if __name__ == '__main__':
    def do_the_thing():
        """Test things."""
        print('hello world')

    loop = BackgroundLoop(interval=5, action=do_the_thing)
    loop.start()
