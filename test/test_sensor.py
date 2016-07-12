
"""
Tests for `sensor` module.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from streamanalysis import sensor
from streamanalysis.athlete import AthleteSpec
from numpy import zeros, allclose, array, any
from datetime import datetime
from Queue import Queue
from time import sleep

class TestSensor(object):

    def setup(self):
        #prepare unit test. Load data etc
        print("setting up " + __name__)
        p = zeros(2)
        # Mock athlete that doesn't move
        self.athlete = lambda t: AthleteSpec(p, p)

    def test_sensor(self):
        q = Queue()
        ID = 'test'
        # Test without noise
        test_sensor = sensor.Sensor(self.athlete, q, ID, noise = 0)
        test_sensor.start()
        sleep(.11)
        test_sensor.stop()
        data = []
        while not q.empty():
            e = q.get_nowait()
            data.append(e.coords)
        assert e.ID == ID
        assert len(data) == 3
        assert allclose(data, 0)
        # Test with noise
        test_sensor = sensor.Sensor(self.athlete, q, ID, noise = 1)
        test_sensor.start()
        sleep(.11)
        test_sensor.stop()
        data = []
        while not q.empty():
            e = q.get_nowait()
            data.append(e.coords)
        assert ~any(array(data) == 0)
            

    def teardown(self):
        #tidy up
        print("tearing down " + __name__)
        pass

if __name__ == '__main__':
    pytest.main()