
"""
Tests for `athlete` module.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from streamanalysis import athlete
from numpy import sqrt, ones, allclose, isclose, zeros
from datetime import datetime

class TestAthlete(object):

    def setup(self):
        #prepare unit test. Load data etc
        print("setting up " + __name__)
        self.athlete = athlete.Athlete()
        
    def test_athlete(self):
        assert self.athlete.time is None
        assert allclose(self.athlete.pos, self.athlete.pos0)
        assert allclose(self.athlete.vel, self.athlete.vel0)
        assert allclose(self.athlete.acc, zeros(2))
        time = datetime.now()
        data = self.athlete(time)
        assert self.athlete.time is time
        assert allclose(data.pos, self.athlete.pos0)
        assert allclose(data.vel, self.athlete.vel0)

    def teardown(self):
        #tidy up
        print("tearing down " + __name__)
        pass

if __name__ == '__main__':
    pytest.main()