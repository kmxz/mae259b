from math import pi
import numpy as np

from cliUtils import cliRun
from dofHelper import DofHelper
from getFb import getFb
from getFs import getFs


def runDER():
    # number of vertices
    nv = 20

    # time step
    dt = 1.5e-2

    # rod Length
    RodLength = 0.20

    # Density
    rho = 1000.0

    # Cross-sectional radius of rod
    r0 = 5e-3

    # Young's modulus
    Y = 1e6

    # gravity
    g = [0.0, -9.81]

    # Tolerance on force function. This is multiplied by ScaleSolver so that we do not have to update it based on edge length and time step size
    tol = 1e-7

    # Maximum number of iterations in Newton Solver
    maximum_iter = 100

    # Total simulation time (it exits after t=totalTime)
    totalTime = 2.5

    # Utility quantities
    ne = nv - 1
    EI = Y * pi * r0 ** 4 / 4
    EA = Y * pi * r0 ** 2
    dm = pi * r0 ** 2 * RodLength * rho / ne  # mass per node

    nodes = np.zeros((nv, 2))

    for c in range(nv):
        nodes[c, 0] = c * RodLength / ne

    ScaleSolver = dm * np.linalg.norm(g)  # i don't know why. maybe just take it as granted

    # mass
    m = np.full(2 * nv, dm)
    m[0] /= 2
    m[1] /= 2
    m[2 * nv - 2] /= 2
    m[2 * nv - 1] /= 2

    # gravity
    garr = np.tile(g, nv)

    # Reference length and Voronoi length
    refLen = np.empty(ne)
    for c in range(ne):
        dx = nodes[c + 1] - nodes[c]
        refLen[c] = np.linalg.norm(dx)

    voronoiRefLen = np.empty(nv)
    voronoiRefLen[0] = 0.5 * refLen[0]
    for c in range(1, nv - 1):
        voronoiRefLen[c] = 0.5 * (refLen[c - 1] + refLen[c])
    voronoiRefLen[nv - 1] = 0.5 * refLen[nv - 2]

    # Initial
    q0 = np.zeros(2 * nv)
    for c in range(nv):
        q0[2 * c] = nodes[c, 0]  # initial x-coord
        q0[2 * c + 1] = nodes[c, 1]  # initial y-coord

    # Constrained dofs
    dofHelper = DofHelper(len(q0))
    dofHelper.constraint(range(0, 4))

    u = np.zeros(2 * nv)

    def objfun(q0WithAdditionalConstraintsApplied):
        mUncons = dofHelper.unconstrained_v(m)
        mMat = np.diag(mUncons)

        qCurrentIterate = q0WithAdditionalConstraintsApplied.copy()
        qUncons = dofHelper.unconstrained_v(qCurrentIterate)
        # Newton-Raphson scheme
        iter = 0
        while True:
            # get forces
            Fb, Jb = getFb(qCurrentIterate, EI, nv, voronoiRefLen, 0)
            Fs, Js = getFs(qCurrentIterate, EA, nv, refLen)
            Fg = m * garr

            Forces = Fb + Fs + Fg

            # Equation of motion
            f = m * (qCurrentIterate - q0) / dt ** 2 - m * u / dt - Forces
            fUncons = dofHelper.unconstrained_v(f)

            # Manipulate the Jacobians
            Jelastic = Jb + Js
            Jelastic = dofHelper.unconstrained_m(Jelastic)
            J = mMat / dt ** 2 - Jelastic

            # Newton's update
            qUncons = qUncons - np.linalg.solve(J, fUncons)
            dofHelper.write_unconstrained_back(qCurrentIterate, qUncons)

            # Get the norm
            normfNew = np.linalg.norm(fUncons)

            # Update iteration number
            iter += 1
            print('Iter=%d, error=%f' % (iter - 1, normfNew))

            if normfNew < tol * ScaleSolver:
                break
            if iter > maximum_iter:
                raise Exception('Cannot converge')
        return qCurrentIterate

    # Time marching
    Nsteps = int(totalTime / dt)  # number of time steps

    ctime = 0

    outputData = [{'time': ctime, 'data': q0.tolist()}]

    for timeStep in range(Nsteps):
        print('t = %f' % ctime)

        qNew = objfun(q0)

        ctime += dt
        u = (qNew - q0) / dt

        # Update x0 and u
        q0 = qNew

        output = {'time': ctime, 'data': q0.tolist()}
        outputData.append(output)

    return {'meta': {'radius': r0, 'closed': False}, 'frames': outputData}


if __name__ == '__main__':
    cliRun(runDER)