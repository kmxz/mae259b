import math
import numpy as np


# thetaNormal.m
def thetaNormal(x):
    return math.radians(75)


# slopeWall.m
def slopeWall(x):
    return math.tan(thetaNormal(x) + math.pi / 2)


# nWall.m
def nWall(x):
    return np.array([math.cos(thetaNormal(x)), math.sin(thetaNormal(x))])


# invMass.m
def invMass(x):
    n = nWall(x)
    return np.eye(2, 2) - n * np.array([n]).T
