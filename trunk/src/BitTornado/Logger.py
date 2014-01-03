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
        self.typesLogs = {}
        self._logWork()
        self.append("LOGGER", "Initilized with interval %d" % (self.writeInterval))
        
    def append(self, type, msg):
        if not self.typesLogs.has_key(type):
            self.typesLogs[type] = deque()
        
        self.typesLogs[type].append("[%s] %s: %s" % (time.strftime("%H:%M:%S"), type , msg))
    
    def flush(self):
        self.write(-1)
    
    def _writeFromQueue(self, file, queue, count):
        if count == -1:
            count = len(queue)
        
        writen = 0
        while (writen < count and len(queue) > 0):
            logMsg = queue.popleft()
            file.write(logMsg + "\n")
            writen += 1
    
    def write(self, countPerType = 5):
        with open(self.filePath, 'a') as file:
            for type in self.typesLogs.iterkeys():
                self._writeFromQueue(file, self.typesLogs[type], countPerType)
                
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