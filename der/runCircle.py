import math
from math import pi, sin, cos
import numpy as np

from polygonUtils import area
from cliUtils import cliRun
from getFb import getFb
from getFf import getFf
from getFp import getFp
from getFs import getFs
from slopeUtils import nWall, slopeWall, thetaNormal, invMass


def runDER():
    # number of vertices
    nv = 32

    # max time step
    max_dt = 5e-3

    # min time step
    min_dt = 1e-4

    # limit f*dt per step
    limit_f_times_dt = 0.002

    # initial center of circle
    x0 = [0.0, 2.0]

    # initial inflation pressure (N/m)
    InflationPressure = 10

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

    # dynamic friction coeff.
    μ = 0.4

    # Tolerance on force function. This is multiplied by ScaleSolver so that we do not have to update it based on edge length and time step size
    tol = 1e-7

    # Maximum number of iterations in Newton Solver
    maximum_iter = 100

    # Total simulation time (it exits after t=totalTime)
    totalTime = 10

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

    # Reference Area
    refA = area(q0, nv)

    # Constrained dofs
    mapCons = np.zeros(2 * nv)
    ForceAll = np.zeros(2 * nv)

    u = np.zeros(2 * nv)
    for c in range(nv):
        u[2 * c] = -5
        u[2 * c + 1] = -10

    # set dt as max at the beginning
    dt = max_dt

    def objfunBW(q, uProjected):
        nonlocal ForceAll

        mMatInv = np.diag(1 / m)
        Ident2nv = np.eye(2 * nv)
        imposedAcceleration = np.zeros(2 * nv)

        # Figure out the imposed acceleration
        for c in range(nv):
            xPos = q0[2 * c]
            # Case 1: both dofs are constrained
            if mapCons[2 * c] and mapCons[2 * c + 1] == 1:
                uProjectedPoint = uProjected[2 * c : 2 * c + 2]
                uPerp = np.dot(uProjectedPoint, nWall(xPos)) * nWall(xPos)
                normU = np.linalg.norm(uPerp)
                if normU < (CircumferenceLength / 9.81) * 1e-3: # very small
                    normUinv = 0
                else:
                    normUinv = 1 / normU
                dY = q0[2 * c + 1] - slopeWall(xPos) * q0[2 * c]
                dRDesired = dY * math.sin(thetaNormal)
                tpseudo = dRDesired * normUinv

                q0Point = np.array([q0[2 * c], q0[2 * c + 1]])
                u0Point = np.array([u[2 * c], u[2 * c + 1]])
                qDesired = q0Point + tpseudo * uProjectedPoint

                imposedAcceleration[2 * c: 2 * c + 2] = (qDesired - q0Point) / dt - u0Point
                mMatInv[2 * c: 2 * c + 2, 2 * c: 2 * c + 2] = np.array([[0, 0], [0, 0]])
            # Case 2: one dof is constrained
            elif mapCons[2 * c + 1] == 1:
                dY = q0[2 * c + 1] - slopeWall(xPos) * q0[2 * c]
                dRDesired = dY * math.sin(thetaNormal)
                q0Point = np.array([q0[2 * c], q0[2 * c + 1]])
                u0Point = np.array([u[2 * c], u[2 * c + 1]])
                qDesired = q0Point - nWall(xPos).T * dRDesired
                imposedAcceleration[2 * c : 2 * c + 2] = (qDesired - q0Point) / dt - (nWall(xPos) * np.dot(u0Point, nWall(xPos))).T
                mMatInv[2 * c: 2 * c + 2, 2 * c: 2 * c + 2] = np.dot(invMass(xPos), np.array([[1 / m[2 * c], 0], [0, 1 / m[2 * c + 1]]]))
            else:
                imposedAcceleration[2 * c : 2 * c + 2] = np.array([0, 0])
                mMatInv[2 * c: 2 * c + 2, 2 * c: 2 * c + 2] = np.array([[1 / m[2 * c], 0], [0, 1 / m[2 * c + 1]]])

        # Newton-Raphson scheme
        iter = 0 # number of iterations

        # Initial guess for delta V
        dV = (q - q0) / dt - u

        normfRecords = []

        while True:
            # Figure out the velocities
            uNew = u + dV
            # Figure out the positions
            q = q0 + dt * uNew

            # Get forces
            Fb, Jb = getFb(q, EI, nv, voronoiRefLen, -2 * pi / nv, isCircular=True)
            Fs, Js = getFs(q, EA, nv, refLen, isCircular=True)
            Fg = m * garr
            Ff = getFf(q, u, nv, mapCons, μ, ForceAll)
            pressureRatio = refA / area(q, nv)
            Fp, Jp = getFp(q, nv, refLen, InflationPressure * pressureRatio)

            Forces = Fb + Fs + Fg + Fp + Ff

            # Equation of motion
            ForceAll = m * dV / dt - Forces  # actual force
            f = dV - np.dot(dt * mMatInv, Forces) - imposedAcceleration  # force used for Baraff-Witkin mass modification

            # Get the norm
            normf = np.linalg.norm(f) * np.mean(m) / dt
            normfRecords.append(normf)

            if normf < tol * ScaleSolver:
                print("Converged after %d loops" % iter)
                break
            if iter > maximum_iter:
                print("Normf before exit", normfRecords)
                raise Exception('Cannot converge')

            Jelastic = Jb + Js + Jp
            J = Ident2nv - dt ** 2 * np.dot(mMatInv, Jelastic)

            dV = dV - np.linalg.solve(J, f)
            iter += 1

        return q, ForceAll

    # Time marching
    ctime = 0

    outputData = [{'time': ctime, 'data': q0.tolist()}]

    def checkMaxAndHackTimeIfNecessary():  # check whether max force is too large. if so, go back in time and reduce step size
        nonlocal dt, ctime
        maxF = np.amax(ForceAll)
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

        mapConsBackup = mapCons.copy()
        uProjected = u.copy()

        # step 1: predictor

        qNew, ForceAll = objfunBW(q0, uProjected)
        if checkMaxAndHackTimeIfNecessary():
            continue

        # step 2: corrector

        changeMade = False  # flag to identify if another step is needed

        for c in range(nv):
            xPos = qNew[2 * c]
            yPos = qNew[2 * c + 1]
            boundaryY = slopeWall(xPos) * xPos

            if (not mapCons[2 * c + 1]) and yPos < boundaryY:
                print("Adding constraint @ %d" % c)
                mapCons[2 * c + 1] = 1

                uProjected[2 * c] = (qNew[2 * c] - q0[2 * c]) / dt
                uProjected[2 * c + 1] = (qNew[2 * c + 1] - q0[2 * c + 1]) / dt

                changeMade = True

        # detect and delete constrained dof

        for c in range(nv):
            xPos = qNew[2 * c]
            yPos = qNew[2 * c + 1]
            boundaryY = slopeWall(xPos) * xPos

            # Delete unnecessary constraints
            if mapCons[2 * c + 1]:
                fReaction = ForceAll[2 * c: 2 * c + 2]
                fNormal = np.dot(fReaction, nWall(xPos))

                # Based on reaction force, release the constraint
                if fNormal <= 0 and yPos >= boundaryY:  # reaction force is negative
                    print("Removing constraint @ %d" % c)
                    mapCons[2 * c + 1] = 0  # unconstrain it
                    changeMade = True

        if changeMade:
            qNew, ForceAll = objfunBW(q0, uProjected)

        if checkMaxAndHackTimeIfNecessary():
            mapCons = mapConsBackup
            continue

        ctime += dt
        u = (qNew - q0) / dt

        # Update x0
        q0 = qNew

        output = {'time': ctime, 'data': q0.tolist()}
        outputData.append(output)

        relax_ratio = limit_f_times_dt / np.amax(ForceAll) / dt
        if (dt < max_dt) and (relax_ratio > 1):
            dt = min((0.6 * relax_ratio + 0.4) * dt, max_dt)
            print('Increasing dt')

    print('Steps attempted: %d' % steps_attempted)
    print('Steps succeeded: %d' % (len(outputData) - 1))

    return {'meta': {'radius': r0, 'closed': True, 'ground': True, 'groundAngle': math.degrees(thetaNormal) - 90}, 'frames': outputData}


if __name__ == '__main__':
    cliRun(runDER)