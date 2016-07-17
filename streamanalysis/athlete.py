#! /usr/bin/env python

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals
from numpy import zeros, pi, sqrt, array
from numpy.random.mtrand import RandomState
from collections import namedtuple as nt
from streamanalysis.utils import get_norm, euclid2polar, polar2euclid

AthleteSpec = nt('athlete', ['pos', 'vel'])

class Athlete(object):
    
    def __init__(self, limits = array([100, 100]), pos0 = None, vel0 = None,
                 amax = 4.0, vmax = 9.0, acc_freq = .2, dec_a = .02,
                 seed = None, keepdata = False):
        """
        Simulated athlete. Returns a AthleteSpec instance on call containing
        current position, velocity, and acceleration.
        
        :param limits (optional): athlete moves between 0 and limits[0] for
        x-coordinate and 0 and limits[1] for y-coordinate, where limits are
        given in meters; default: [100, 100]
        :param pos0 (optional): array of initial positions (x and y);
        default: half-way between 0 and limits for x and y
        :param vel0 (optional): array of initial velocities (x and y);
        default: [0,0]
        :param amax (optional): maximum acceleration of athlete in m/s2;
        default: 4
        :param vmax (optional): maximum velocity of athelte in m/s; default: 9
        :param acc_freq (optional): frequency of additional acceleration input
        in Hz; default: 0.2
        :param dec_a (optional): magnitude of default deceleration in m/s2;
        default: 0.01
        :param seed (optional): random seed; default: None
        :param keepData (optional): Flag for storing the history of the
        athlete in self.data; default: False
        """
        self.limits = limits
        if pos0 is None:
            pos0 = limits * .5
        self.pos0 = pos0
        if vel0 is None:
            vel0 = zeros(2)
        self.vel0 = vel0
        self.amax = amax
        self.vmax = vmax
        self.acc_freq = acc_freq
        self.dec_a = dec_a
        self.rs = RandomState(seed)
        self.keepdata = keepdata
        self.reset()
            
    def __call__(self, time):
        """
        Return AthleteSpec instance containing position, velocity, and
        acceleration at the input time
        :param time: datetime instance as input time
        :returns data: AthleteSpec instance containing position, velocity, and
        acceleration
        """
        # reset velocity to zero if player bumped into boundaries
        # TODO: this creates an abrupt change in velocity/acceleration
        # which could be improved with a softer deceleration close to the
        # boundaries
        if self.reset_acc:
            self.acc = zeros(2)
            self.reset_acc = False
        if self.reset_vel:
            self.vel = zeros(2)
            self.reset_vel = False
        if self.time is None:
            # if self.time is None, the athlete didn't start moving yet
            # and returns the initial values
            self.time = time
            athlete = AthleteSpec(self.pos, self.vel)
        else:
            # calculate the time increment dt in seconds by comparing the 
            # input time to the time of the last call stored in self.time
            dt = (time - self.time).total_seconds()
            # update time in self.time
            self.time = time
            # draw random number and decide to accelerate or decelerate
            # according to self.acc_freq
            r = self.rs.rand()
            rt = self.acc_freq * dt
            if r > rt:
                # update acceleration of athlete according to self.dec_a
                self.decelerate(dt)
            else:
                # recycle r to represent a random value between 0 and 2 pi
                # this is the angle of the acceleration
                angle = (2 * pi / rt) * r
                # draw random magnitude of acceleration from a linear
                # distribution between 0 and amax
                a = (1.0 - sqrt(self.rs.rand())) * self.amax
                # transform polar coordinates of acceleration into x and y
                # component
                self.acc = polar2euclid(a, angle)
            # update position and velocity of athlete
            self.update_velocity(dt) 
            self.update_position(dt)
            # create AthleteSpec instance containing the athlete data
            athlete = AthleteSpec(pos = self.pos, 
                                  vel = self.vel)
        if self.keepdata:
            # optionally update the data list to keep track of the athlete
            self.data.append(athlete)
        return athlete

    def reset(self):
        """
        Reset athlete to initial conditions.
        """
        self.pos = self.pos0[:]
        self.vel = self.vel0[:]
        self.acc = zeros(2)
        self.time = None
        self.data = []
        self.reset_acc = False
        self.reset_vel = False
        
    def decelerate(self, dt):
        """
        Updates acceleration of athlete to account for deceleration by the
        default magnitude given in self.dec_a.
        :param dt: time increment for deceleration
        """
        # calculate total velocity
        v_ = get_norm(self.vel)
        if v_ > self.dec_a * dt:
            # decelerate if velocity is large
            da_vec = (self.dec_a / v_) * self.vel
            self.acc -= da_vec
        else:
            # stop player if velocity is small
            self.acc = -self.vel / dt
    
    def update_velocity(self, dt):
        """
        Updates velocity of the athlete.
        
        :param dt: time increment for update
        :returns reset_acc: acceleration to set after update, e.g. if
        athlete reaches vel limit
        """
        # increment velocity
        self.vel += self.acc * dt
        vel_abs = get_norm(self.vel)
        # check if velocity is consistent with maximal velocity
        # and correct it otherwise
        if vel_abs > self.vmax:
            self.vel *= (self.vmax / vel_abs)
            self.reset_acc = True

    def update_position(self, dt):
        """
        Updates position of the athlete.
        
        :param dt: time increment for update
        :returns reset_vel: flag for reseting the velocity
        to zero in case the athlete bumped into the limits
        """
        # increment position
        oldpos = self.pos[:]
        self.pos = oldpos + self.vel * dt
        # check if position is consistent with boundaries
        # and correct it otherwise
        if any(self.pos < 0) or any(self.pos > self.limits):
            # change angle of acceleration to avoid long waiting
            # at the boundaries
            a, angle = euclid2polar(self.acc)
            self.acc = polar2euclid(a, angle + .5 * pi)
            self.reset_vel = True
        idx = self.pos < 0
        self.pos[idx] = 0.0
        idx = self.pos > self.limits
        self.pos[idx] = self.limits[idx]
        # update velocity after correcting the positions
        self.vel = (self.pos - oldpos) / dt
        