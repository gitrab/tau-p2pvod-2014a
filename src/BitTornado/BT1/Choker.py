# Written by Bram Cohen
# see LICENSE.txt for license information

from random import randrange, shuffle
from BitTornado.clock import clock
from BitTornado.Logger import Logger
try:
    True
except:
    True = 1
    False = 0

class Choker:
    def __init__(self, config, schedule, picker, done = lambda: False):
        self.config = config
        self.round_robin_period = config['round_robin_period']
        self.schedule = schedule
        self.picker = picker
        self.connections = []
        self.last_preferred = 0
        self.last_round_robin = clock()
        self.done = done
        self.super_seed = False
        self.paused = False
        schedule(self._round_robin, 5)
        self.passedEndOfMovieFlag = False

    def set_round_robin_period(self, x):
        self.round_robin_period = x

    def _round_robin(self):
        self.schedule(self._round_robin, 5)
        if self.super_seed:
            cons = range(len(self.connections))
            to_close = []
            count = self.config['min_uploads']-self.last_preferred
            if count > 0:   # optimization
                shuffle(cons)
            for c in cons:
                i = self.picker.next_have(self.connections[c], count > 0)
                if i is None:
                    continue
                if i < 0:
                    to_close.append(self.connections[c])
                    continue
                self.connections[c].send_have(i)
                count -= 1
            for c in to_close:
                c.close()
        if self.last_round_robin + self.round_robin_period < clock():
            self.last_round_robin = clock()
            for i in xrange(1, len(self.connections)):
                c = self.connections[i]
                u = c.get_upload()
                if u.is_choked() and u.is_interested():
                    self.connections = self.connections[i:] + self.connections[:i]
                    break
        self._rechoke()
    
    #### P2PVODEX start ####
    def _finishedViewingMovie(self):
        if self.picker.getViewingPoint() >= self.picker.numpieces:
            return True
        return False
    #### P2PVODEX end ####
    
    def _rechoke(self, isVODPreferred = False):
        self._finishedViewingMovie()
        preferred = []
        maxuploads = self.config['max_uploads']
        if self.paused:
            for c in self.connections:
                c.get_upload().choke()
            return
        if maxuploads > 1:
            for c in self.connections:
                
                u = c.get_upload()

#HILLEL:
                d = c.get_download()
                if (d.get_rate() != u.get_rate()) and (u.get_rate()>(d.get_rate()/4)):
                    u.choke()
#-------
                if not u.is_interested():
                    continue
                if self.done():
                    r = u.get_rate()

                else:
                    d = c.get_download()
                    r = d.get_rate()
                    if r < 1000 or d.is_snubbed():
                        continue
                #### P2PVODEX start ####
                if self._finishedViewingMovie() and not self.passedEndOfMovieFlag:
                    Logger.getLogger().append("CHOKER","Movie finish point viewing point - %d , total pieces - %d" % (self.picker.getViewingPoint() , self.picker.numpieces))
                    self.passedEndOfMovieFlag = True
                    
                if isVODPreferred or self._finishedViewingMovie():
                    conncetionIndex = 2
                    preferred.append((int(not u.connection.isVODPeer()), -r ,c))
                else:
                    conncetionIndex = 1
                    preferred.append((-r ,c))
                
            self.last_preferred = len(preferred)
            preferred.sort()
            del preferred[maxuploads-1:]
            preferred = [x[conncetionIndex] for x in preferred]
            if len(preferred) > 0:
                Logger.getLogger().append("CHOKER","Top of preferred list is - %s" % preferred[0].get_id())
        count = len(preferred)
        hit = False
        to_unchoke = []
        for c in self.connections:
            u = c.get_upload()
            if c in preferred:
                to_unchoke.append(u)
            else:
                if count < maxuploads or not hit:
                    to_unchoke.append(u)
                    if u.is_interested():
                        count += 1
                        hit = True
                else:
                    u.choke()
        for u in to_unchoke:
            Logger.getLogger().append("CHOKER","Unchoking - %s" % u.connection.get_id())
            u.unchoke()

    def connection_made(self, connection, p = None):
        if p is None:
            p = randrange(-2, len(self.connections) + 1)
        self.connections.insert(max(p, 0), connection)
        self._rechoke()

    def connection_lost(self, connection):
        self.connections.remove(connection)
        self.picker.lost_peer(connection)
        if connection.get_upload().is_interested() and not connection.get_upload().is_choked():
            self._rechoke()

    def interested(self, connection):
        if not connection.get_upload().is_choked():
            self._rechoke()

    def not_interested(self, connection):
        if not connection.get_upload().is_choked():
            self._rechoke()

    def set_super_seed(self):
        while self.connections:             # close all connections
            self.connections[0].close()
        self.picker.set_superseed()
        self.super_seed = True

    def pause(self, flag):
        self.paused = flag
        self._rechoke()
