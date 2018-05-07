# Computing forces and Jacobian of friction
from math import exp
import numpy as np

P = 5


def sign(x):
    return 2 / (1 + exp(-P * x)) - 1


def getFf(u, nv, dofHelper, reactionForces, coeff):
    Ff = np.zeros(2 * nv)
    Jf = np.zeros((2 * nv, 2 * nv))

    for c in dofHelper._constrained:
        assert c % 2 == 1  # assume it must be a y-direction dof
        rF = reactionForces[c]
        if rF <= 0:
            continue
        v = u[c - 1]
        Ff[c - 1] = - coeff * sign(v) * rF

    return Ff, Jf
