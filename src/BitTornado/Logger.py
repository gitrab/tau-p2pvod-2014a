"""
Created on 03/01/2013

 ~~~ DivineSeeders: Assaf Krintza and Nir Malbin ~~
"""

import time
from collections import deque

class Logger:
        
    def __init__(self, filePath, sched, writeInterval = 30):
        self.filePath = filePath
        self.sched = sched
        self.writeInterval = writeInterval
        self.logQueue = deque()
        self.__logWork()
        
    def append(self, type, msg):
        self.logQueue.append("[%s] %s: %s" % time.strftime("%H:%M:%S"), type , msg)
    
    def flush(self):
        self.write(len(self.logQueue))
    
    def write(self, count = 5):
        if (len(self.logQueue) == 0):
            return
        
        with open(self.csvFile, 'a') as file:
            writen = 0
            
            while (writen < count and len(self.logQueue) > 0):
                logMsg = self.logQueue.pop()
                file.write(logMsg)
                writen += 1
                
            file.flush()
            
    def __logWork(self):
        self.sched(self.__logWork, self.writeInterval)