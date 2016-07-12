#! /usr/bin/env python

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

from numpy import array, cos, sin, arctan2, sqrt

def polar2euclid(a, angle):
    return array([a * cos(angle), a * sin(angle)])

def euclid2polar(vec):
    return get_norm(vec), arctan2(vec[1], vec[0])

def get_norm(vec):
    return sqrt((vec * vec).sum())