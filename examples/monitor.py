import logging
import time
import timeit

from senseme import discover


logging.getLogger('__main__')
logging.setLevel = logging.DEBUG

f = discover()[0]

print('No cache')
print(timeit.timeit(f._get_all, number=1))

print('Cache hits')
print(timeit.timeit(f._get_all, number=1))
print(timeit.timeit(f._get_all, number=1))

print('Starting monitor')
f.monitor = True
f.monitor_frequency = 30
f.start_monitor()
print('Sleeping for a bit')
time.sleep(60)

print('This should be a cache hit despite us not calling it in awhile due to monitor')
print(timeit.timeit(f._get_all, number=1))

