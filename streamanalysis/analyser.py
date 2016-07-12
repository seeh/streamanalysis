#! /usr/bin/env python

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

from threading import Thread
from Queue import Empty
from numpy import sqrt, zeros, matrix, eye, diag, log

from streamanalysis.utils import get_norm

from collections import namedtuple as nt

ResultSpec = nt('result', ['pos', 'pos_err', 'vel', 'vel_err', 'dist',
                           'stationary', 'time'])
FilterSpec = nt('filter', ['X', 'P'])

POS_IDX = [0, 2]
VEL_IDX = [1, 3]

class Analyser(Thread):
    
    def __init__(self, queue, pos0 = [50.0, 50.0], vel0 = [0.0, 0.0],
                 noise = 0.3, dt0 = 1./20, acc_noise = 4.0, wait = 1.0):
        """
        Analysis thread for position data from sensors using a Kalman Filter.
        Stores results of the individual sensors in a dictionary at
        self.sensors.
        
        :param queue: queue from which the sensor data is processed
        :param pos0 (optional): list of initial positions for the Kalman
        Filter; default: [50, 50]
        :param vel0 (optional): list of initial velocities for the Kalman
        Filter; default: [0, 0]
        :param noise (optional): standard deviation of noise on observations
        :param dt0 (otpional): estimate for sampling rate (needed for initial
        Kalman filter step); default: 0.05
        :param acc_noise (optional): estimate for standard deviation in
        acceleration; default: 4.0
        :param wait (optional): time to wait for new elements in the queue
        before stopping (in seconds); default: 1 
        """
        super(Analyser, self).__init__()
        self.queue = queue
        self.wait = wait
        self.data = {}
        self.sensors = {}
        self.filter = {}
        self.pos0 = pos0
        self.vel0 = vel0
        self.dt0 = dt0
        self.acc_noise = acc_noise
        self.noise = noise
        self.stat_p = 0.95
        
    def run(self):
        """
        Run analysis thread
        """
        self.initialize_matrices()
        while True:
            # Try to get data from queue and break if we have to wait for more
            # than self.wait seconds
            try:
                data = self.queue.get(timeout = self.wait)
                self.analyse_data(data)
            except Empty:
                break

    def analyse_data(self, data):
        """
        Analyse the sensor data and append result to self.sensors
        
        :param data: MeasurementSpec instance
        """
        # get ID from sensor
        ID = data.ID
        # try to recover previous status for this ID
        # initialise otherwise
        try:
            # last result
            sensor = self.sensors[ID][-1]
            # state of Kalman Filter
            prev = self.filter[ID]
            # time increment to last measurement
            dt = (data.time - sensor.time).total_seconds()
        except KeyError:
            # Initialize empty list to which result will be appended
            self.sensors[ID] = []
            # Initialize Kalman Filter
            prev = self.initialize_filter()
            # Create initial value of sensor
            err = diag(prev.P.A)
            dt = self.dt0
            sensor = ResultSpec(pos = self.pos0,
                                pos_err = err[POS_IDX],
                                vel = self.vel0,
                                vel_err = err[VEL_IDX],
                                dist = 0.0,
                                stationary = True,
                                time = None)
        # Update Kalman Filter
        Filter = self.kalman_filter(data.coords, dt, prev)
        # Process Kalman Filter into ResultSpec instance
        res = self.get_new_state(Filter, sensor, data.time)
        # Update Filter, data, and append results
        self.filter[ID] = Filter
        self.data[ID] = data
        self.sensors[ID].append(res)

    def initialize_filter(self):
        """
        Initialize Kalman Filter. As implemented right now, it assumes
        perfect knowledge of initial values (could be generalized).
        
        :returns filter: FilterSpec instance
        """
        # Initial position assumes perfect knowledge at the moment
        P = matrix(zeros((4,4)))
        X = matrix([self.pos0[0], self.vel0[0],
                    self.pos0[1], self.vel0[1]]).T
        return FilterSpec(X = X, P = P)
    
    def initialize_matrices(self):
        """
        Initialize matrices that the Kalman Filter uses repeatedly.
        """
        self.H = matrix([[1,0,0,0],
                         [0,0,1,0]])
        self.R = matrix(eye(2) * (self.noise * self.noise))
        self.identity = matrix(eye(4))
        
    def kalman_filter(self, coords, dt, prev):
        """
        Update Kalman Filter. Algorithm adapted from:
        
        https://en.wikipedia.org/wiki/Kalman_filter#Example_application.2C_technical
        
        :param coords: Observed coordinates from the sensor
        :param dt: Time increment with respect to previous state of filter
        :param prev: previous state of filter
        :returns filter: FilterSpec instance
        """
        # Matrix that describes the update for position and velocity
        F = matrix([[1,dt,0,0],
                    [0, 1,0,0],
                    [0, 0,1,dt],
                    [0, 0,0,1]])
        # Matrix that describes uncertainty in the prediction due to
        # acceleration
        G = matrix([[dt*dt*.5,dt,0,0],[0,0,dt*dt*.5,dt]]).T
        Q = (self.acc_noise * self.acc_noise) * G * G.T
        # Vector of measurements
        m = matrix(coords).T
        # Prediction of measurement from previous state of the filter
        xk = F * prev.X
        # Prediction of error covariance
        Pk = (F * prev.P) * F.T + Q
        # Residual difference between prediction and observation
        yk = m - self.H * xk
        # Adaption of model and error according to residual
        Sk = self.H * (Pk * self.H.T) + self.R
        Kk = (Pk * self.H.T) * Sk.I
        X = xk + Kk * yk
        P = (self.identity - Kk * self.H) * Pk
        return FilterSpec(X = X, P = P)
    
    def get_new_state(self, Filter, sensor, time):
        """
        Process new filter state into ResultSpec instance
        
        :param Filter: state of Kalman Filter
        :param sensor: previous result
        :param time: time of new measurement
        :returns result: ResultSpec instance
        """
        # Get position, velocity and their errors from filter state
        X = Filter.X.A[:,0]
        err = diag(Filter.P.A)
        pos = X[POS_IDX]
        pos_err = sqrt(err[POS_IDX])
        vel = X[VEL_IDX]
        vel_err = sqrt(err[VEL_IDX])
        # Test if object is stationary (needed to minimize bias in distance
        # estimation for stationary objects)
        stat = self.is_stationary(vel, vel_err)
        # If object is not stationary, increment total distance
        if not stat:
            dist = sensor.dist + get_norm(pos-sensor.pos)
        else:
            dist = sensor.dist
        # Return result
        result = ResultSpec(pos = pos, pos_err = pos_err,
                            vel = vel, vel_err = vel_err,
                            dist = dist, stationary = stat,
                            time = time)
        return result
    
    def is_stationary(self, vel, vel_err):
        """
        Test if sensor is stationary using a hypothesis test which tests if
        the observed velocity is consistent with 0 within the estimated noise
        
        :param vel: estimated velocities
        :param vel_err: estimated error on velocities
        :returns: True if estimate is consistent with stationary, False else
        """
        dv = vel/vel_err
        chi_squared = (dv * dv).sum()
        return chi_squared < -2 * log(1-self.stat_p)
        