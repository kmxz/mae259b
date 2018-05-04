from math import pi, sin, cos
from copy import deepcopy
import numpy as np

from cliUtils import cliRun
from dofHelper import DofHelper
from getFb import getFb
from getFp import getFp
from getFs import getFs


def runDER():
    # number of vertices
    nv = 24

    # max time step
    max_dt = 1e-2

    # min time step
    min_dt = 1e-4

    # limit du per step
    limit_du_per_step = 0.2

    # initial center of circle
    x0 = [0.0, 0.50]

    # inflation pressure (N/m)
    InflationPressure = 10.0

    # circle radius
    CircleRadius = 0.20

    # circumference length
    CircumferenceLength = 2 * pi * CircleRadius

    # Density
    rho = 500.0

    # Cross-sectional radius of rod
    r0 = 5e-3

    # Young's modulus
    Y = 5e6

    # gravity
    g = [0.0, -9.81]

    # Tolerance on force function. This is multiplied by ScaleSolver so that we do not have to update it based on edge length and time step size
    tol = 1e-7

    # Maximum number of iterations in Newton Solver
    maximum_iter = 100

    # Total simulation time (it exits after t=totalTime)
    totalTime = 1.5

    # Utility quantities
    EI = Y * pi * r0 ** 4 / 4
    EA = Y * pi * r0 ** 2
    dm = pi * r0 ** 2 * CircumferenceLength * rho / nv  # mass per node

    nodes = np.empty((nv, 2))

    for c in range(nv):
        nodes[c, 0] = x0[0] + CircleRadius * cos(c * 2 * pi / nv + pi / 2)
        nodes[c, 1] = x0[1] + CircleRadius * sin(c * 2 * pi / nv + pi / 2)

    ScaleSolver = dm * np.linalg.norm(g)  # i don't know why. maybe just take it as granted

    # mass
    m = np.full(2 * nv, dm)

    # gravity
    garr = np.tile(g, nv)

    # Reference length and Voronoi length
    refLen = np.empty(nv)
    for c in range(nv - 1):
        dx = nodes[c + 1] - nodes[c]
        refLen[c] = np.linalg.norm(dx)
    refLen[nv - 1] = np.linalg.norm(nodes[0] - nodes[nv - 1])

    voronoiRefLen = np.empty(nv)
    for c in range(nv):
        voronoiRefLen[c] = 0.5 * (refLen[c - 1] + refLen[c])

    # Initial
    q0 = np.zeros(2 * nv)
    for c in range(nv):
        q0[2 * c] = nodes[c, 0]  # initial x-coord
        q0[2 * c + 1] = nodes[c, 1]  # initial y-coord

    # Constrained dofs
    dofHelper = DofHelper(len(q0))
    # dofHelper.constraint([1])

    u = np.zeros(2 * nv)
    for c in range(nv):
        u[2 * c] = -0.5
        u[2 * c + 1] = -15.0

    # set dt as max at the beginning
    dt = max_dt

    def objfun(q0WithAdditionalConstraintsApplied):
        mUncons = dofHelper.unconstrained_v(m)
        mMat = np.diag(mUncons)

        qCurrentIterate = q0WithAdditionalConstraintsApplied.copy()
        qUncons = dofHelper.unconstrained_v(qCurrentIterate)
        # Newton-Raphson scheme
        iter = 0
        while True:
            # get forces
            Fb, Jb = getFb(qCurrentIterate, EI, nv, voronoiRefLen, -2 * pi / nv, isCircular=True)
            Fs, Js = getFs(qCurrentIterate, EA, nv, refLen, isCircular=True)
            Fg = m * garr
            Fp, Jp = getFp(qCurrentIterate, nv, refLen, InflationPressure)

            Forces = Fb + Fs + Fg + Fp

            # Equation of motion
            du = (qCurrentIterate - q0) / dt - u
            maxDu = np.amax(np.abs(du))
            f = m * du / dt - Forces
            fUncons = dofHelper.unconstrained_v(f)

            # Manipulate the Jacobians
            Jelastic = Jb + Js
            Jelastic = dofHelper.unconstrained_m(Jelastic)
            Jp = dofHelper.unconstrained_m(Jp)
            J = mMat / dt ** 2 - Jelastic - Jp

            # Newton's update
            qUncons = qUncons - np.linalg.solve(J, fUncons)
            dofHelper.write_unconstrained_back(qCurrentIterate, qUncons)

            # Get the norm
            normfNew = np.linalg.norm(fUncons)

            # Update iteration number
            iter += 1
            print('Iter=%d, error=%.8f' % (iter - 1, normfNew))

            if normfNew < tol * ScaleSolver:
                break
            if iter > maximum_iter:
                raise Exception('Cannot converge')
        return qCurrentIterate, f, maxDu

    # Time marching
    ctime = 0

    outputData = []

    def checkMaxDuAndHackTimeIfNecessary(maxDu):  # check whether max-du is too large. if so, go back in time and reduce step size
        nonlocal dt, ctime
        if (dt > min_dt) and (maxDu > limit_du_per_step):  # du too large!
            dt = max(dt * limit_du_per_step / maxDu, min_dt)
            print('Reducing dt and recompute')
            return True
        else:
            return False

    while ctime <= totalTime:
        print('t = %f, dt = %f' % (ctime, dt))
        output = {'time': ctime, 'data': q0.tolist()}
        outputData.append(output)

        qNew, reactionForces, maxDu = objfun(q0)
        if checkMaxDuAndHackTimeIfNecessary(maxDu):
            continue

        dofHelperBackup = deepcopy(dofHelper)  # in case we need to go back in time, we'll need to restore original dof configuration

        # inspect reactionForces to see if any one is negative, which should be UNCONSTRAINED
        needToFree = [unconsInd for unconsInd in dofHelper._constrained if (reactionForces[unconsInd] < 0)]
        if needToFree:
            dofHelper.unconstraint(needToFree)
            print('Contact condition updated. Remove constraints and recompute')
            qNew, reactionForces, maxDu = objfun(q0)
        if checkMaxDuAndHackTimeIfNecessary(maxDu):
            dofHelper = dofHelperBackup
            continue

        # inspect qNew to see if any one falls below ground, which should be CONSTRAINED
        while True:
            q0Effective = None
            for c in range(nv):
                index = 2 * c + 1
                if qNew[index] < 0:  # y < 0: bad!
                    if q0Effective is None:
                        q0Effective = q0.copy()
                    q0Effective[index] = 0
                    dofHelper.constraint([index])
            if q0Effective is None:
                break
            else:
                print('Contact condition violated. Add constraints and recompute')
                qNew, reactionForces, maxDu = objfun(q0Effective)

        if checkMaxDuAndHackTimeIfNecessary(maxDu):
            dofHelper = dofHelperBackup
            continue

        ctime += dt
        u = (qNew - q0) / dt

        # Update x0
        q0 = qNew

        if (dt < max_dt) and (maxDu < limit_du_per_step):
            relax_ratio = limit_du_per_step / maxDu  # we may relax dt by this ratio. but to be conservative, we don't relax that much
            dt = min((0.6 * relax_ratio + 0.4) * dt, max_dt)
            print('Increasing dt')

    # also save final state
    output = {'time': ctime, 'data': q0.tolist()}
    outputData.append(output)

    print('Steps used: %d' % len(outputData))

    return {'meta': {'radius': r0, 'closed': True, 'ground': True}, 'frames': outputData}


if __name__ == '__main__':
    cliRun(runDER)