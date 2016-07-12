
"""
Tests for `analyser` module.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from streamanalysis import analyser
from Queue import Queue
from streamanalysis.sensor import MeasurementSpec
from numpy import ones, zeros, allclose, isclose
from datetime import datetime
from time import sleep

class TestAthlete(object):

    def setup(self):
        #prepare unit test. Load data etc
        print("setting up " + __name__)
        self.q = Queue()
        self.analyser = analyser.Analyser(self.q)
        self.date = datetime.now()
        self.m = MeasurementSpec('test', self.analyser.pos0, self.date)
        self.r = analyser.ResultSpec(self.m.coords, None, zeros(2), None, 0.0,
                                     True, self.date)
        self.q.put(self.m)
        
    def test_is_stationary(self):
        vel = zeros(2)
        vel_err = ones(2)
        assert self.analyser.is_stationary(vel, vel_err)
        
    def test_run(self):
        self.analyser.start()
        sleep(2)
        assert not self.analyser.isAlive()
        assert self.analyser.data['test'] == self.m
        res = self.analyser.sensors['test']
        assert len(res) == 1
        assert allclose(self.r.pos, res[0].pos)
        assert allclose(self.r.vel, res[0].vel)
        assert isclose(self.r.dist, res[0].dist)
        assert self.r.stationary == res[0].stationary
        assert self.r.time == self.date

    def teardown(self):
        #tidy up
        print("tearing down " + __name__)
        pass

if __name__ == '__main__':
    pytest.main()