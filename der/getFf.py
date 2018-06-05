import numpy as np

from slopeUtils import nWall


def getFf(q, u, nv, mapCons, μ, ForceAll):
    rv = np.zeros(2 * nv)
    for c in range(nv):
        if (not mapCons[2 * c]) and mapCons[2 * c + 1]:
            localU = u[2 * c : 2 * c + 2]
            parallelU = localU - np.dot(localU, nWall(q[2 * c])) * nWall(q[2 * c]).T
            uNorm = np.linalg.norm(parallelU)
            if uNorm == 0:
                continue
            normalForce = np.dot(ForceAll[2 * c : 2 * c + 2], nWall(q[2 * c]))
            if normalForce <= 0:
                continue
            rv[2 * c : 2 * c + 2] = - (parallelU / uNorm) * μ * normalForce
    return rv
