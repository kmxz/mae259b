import math
import numpy as np


# thetaNormal.m
thetaNormal = math.radians(75)


# slopeWall.m
def slopeWall(x):
    return math.tan(thetaNormal + math.pi / 2)


# nWall.m
def nWall(x):
    return np.array([[math.cos(thetaNormal)], [math.sin(thetaNormal)]])


# invMass.m
def invMass(x):
    n = nWall(x)
    return np.eye(2, 2) - n * n.T
