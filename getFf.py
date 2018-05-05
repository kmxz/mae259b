# Computing forces and Jacobian of friction
import numpy as np


def getFf(newQ, oldQ, nv, dt, dofHelper, coeff):

    Ff = np.zeros(2 * nv)
    Jf = np.zeros((2 * nv, 2 * nv))

    for c in dofHelper._constrained:
        assert c % 2 == 1  # assume it must be a y-direction dof
        vx = (newQ[c - 1] - oldQ[c - 1]) / dt
        Ff[c - 1] = - coeff * vx
        Jf[c - 1, c - 1] = - coeff / dt

    return Ff, Jf