
"""
Tests for `utils` routines.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from streamanalysis import utils
from numpy import sqrt, ones, allclose, isclose, zeros
from datetime import datetime

class TestUtils(object):

    def setup(self):
        #prepare unit test. Load data etc
        print("setting up " + __name__)

    def test_vectoroperations(self):
        vector = ones(2)/sqrt(2)
        v, angle = utils.euclid2polar(vector)
        assert allclose(utils.polar2euclid(v, angle), vector)
        assert isclose(utils.get_norm(vector), 1)
        
    def teardown(self):
        #tidy up
        print("tearing down " + __name__)
        pass

if __name__ == '__main__':
    pytest.main()