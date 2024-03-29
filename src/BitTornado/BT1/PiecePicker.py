# Written by Bram Cohen
# see LICENSE.txt for license information

import time
import sys
import math
import random
from random import randrange, shuffle
from BitTornado.clock import clock
from BitTornado.StreamWatcher import StreamWatcher 
from BitTornado.Logger import Logger

try:
    True
except:
    True = 1
    False = 0

class PiecePicker:
    def __init__(self, numpieces,
                 rarest_first_cutoff = 1, rarest_first_priority_cutoff = 3,
                 priority_step = 20):
        self.rarest_first_cutoff = rarest_first_cutoff
        self.rarest_first_priority_cutoff = rarest_first_priority_cutoff + priority_step
        self.priority_step = priority_step
        self.cutoff = rarest_first_priority_cutoff
        self.numpieces = numpieces
        self.started = []
        self.totalcount = 0
        self.numhaves = [0] * numpieces
        self.priority = [1] * numpieces
        self.removed_partials = {}
        self.crosscount = [numpieces]
        self.crosscount2 = [numpieces]
        self.has = [0] * numpieces
        self.numgot = 0
        self.done = False
        self.seed_connections = {}
        self.past_ips = {}
        self.seed_time = None
        self.superseed = False
        self.seeds_connected = 0
        self._init_interests()
        #### P2PVODEX start ####
        self.streamWatcher = None
        self.connecter = None
        self.storagewrapper = None
        self.vod_seeds_connected = 0
        self.logger = Logger.getLogger()
        self.rate = sys.maxint
        #### P2PVODEX start ####
        
    def _init_interests(self):
        """
        Initializes the self.interests list. this is a list of list in the size of priority_step
        each inner list is in the size of self.numpieces
        The higher the a piece in the interests index, the better it's priority
        each piece could be in at most one priority (e.g if piece 274 is in priority 12 it can't be in any other priority)
        """
        self.interests = [[] for x in xrange(self.priority_step)]
        self.level_in_interests = [self.priority_step] * self.numpieces
        interests = range(self.numpieces)
        shuffle(interests)
        self.pos_in_interests = [0] * self.numpieces
        for i in xrange(self.numpieces):
            self.pos_in_interests[interests[i]] = i
        self.interests.append(interests)

    
    def got_have(self, piece):
        """
        Update that there is a peer that have this particular piece.
        """
        self.totalcount+=1
        numint = self.numhaves[piece]
        self.numhaves[piece] += 1
        self.crosscount[numint] -= 1
        if numint+1==len(self.crosscount):
            self.crosscount.append(0)
        self.crosscount[numint+1] += 1
        if not self.done:
            numintplus = numint+self.has[piece]
            self.crosscount2[numintplus] -= 1
            if numintplus+1 == len(self.crosscount2):
                self.crosscount2.append(0)
            self.crosscount2[numintplus+1] += 1
            numint = self.level_in_interests[piece]
            self.level_in_interests[piece] += 1
        if self.superseed:
            self.seed_got_haves[piece] += 1
            numint = self.level_in_interests[piece]
            self.level_in_interests[piece] += 1
        elif self.has[piece] or self.priority[piece] == -1:
            return
        if numint == len(self.interests) - 1:
            self.interests.append([])
        self._shift_over(piece, self.interests[numint], self.interests[numint + 1])

    def lost_have(self, piece):
        """
        Update that we no longer have a peer with that piece.
        """
        self.totalcount-=1
        #The number of peers that holds this piece
        numint = self.numhaves[piece]
        self.numhaves[piece] -= 1
        #???
        self.crosscount[numint] -= 1
        self.crosscount[numint-1] += 1
        if not self.done:
            numintplus = numint+self.has[piece]
            self.crosscount2[numintplus] -= 1
            self.crosscount2[numintplus-1] += 1
            numint = self.level_in_interests[piece]
            self.level_in_interests[piece] -= 1
        if self.superseed:
            numint = self.level_in_interests[piece]
            self.level_in_interests[piece] -= 1
        elif self.has[piece] or self.priority[piece] == -1:
            return
        self._shift_over(piece, self.interests[numint], self.interests[numint - 1])
    
  
    def _shift_over(self, piece, l1, l2):
        """
        Shifts piece from l1 to l2.
        l1 and l2 are two pieces lists, each represents different priority step in self.interests  
        """
        assert self.superseed or (not self.has[piece] and self.priority[piece] >= 0)
        parray = self.pos_in_interests
        p = parray[piece]
        assert l1[p] == piece
        q = l1[-1]
        l1[p] = q
        parray[q] = p
        del l1[-1]
        newp = randrange(len(l2)+1)
        if newp == len(l2):
            parray[piece] = len(l2)
            l2.append(piece)
        else:
            old = l2[newp]
            parray[old] = len(l2)
            l2.append(old)
            l2[newp] = piece
            parray[piece] = newp

     #### P2PVODEX start ####
    def got_seed(self, isVODSeed):
        self.seeds_connected += 1
        if isVODSeed:
            self.vod_seeds_connected += 1
        self.cutoff = max(self.rarest_first_priority_cutoff-self.seeds_connected,0)
     #### P2PVODEX end ####

    def became_seed(self, isVODSeed):
        self.got_seed(isVODSeed)
        self.totalcount -= self.numpieces
        self.numhaves = [i-1 for i in self.numhaves]
        if self.superseed or not self.done:
            self.level_in_interests = [i-1 for i in self.level_in_interests]
            if self.interests:
                del self.interests[0]
        del self.crosscount[0]
        if not self.done:
            del self.crosscount2[0]
    #### P2PVODEX start ####
    def lost_seed(self, isVODSeed):
        self.seeds_connected -= 1
        
        if isVODSeed:
            self.vod_seeds_connected -= 1
        
        self.cutoff = max(self.rarest_first_priority_cutoff-self.seeds_connected,0)
    #### P2PVODEX end ####

    def requested(self, piece):
        if piece not in self.started:
            self.started.append(piece)

    def _remove_from_interests(self, piece, keep_partial = False):
        l = self.interests[self.level_in_interests[piece]]
        p = self.pos_in_interests[piece]
        assert l[p] == piece
        q = l[-1]
        l[p] = q
        self.pos_in_interests[q] = p
        del l[-1]
        try:
            self.started.remove(piece)
            if keep_partial:
                self.removed_partials[piece] = 1
        except ValueError:
            pass

    def complete(self, piece):

        ###### GROUP VOD ######
        # assert not self.has[piece]
        if (self.has[piece]):
            return
        #######################

        self.has[piece] = 1
        self.numgot += 1
        if self.numgot == self.numpieces:
            self.done = True
            self.crosscount2 = self.crosscount
        else:
            numhaves = self.numhaves[piece]
            self.crosscount2[numhaves] -= 1
            if numhaves+1 == len(self.crosscount2):
                self.crosscount2.append(0)
            self.crosscount2[numhaves+1] += 1
        self._remove_from_interests(piece)


    #### P2PVODEX start ####
    
    def getNumOfVODPeers(self):
        """
        Returns the number of VOD peers in the current connections list
        """
        numOfVODPeers = 0
        
        for connection in self.connecter.connections.values():
            if connection.isVODPeer():
                numOfVODPeers += 1
                
        return numOfVODPeers
    
    def getPercentageOfVODPeers(self):
        """
        Returns the percentage of VOD peers in the current connections list
        """
        consNum = len(self.connecter.connections.values())
        if consNum == 0:
            return 0        
        
        return  self.getNumOfVODPeers() / float(consNum)
    
    def getPercentageOfNotSeedersVOD(self):
        """
        Returns the percentage of VOD peers in the current connections list that are not seeders
        """
        consNum = len(self.connecter.connections.values())
        if consNum == 0:
            return 0        
        
        return  (self.getNumOfVODPeers() - self.vod_seeds_connected) / float(consNum)
    
    def formatPiecesGot(self):
        formatted = "("
        vp = self.getViewingPoint()
        for i in range(self.numpieces):
            if vp == i:
                p = '*'
            elif self.storagewrapper.do_I_have(i):
                p = '+'
            elif i in self.started:
                p = '/'
            else:
                p = '-'
            formatted += p
        return formatted + ')'
    
    def formatPiecesGotWithWindows(self, window):
        if window == None or len(window) == 0:
            return self.formatPiecesGot()
        formatted = "("
        vp = self.getViewingPoint()
        
        t = int(time.time() - self.streamWatcher.startTime)
        prefetrch = int(((t - self.streamWatcher.delay  + self.streamWatcher.prefetch ) * \
                                self.streamWatcher.rate) / self.streamWatcher.toKbytes(self.streamWatcher.piece_size))
        
        windowStart = window[0]
        windowEnd = window[-1]
        
        for i in range(self.numpieces):
            
            p = ''
            
            if i == vp:
                p += '['
            if i == windowStart:
                p += '{'
        
            if self.storagewrapper.do_I_have(i):
                    p += '+'
            elif i in self.started:
                    p += '/'
            else:
                    p += '-'

            if i == windowEnd:
                p += '}'
            if i == prefetrch:
                p += ']'    
            
            formatted += p
            
        return formatted + ')'
    
    def updateCurrentRate(self, rate):
        if rate != 0:
            self.rate = rate / 1024.0
        else:
            rate = 0.0001
        #self.logger.append("PIECEPICKER","Current rate is - %d" % rate)
            
    def next(self, haves, wantfunc, complete_first = False, rate = sys.maxint):
        """
        return the index of the next piece to ask for
        haves - list of pieces we know peers have
        wantfunc - a function that return if we want that particular piece
        complete_first - should we complete pieces that we already started to take care of?
        """
        self.updateCurrentRate(rate)           
               
