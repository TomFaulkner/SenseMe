import logging
import time

logging.getLogger(__name__).addHandler(logging.NullHandler())


class MWT(object):
    """Memoize With Timeout
    
    Example:
        @MWT(timeout=30)
        def do_slow_thing():
            # slow things here
            return hard_earned_result

        print(timeit.timeit(lambda: print(do_slow_thing(), number=5))
        # was really slow the first time, instant on the remaining
    """
    # https://code.activestate.com/recipes/325905-memoize-decorator-with-timeout/
    _caches = {}
    _timeouts = {}

    def __init__(self,timeout=2):
        self.timeout = timeout

    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache

    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout

        def func(*args, **kwargs):
            kw = sorted(kwargs.items())
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                logging.debug('Pulled from cache')
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                logging.debug('Ran function')
                v = self.cache[key] = f(*args, **kwargs), time.time()
            return v[0]
        func.func_name = f.__name__

        return func