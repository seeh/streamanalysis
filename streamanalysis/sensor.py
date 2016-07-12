#! /usr/bin/env python

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

from threading import Thread, Event
from datetime import datetime
from numpy.random.mtrand import RandomState
from collections import namedtuple as nt

MeasurementSpec = nt('measurement', ['ID', 'coords', 'time'])

class Sensor(Thread):
    
    def __init__(self, athlete, queue, ID, rate = 20,
                 noise = 0.3, verbose = False, seed = None):
        """
        Sensor class which gets position measurements from athlete, adds noise
        and collects them in a queue.
        
        :param athlete: object yielding position data when called
        :param queue: queue to which the measurements are added
        :param id: sensor ID
        :param rate (optional): sampling rate of sensor in Hz, default: 20
        :param noise (optional): standard deviation of noise on measurement in
        meter, default: 0.3
        :param verbose (optional): verbosity of sensor, default: False
        :param seed (optional): seed of noise generation, default: None 
        """
        super(Sensor, self).__init__()
        self.queue = queue
        self.ID = ID
        self.athlete = athlete
        self.rate = rate
        self.deltat = 1./self.rate
        self.noise = noise
        self.verbose = verbose
        self.rs = RandomState(seed)
        self.running = Event()
        
    def run(self):
        """
        Run sensor.
        """
        if self.verbose:
            print('Sensor %s started'%self.ID)
        # start time
        time = datetime.now()
        # number of measurements
        i = 0
        while not self.running.isSet():
            # get time of measurement
            t = datetime.now()
            # get data from athlete
            data = self.athlete(t)
            # add noise to position
            pos = data.pos + self.rs.randn(2) * self.noise
            # create MeasurementSpec instance containing ID, position,
            # and time of measurement
            measurement = MeasurementSpec(ID = self.ID, coords = pos,
                                          time = t)
            # add measurement to queue
            self.queue.put(measurement)
            # increment number of measurements
            i += 1
            # calculate time to wait to satisfy sampling rate
            timeout = i * self.deltat - (datetime.now()-time).total_seconds()
            self.running.wait(timeout)
        if self.verbose:
            print('Sensor %s stopped'%self.ID)

        
    def stop(self):
        """
        Stop sensor.
        """
        self.running.set()