#         t = int(time.time() - self.streamWatcher.startTime)
#         if t <= self.streamWatcher.delay:
#             interval  =  int( ( ( self.streamWatcher.delay ) * self.streamWatcher.rate) / \
#                                    self.streamWatcher.toKbytes(self.streamWatcher.piece_size) )
#             return self.smartRarestFirst(haves, wantfunc, complete_first, range(0, interval))
       
        return self.dynamicWindowedRarestFirst(haves, wantfunc, complete_first)
        #return self.windowedSmartRarestFirst(haves, wantfunc, complete_first)
        #return self.hybridVODNext(haves, wantfunc, complete_first)
        #return self.lastYearnext(haves, wantfunc, complete_first)
       
    def lastYearnext(self,haves,wantfunc,complete_first = False):
        if (time.time()-self.streamWatcher.startTime < int(self.streamWatcher.delay) ):
            p=self.lastYearRandomRarest(haves, wantfunc)
        else:
            p = self.lastYearInOrder(haves, wantfunc)
        if (p==None):
            downloadRate = self.rate 
            if downloadRate > int(self.rate)*1.5:
                p=self.lastYearBetaRarest(haves, wantfunc)
            else:
                p=self.lastYearRandomRarest(haves, wantfunc)
        if (p==None):
            p=self.lastYearRandomRarest(haves, wantfunc)
        return p
         
    def lastYearGetInOrderInterval(self):
        alpha = self.getIntervalStart()
        if (alpha>0):
            alpha+=1
        beta = alpha + int(0.1*self.numpieces)
        if beta>self.numpieces-1:
            beta  =  self.numpieces-1
        if alpha>beta-1:
            alpha  = beta-1
        return [alpha,beta]
    
    def lastYearInOrder(self, haves, wantfunc):
        interval = self.lastYearGetInOrderInterval()
        for j in xrange(interval[0],interval[1]):
                if  haves[j] and wantfunc(j):
                    return j 
        
        return None

    def lastYearRandomRarest(self, haves, wantfunc):
        best = None
        bestnum = 2 ** 30
        for i in self.started:
            if haves[i] and wantfunc(i):
                if self.level_in_interests[i] < bestnum:
                    best = i
                    bestnum = self.level_in_interests[i]
        if best is not None:
            return best
        if haves.complete():
            r = [ (0, min(bestnum,len(self.interests))) ]
        elif len(self.interests) > self.cutoff:
            r = [ (self.cutoff, min(bestnum,len(self.interests))) ,(0, self.cutoff) ]
        else:
            r = [ (0, min(bestnum,len(self.interests))) ]
        for lo,hi in r:
            for i in xrange(lo,hi):
                for j in self.interests[i]:
                    if haves[j] and wantfunc(j):
                        return j
        if best is not None:
            return best
        return None
    
    def lastYearBetaRarest(self, haves, wantfunc):
        best = None
        bestnum = 2 ** 30
        for i in self.started:
            if haves[i] and wantfunc(i):
                if self.level_in_interests[i] < bestnum:
                    best = i
                    bestnum = self.level_in_interests[i]
        if best is not None:
            return best
        if haves.complete():
            r = [ (0, min(bestnum,len(self.interests))) ]
        elif len(self.interests) > self.cutoff:
            r = [ (self.cutoff, min(bestnum,len(self.interests))) ,(0, self.cutoff) ]
        else:
            r = [ (0, min(bestnum,len(self.interests))) ]
        for lo,hi in r:
            for i in xrange(lo,hi):
                betaList = list(self.interests[i])
                betaList.sort()
                if  len(betaList):
                    p = self.lastYearBetaRandom(haves, wantfunc , betaList )
                    if p is not None:
                        return p 
        if best is not None:
            return best
        return None
    
    def lastYearBetaRandom(self, haves, wantfunc , list ):   
            beta_pieces_list = []                 
            for j in list:
                if haves[j] and wantfunc(j):
                    beta_pieces_list.append(j)
            
            if len(beta_pieces_list)==0:
                return None
            
            bvRand = random.betavariate(0.4,4.0)            
            if bvRand == 1:
                i =  len(beta_pieces_list) - 1
            else:
                i =  int(math.floor( bvRand * len(beta_pieces_list)))         
            return beta_pieces_list[i]
        
    def dynamicWindowedRarestFirst(self, haves, wantfunc, complete_first):
        
        dfs = max(float(self.streamWatcher.total_dfs) / self.streamWatcher.total, 0.01)
        vods = self.getPercentageOfNotSeedersVOD()
        #interval = (vods ** 1.6) / (0 * (dfs - 1) + 1)
        interval = (0.82 * vods - 0.08) * ((1 - dfs) ** 0.1) 
        interval = min(max(interval, 0.00001), 1)
        interval = int(math.ceil(interval * self.numpieces))
        
        self.logger.append("PIECEPICKER", "window interval %.2f,%.2f => %d" % (dfs, vods, interval))
        
        start = self.getIntervalStart()
        p = self.intervalRarestFirst(haves, wantfunc, complete_first, start, interval)
        
        if p != None:
            window = range(start, start + interval)
            self.logger.append("PIECEPICKER", "%s [%d,%d]" % (self.formatPiecesGotWithWindows(window), start, start + interval))
            
        if p == None:
            p = self.smartRarestFirst(haves, wantfunc, complete_first)
        
        if p == None:
            p = self.rarestFirst(haves, wantfunc, complete_first)
        
        return p
        
    def intervalRarestFirst(self, haves, wantfunc, complete_first, start, interval):
        calcInterval = lambda i: \
                math.floor((((i - start) / interval) + 1))
        
        cutoff = self.numgot < self.rarest_first_cutoff
        complete_first = (complete_first or cutoff) and not haves.complete()
        best = None
        bestInterval = 2 ** 30
        bestnum = 2 ** 30
        #self.started represents all of the pieces that have been called already
        for i in self.started:
            if haves[i] and wantfunc(i) and i >= start:
                currInterval = calcInterval(i)
                if currInterval < bestInterval or \
                    (currInterval == bestInterval and self.level_in_interests[i] < bestnum):
                    #the best one to get next
                    best = i
                    bestInterval = calcInterval(i)
                    #the priority of this "best" piece
                    bestnum = self.level_in_interests[i]
        if best is not None:
            if complete_first or (cutoff and len(self.interests) > self.cutoff):
                return best
        if haves.complete():
            r = [ (0, min(bestnum,len(self.interests))) ]
        elif cutoff and len(self.interests) > self.cutoff:
            r = [ (self.cutoff, min(bestnum,len(self.interests))),
                      (0, self.cutoff) ]
        else:
            r = [ (0, min(bestnum,len(self.interests))) ]
        
        p = None
        pInterval = 2 ** 30
        for lo,hi in r:
            for i in xrange(lo,hi):
                for j in self.interests[i]:
                    currInterval = calcInterval(j)
                    if haves[j] and wantfunc(j) and j >= start and currInterval < pInterval:
                        p = j
                        pInterval = currInterval
        if p is not None:
            return p
        if best is not None:
            return best
        return None
        
    def windowedSmartRarestFirst(self, haves, wantfunc, complete_first):
        intervalStart = self.getIntervalStart()
        intervalEnd = intervalStart + int(self.numpieces * 0.33)
        
        if intervalEnd >= self.numpieces:
            intervalEnd = self.numpieces
            
        window = range(intervalStart, intervalEnd)
        
        self.logger.append("PIECEPICKER", self.formatPiecesGotWithWindows(window))
        
        #if len(window) > 0:
        #    self.logger.append("PIECEPICKER","Window is [%d, %d]" % (window[0], window[-1]))
        if len(window) == 0:
            window = None
        
        p = self.smartRarestFirst(haves, wantfunc, complete_first, window)
        
        if p == None:
            p = self.smartRarestFirst(haves, wantfunc, complete_first)
        
        #if p != None:
        #    self.logger.append("PIECEPICKER","piece chosen is %d" % (p))
        
        return p
    
    def hybridVODNext(self, haves, wantfunc, complete_first):
         inOrderWindow = int(max(0, 0.75 - 4 * self.getPercentageOfNotSeedersVOD()) * len(haves))
         # self.logger.append("PIECEPICKER","Window Size %d" % inOrderWindow)
         return self.hybridNext(inOrderWindow, haves, wantfunc, complete_first)
    
    def dynamicHybridNext(self, haves, wantfunc, complete_first):
        if (not hasattr(self, 'inOrderWindow')):
            self.inOrderWindow = int(max(0, 0.25 - 0.5 * self.getPercentageOfNotSeedersVOD()) * len(haves))
            self.prevDfs = self.streamWatcher.total_dfs*1000 / self.streamWatcher.total
            self.lastWindowUpdate = time.time()
        
        if ((time.time() - self.lastWindowUpdate) > self.streamWatcher.prefetchT + 5):
            currDfs = self.streamWatcher.total_dfs*1000 / self.streamWatcher.total
            dfsDiff = currDfs - self.prevDfs
            
            self.prevDfs = currDfs
            self.lastWindowUpdate = time.time()
            
            if (dfsDiff >= 10):
                self.inOrderWindow = min(len(haves), self.inOrderWindow + 1)
            elif (dfsDiff < 1):
                self.inOrderWindow = max(0, self.inOrderWindow - 1)
            
            Logger.getLogger().append("WINDOW_UPDATE", "%d %d %d" % (currDfs, dfsDiff,self.inOrderWindow))
                
        return (self.hybridNext(self.inOrderWindow, haves, wantfunc, complete_first))
        
    
    def hybridNext(self, inOrderWindow, haves, wantfunc, complete_first = False):
        """
        An hybrid method to pick pieces including smartInOrder and rarestFirst.
            The method pick pieces by smartInOrder within a specific pre-defined window and
            after goes to pick by rarestFirst.
        """
        if ((inOrderWindow > 0) and 
            (self.getCompletedSequence(self.getIntervalStart(), inOrderWindow) <= inOrderWindow)):
            p = self.smartInOrder(haves, wantfunc)
            alg = "smartInOrder"
        elif (self.getIntervalStart() < len(haves)):
            p = self.smartRarestFirst(haves, wantfunc, complete_first)
            alg = "smartRarestFirst"
        else:
            p = self.rarestFirst(haves, wantfunc, complete_first)
            alg = "RarestFirst"
        
        if p == None:
             self.logger.append("PIECEPICKER","Used %s. Piece NONE" % alg)
        else:
             self.logger.append("PIECEPICKER","Used %s. Piece %d" % (alg, p))
        
        return p
    
    def getCompletedSequence(self, start = 0, max = -1):
        if (max == -1) or (start + max > self.numpieces):
            max = self.numpieces - start
        
        seq = 0
        
        
        
        while (seq < max) and self.storagewrapper.do_I_have(start + seq):
            seq += 1

        return seq
        
    def getViewingPoint(self):
         t = int(time.time() - self.streamWatcher.startTime)
         return int(((t - self.streamWatcher.delay) * self.streamWatcher.rate) / self.streamWatcher.toKbytes(self.streamWatcher.piece_size))
    
    def getIntervalStart(self):
        """
        Return the piece index of the start of the interval of wanted pieces.
        i.e Viewing Point + Prefetch Time
        """
        t = int(time.time() - self.streamWatcher.startTime)
        if t > self.streamWatcher.delay:
            intervalStart  =  int(((t - self.streamWatcher.delay  + self.streamWatcher.prefetch ) * \
                                    self.streamWatcher.rate) / self.streamWatcher.toKbytes(self.streamWatcher.piece_size))
            
            #Safe distance to ensure the downloaded piece could actually be watched on time
            #safeDistance = int( math.ceil( math.sqrt (self.streamWatcher.rate / float(self.rate) ) ) ) 
            safeDistance = 0
                
            #self.logger.append("PIECEPICKER","Current safe distance is: %d" % safeDistance)
        else:
            intervalStart = 0
            safeDistance = 0
        
        if intervalStart + safeDistance < self.numpieces:
            return intervalStart + safeDistance 
        
        return intervalStart
    
    def smartInOrder(self, haves, wantfunc):
        """
        An In Order implementation which respects the playing point and prefetch time and
        only ask for pieces after that
        """
        intervalStart = self.getIntervalStart()
        for i in range(intervalStart, self.numpieces):
            if haves[i] and wantfunc(i):
                return i
        
        return None
            
    def SimpleInOrder(self, haves, wantfunc):
        """
        A simple In Order implementation used for the first Milestone
        """      
        for i in range(self.numpieces):
            if haves[i] and wantfunc(i):
                return i
        
        return None
        
    def smartRarestFirst(self, haves, wantfunc, complete_first = False, window = None):
        
        if window == None:
            self.logger.append("PIECEPICKER", self.formatPiecesGot())
            
            newWantFunc = lambda i: \
                ((i >= self.getIntervalStart()) and wantfunc(i))
        else:
            #self.logger.append("PIECEPICKER", "%s [%d,%d]" % (self.formatPiecesGotWithWindows(window), window[0], window[-1]))
            
            newWantFunc = lambda i: \
                ((i in window) and wantfunc(i))
        return (self.rarestFirst(haves, newWantFunc, complete_first))
    
    def rarestFirst(self, haves, wantfunc, complete_first = False):
        cutoff = self.numgot < self.rarest_first_cutoff
        complete_first = (complete_first or cutoff) and not haves.complete()
        best = None
        bestnum = 2 ** 30
        #self.started represents all of the pieces that have been called already
        for i in self.started:
            if haves[i] and wantfunc(i):
                if self.level_in_interests[i] < bestnum:
                    #the best one to get next
                    best = i
                    #the priority of this "best" piece
                    bestnum = self.level_in_interests[i]
        if best is not None:
            if complete_first or (cutoff and len(self.interests) > self.cutoff):
                return best
        if haves.complete():
            r = [ (0, min(bestnum,len(self.interests))) ]
        elif cutoff and len(self.interests) > self.cutoff:
            r = [ (self.cutoff, min(bestnum,len(self.interests))),
                      (0, self.cutoff) ]
        else:
            r = [ (0, min(bestnum,len(self.interests))) ]
        for lo,hi in r:
            for i in xrange(lo,hi):
                for j in self.interests[i]:
                    if haves[j] and wantfunc(j):
                        return j
        if best is not None:
            return best
        return None

    #### P2PVODEX end  ####
        
    def am_I_complete(self):
        return self.done
    
    def bump(self, piece):
        l = self.interests[self.level_in_interests[piece]]
        pos = self.pos_in_interests[piece]
        del l[pos]
        l.append(piece)
        for i in range(pos,len(l)):
            self.pos_in_interests[l[i]] = i
        try:
            self.started.remove(piece)
        except:
            pass

    def set_priority(self, piece, p):
        if self.superseed:
            return False    # don't muck with this if you're a superseed
        oldp = self.priority[piece]
        if oldp == p:
            return False
        self.priority[piece] = p
        if p == -1:
            # when setting priority -1,
            # make sure to cancel any downloads for this piece
            if not self.has[piece]:
                self._remove_from_interests(piece, True)
            return True
        if oldp == -1:
            level = self.numhaves[piece] + (self.priority_step * p)
            self.level_in_interests[piece] = level
            if self.has[piece]:
                return True
            while len(self.interests) < level+1:
                self.interests.append([])
            l2 = self.interests[level]
            parray = self.pos_in_interests
            newp = randrange(len(l2)+1)
            if newp == len(l2):
                parray[piece] = len(l2)
                l2.append(piece)
            else:
                old = l2[newp]
                parray[old] = len(l2)
                l2.append(old)
                l2[newp] = piece
                parray[piece] = newp
            if self.removed_partials.has_key(piece):
                del self.removed_partials[piece]
                self.started.append(piece)
            # now go to downloader and try requesting more
            return True
        numint = self.level_in_interests[piece]
        newint = numint + ((p - oldp) * self.priority_step)
        self.level_in_interests[piece] = newint
        if self.has[piece]:
            return False
        while len(self.interests) < newint+1:
            self.interests.append([])
        self._shift_over(piece, self.interests[numint], self.interests[newint])
        return False

    def is_blocked(self, piece):
        return self.priority[piece] < 0


    def set_superseed(self):
        assert self.done
        self.superseed = True
        self.seed_got_haves = [0] * self.numpieces
        self._init_interests()  # assume everyone is disconnected

    def next_have(self, connection, looser_upload):
        if self.seed_time is None:
            self.seed_time = clock()
            return None
        if clock() < self.seed_time+10:  # wait 10 seconds after seeing the first peers
            return None                 # to give time to grab have lists
        if not connection.upload.super_seeding:
            return None
        olddl = self.seed_connections.get(connection)
        if olddl is None:
            ip = connection.get_ip()
            olddl = self.past_ips.get(ip)
            if olddl is not None:                               # peer reconnected
                self.seed_connections[connection] = olddl
        if olddl is not None:
            if looser_upload:
                num = 1     # send a new have even if it hasn't spread that piece elsewhere
            else:
                num = 2
            if self.seed_got_haves[olddl] < num:
                return None
            if not connection.upload.was_ever_interested:   # it never downloaded it?
                connection.upload.skipped_count += 1
                if connection.upload.skipped_count >= 3:    # probably another stealthed seed
                    return -1                               # signal to close it
        for tier in self.interests:
            for piece in tier:
                if not connection.download.have[piece]:
                    seedint = self.level_in_interests[piece]
                    self.level_in_interests[piece] += 1  # tweak it up one, so you don't duplicate effort
                    if seedint == len(self.interests) - 1:
                        self.interests.append([])
                    self._shift_over(piece,
                                self.interests[seedint], self.interests[seedint + 1])
                    self.seed_got_haves[piece] = 0       # reset this
                    self.seed_connections[connection] = piece
                    connection.upload.seed_have_list.append(piece)
                    return piece
        return -1       # something screwy; terminate connection

    def lost_peer(self, connection):
        olddl = self.seed_connections.get(connection)
        if olddl is None:
            return
        del self.seed_connections[connection]
        self.past_ips[connection.get_ip()] = olddl
        if self.seed_got_haves[olddl] == 1:
            self.seed_got_haves[olddl] = 0
