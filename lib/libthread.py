# -*- coding: utf-8 -*-
## {{{ http://code.activestate.com/recipes/577187/ (r9)
__author__ = "Emilio Monti"
__license__ = "MIT"

from Queue import Queue
from threading import Thread
from datetime import datetime
from dateutil import relativedelta
import time

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try: func(*args, **kargs)
            except Exception, e: print e
            self.tasks.task_done()

class ThreadPool(object):
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in xrange(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()  

class LockObject(object):
    def __init__(self, func):
        self.func= func
        self.lock = False
        
    def do(self, s):
        while self.lock:
            print "Can't do!"
            time.sleep(2)
            
        self.lock = True
        print "lock acquired"
        self.func(s)
        self.lock = False
        print "lock released"
