from math import pi, sin, cos
from copy import deepcopy
import numpy as np

from cliUtils import cliRun
from dofHelper import DofHelper
from getFb import getFb
from getFf import getFf
from getFp import getFp
from getFs import getFs


def runDER():
    # number of vertices
    nv = 32

    # max time step
    max_dt = 5e-3

    # min time step
    min_dt = 1.5e-4

    # limit f*dt per step
    limit_f_times_dt = 0.001

    # initial center of circle
    x0 = [0.0, 1.00]

    # inflation pressure (N/m)
    InflationPressure = 160

    # circle radius
    CircleRadius = 0.15

    # circumference length
    CircumferenceLength = 2 * pi * CircleRadius

    # Density
    rho = 1000.0

    # Cross-sectional radius of rod
    r0 = 3.25e-3

    # Young's modulus
    Y = 1e7

    # gravity
    g = [0.0, -9.81]

    # Tolerance on force function. This is multiplied by ScaleSolver so that we do not have to update it based on edge length and time step size
    tol = 1e-7

    # Maximum number of iterations in Newton Solver
    maximum_iter = 100

    # Total simulation time (it exits after t=totalTime)
    totalTime = 2.5

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

    u = np.zeros(2 * nv)
    for c in range(nv):
        u[2 * c] = -2.5
        u[2 * c + 1] = -7.5

    reactionForces = np.zeros(2 * nv)

    # set dt as max at the beginning
    dt = max_dt

    def objfun(q0WithAdditionalConstraintsApplied):
        mMat = np.diag(m)

        qCurrentIterate = q0WithAdditionalConstraintsApplied.copy()
        qUncons = dofHelper.unconstrained_v(qCurrentIterate)

        f = reactionForces
        # Newton-Raphson scheme
        iter = 0
        while True:
            # get forces
            Fb, Jb = getFb(qCurrentIterate, EI, nv, voronoiRefLen, -2 * pi / nv, isCircular=True)
            Fs, Js = getFs(qCurrentIterate, EA, nv, refLen, isCircular=True)
            Fg = m * garr
            Fp, Jp = getFp(qCurrentIterate, nv, refLen, InflationPressure)
            Ff, Jf = getFf(u, nv, dofHelper, f, 0.5)

            Forces = Fb + Fs + Fg + Fp + Ff

            # Equation of motion
            f = m * ((qCurrentIterate - q0) / dt - u) / dt - Forces

            fUncons = dofHelper.unconstrained_v(f)

            # Manipulate the Jacobians
            Jelastic = Jb + Js
            Jexternal = Jp + Jf
            J = mMat / dt ** 2 - Jelastic - Jexternal

            # Newton's update
            qUncons = qUncons - np.linalg.solve(dofHelper.unconstrained_m(J), fUncons)
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
        return qCurrentIterate, f

    # Time marching
    ctime = 0

    outputData = [{'time': ctime, 'data': q0.tolist()}]

    def checkMaxDuAndHackTimeIfNecessary(reactionForces):  # check whether max-du is too large. if so, go back in time and reduce step size
        nonlocal dt, ctime
        maxF = np.amax(reactionForces)
        if (dt > min_dt) and (maxF * dt > limit_f_times_dt):  # du too large!
            relax_ratio = limit_f_times_dt / maxF / dt  # we may contract dt by this ratio. but to be efficient, we don't contract that much
            dt = max((0.3 * relax_ratio + 0.45) * dt, min_dt)
            print('Reducing dt and recompute')
            return True
        else:
            return False

    steps_attempted = 0
    while ctime <= totalTime:
        print('t = %f, dt = %f' % (ctime, dt))
        steps_attempted += 1

        qNew, reactionForces = objfun(q0)
        if checkMaxDuAndHackTimeIfNecessary(reactionForces):
            continue

        dofHelperBackup = deepcopy(dofHelper)  # in case we need to go back in time, we'll need to restore original dof configuration

        # inspect reactionForces to see if any one is negative, which should be UNCONSTRAINED
        needToFree = [unconsInd for unconsInd in dofHelper._constrained if (reactionForces[unconsInd] < 0)]
        if needToFree:
            dofHelper.unconstraint(needToFree)
            print('Contact condition updated. Remove constraints and recompute')
            qNew, reactionForces = objfun(q0)
        if checkMaxDuAndHackTimeIfNecessary(reactionForces):
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
                qNew, reactionForces = objfun(q0Effective)

        if checkMaxDuAndHackTimeIfNecessary(reactionForces):
            dofHelper = dofHelperBackup
            continue

        ctime += dt
        u = (qNew - q0) / dt

        # Update x0
        q0 = qNew

        output = {'time': ctime, 'data': q0.tolist()}
        outputData.append(output)

        relax_ratio = limit_f_times_dt / np.amax(reactionForces) / dt
        if (dt < max_dt) and (relax_ratio > 1):
            dt = min((0.6 * relax_ratio + 0.4) * dt, max_dt)
            print('Increasing dt')

    print('Steps attempted: %d' % steps_attempted)
    print('Steps succeeded: %d' % (len(outputData) - 1))

    return {'meta': {'radius': r0, 'closed': True, 'ground': True}, 'frames': outputData}


if __name__ == '__main__':
    cliRun(runDER)