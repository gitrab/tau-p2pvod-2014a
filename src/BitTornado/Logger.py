"""
Created on 03/01/2013

 ~~~ DivineSeeders: Assaf Krintza and Nir Malbin ~~
"""

import time
from collections import deque
import os

class Logger:
    
    singletone = None
    
    def __init__(self, filePath, sched, writeInterval = 30):
        self.filePath = filePath
        self.sched = sched
        self.writeInterval = writeInterval
        self.logQueue = deque()
        self._logWork()
        self.append("LOGGER", "Initilized with interval %d" % (self.writeInterval))
        
    def append(self, type, msg):
        self.logQueue.append("[%s] %s: %s" % (time.strftime("%H:%M:%S"), type , msg))
    
    def flush(self):
        self.write(len(self.logQueue))
    
    def write(self, count = 5):
        if (len(self.logQueue) == 0):
            return
        
        with open(self.filePath, 'a') as file:
            writen = 0
            while (writen < count and len(self.logQueue) > 0):
                logMsg = self.logQueue.popleft()
                file.write(logMsg + "\n")
                writen += 1
                
            file.flush()
            
    def _logWork(self):
        self.write()
        self.sched(self._logWork, self.writeInterval)
        
    @staticmethod
    def initLogger(filePath, sched, writeInterval = 30):
        if not os.path.exists(os.path.dirname(filePath)):
            os.makedirs(os.path.dirname(filePath))
        Logger.singletone = Logger(filePath, sched, writeInterval)
        
    @staticmethod
    def getLogger():
        return (Logger.singletone)