import math
from math import pi, sin, cos
import numpy as np
from shapely.geometry import Polygon, Point

from polygonUtils import area
from cliUtils import cliRun
from getFb import getFb
from getFf import getFf
from getFp import getFp
from getFs import getFs
from slopeUtils import nWall, slopeWall, thetaNormal, invMass


def runDER():
    # 2 objects. all variables ending with _AN should be an array of objects
    OAN = 2

    # number of vertices
    nv = 32

    # max time step
    max_dt = 5e-3

    # min time step
    min_dt = 1e-4

    # limit f*dt per step
    limit_f_times_dt = 0.0025

    # initial center of circle
    x0_AN = [[-0.5, 0.75], [0.5, 0.75]]

    # initial bulk velocity
    u0_AN = [[1.25, -2.5], [-1.25, -2.5]]

    # initial inflation pressure (N/m)
    InflationPressure_AN = [2.5, 2.5]

    # circle radius
    CircleRadius_AN = [0.15, 0.15]

    # circumference length
    CircumferenceLength_AN = [2 * pi * i for i in CircleRadius_AN]

    # Density
    rho_AN = [1000.0, 1000.0]

    # Cross-sectional radius of rod
    r0 = 3.25e-3

    # Young's modulus
    Y_AN = [1e7, 1e7]

    # gravity
    g = [0.0, -9.81]

    # dynamic friction coeff.
    μ = 0.4

    # Tolerance on force function. This is multiplied by ScaleSolver so that we do not have to update it based on edge length and time step size
    tol = 5e-7

    # Maximum number of iterations in Newton Solver
    maximum_iter = 100

    # Total simulation time (it exits after t=totalTime)
    totalTime = 5

    # Utility quantities
    EI_AN = [Y * pi * r0 ** 4 / 4 for Y in Y_AN]
    EA_AN = [Y * pi * r0 ** 2 for Y in Y_AN]

    dm_AN = [pi * r0 ** 2 * CircumferenceLength_AN[oa] * rho_AN[oa] / nv for oa in range(OAN)]  # mass per node

    nodes_AN = []
    for oa in range(OAN):
        nodes_oa = np.empty((nv, 2))
        x0_oa = x0_AN[oa]
        for c in range(nv):
            nodes_oa[c, 0] = x0_oa[0] + CircleRadius_AN[oa] * cos(c * 2 * pi / nv + pi / 2)
            nodes_oa[c, 1] = x0_oa[1] + CircleRadius_AN[oa] * sin(c * 2 * pi / nv + pi / 2)
        nodes_AN.append(nodes_oa)

    ScaleSolver_AN = [dm * np.linalg.norm(g) for dm in dm_AN]  # i don't know why. maybe just take it as granted

    # mass
    m_AN = [np.full(2 * nv, dm) for dm in dm_AN]

    # gravity
    garr = np.tile(g, nv)

    # Reference length and Voronoi length
    refLen_AN = []
    for oa in range(OAN):
        refLen_oa = np.empty(nv)
        nodes_oa = nodes_AN[oa]
        for c in range(nv - 1):
            dx = nodes_oa[c + 1] - nodes_oa[c]
            refLen_oa[c] = np.linalg.norm(dx)
            refLen_oa[nv - 1] = np.linalg.norm(nodes_oa[0] - nodes_oa[nv - 1])
        refLen_AN.append(refLen_oa)

    voronoiRefLen_AN = []
    for oa in range(OAN):
        voronoiRefLen_oa = np.empty(nv)
        refLen_oa = refLen_AN[oa]
        for c in range(nv):
            voronoiRefLen_oa[c] = 0.5 * (refLen_oa[c - 1] + refLen_oa[c])
        voronoiRefLen_AN.append(voronoiRefLen_oa)

    # Initial
    q0_AN = []
    for oa in range(OAN):
        q0 = np.zeros(2 * nv)
        nodes = nodes_AN[oa]
        for c in range(nv):
            q0[2 * c] = nodes[c, 0]  # initial x-coord
            q0[2 * c + 1] = nodes[c, 1]  # initial y-coord
        q0_AN.append(q0)

    # Reference Area
    refA_AN = [area(q0, nv) for q0 in q0_AN]

    # Constrained dofs
    mapCons_AN = [np.zeros(2 * nv) for _ in range(OAN)]
    ForceAll_AN = [np.zeros(2 * nv) for _ in range(OAN)]

    u_AN = []
    for oa in range(OAN):
        u_oa = np.zeros(2 * nv)
        u0_oa = u0_AN[oa]
        for c in range(nv):
            u_oa[2 * c] = u0_oa[0]
            u_oa[2 * c + 1] = u0_oa[1]
        u_AN.append(u_oa)

    # set dt as max at the beginning
    dt = max_dt

    def objfunBW(q, oa, mapCons):
        nonlocal ForceAll_AN

        mMatInv = np.diag(1 / m_AN[oa])
        Ident2nv = np.eye(2 * nv)
        imposedAcceleration = np.zeros(2 * nv)

        q0 = q0_AN[oa]
        u = u_AN[oa]
        m = m_AN[oa]

        # Figure out the imposed acceleration
        for c in range(nv):
            xPos = q0[2 * c]
            # Case 2: one dof is constrained
            if mapCons[2 * c + 1] == 1:
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
            Fb, Jb = getFb(q, EI_AN[oa], nv, voronoiRefLen_AN[oa], -2 * pi / nv, isCircular=True)
            Fs, Js = getFs(q, EA_AN[oa], nv, refLen_AN[oa], isCircular=True)
            Fg = m * garr
            Ff = getFf(q, u, nv, mapCons_AN[oa], μ, ForceAll_AN[oa])
            pressureRatio = refA_AN[oa] / area(q, nv)
            Fp, Jp = getFp(q, nv, refLen_AN[oa], InflationPressure_AN[oa] * pressureRatio)

            Forces = Fb + Fs + Fg + Fp + Ff

            # Equation of motion
            ForceAll_AN[oa] = m * dV / dt - Forces  # actual force
            f = dV - np.dot(dt * mMatInv, Forces) - imposedAcceleration  # force used for Baraff-Witkin mass modification

            # Get the norm
            normf = np.linalg.norm(f) * np.mean(m) / dt
            normfRecords.append(normf)

            if normf < tol * ScaleSolver_AN[oa]:
                print("Converged after %d loops" % iter)
                break
            if iter > maximum_iter:
                print("Normf before exit", normfRecords)
                raise Exception('Cannot converge')

            Jelastic = Jb + Js + Jp
            J = Ident2nv - dt ** 2 * np.dot(mMatInv, Jelastic)

            dV = dV - np.linalg.solve(J, f)
            iter += 1

        return q, ForceAll_AN[oa]

    # Time marching
    ctime = 0

    outputData = [{'time': ctime, 'data': [q0.tolist() for q0 in q0_AN]}]

    def checkMaxAndHackTimeIfNecessary(ForceAll):  # check whether max force is too large. if so, go back in time and reduce step size
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

        q0_work_AN = q0_AN.copy()
        u_work_AN = u_AN.copy()
        mapCons_work_AN = [mapCons.copy() for mapCons in mapCons_AN]

        redo = False

        for oa in range(OAN):
            q0 = q0_AN[oa]
            mapCons = mapCons_work_AN[oa]

            # step 1: predictor

            qNew, ForceAll = objfunBW(q0, oa, mapCons)
            if checkMaxAndHackTimeIfNecessary(ForceAll):
                redo = True
                break

            # step 2: corrector

            changeMade = False  # flag to identify if another step is needed

            for c in range(nv):
                xPos = qNew[2 * c]
                yPos = qNew[2 * c + 1]
                boundaryY = slopeWall(xPos) * xPos

                if (not mapCons[2 * c + 1]) and yPos < boundaryY:
                    print("Adding constraint @ %d" % c)
                    mapCons[2 * c + 1] = 1
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
                    if fNormal <= 0 and yPos >= boundaryY - 2e-6:  # reaction force is negative
                        print("Removing constraint @ %d" % c)
                        mapCons[2 * c + 1] = 0  # unconstrain it
                        changeMade = True

            if changeMade:
                qNew, ForceAll = objfunBW(q0, oa, mapCons)

            if checkMaxAndHackTimeIfNecessary(ForceAll):
                redo = True
                break

            u_work_AN[oa] = (qNew - q0) / dt

            # Update x0
            q0_work_AN[oa] = qNew

        if redo:
            continue

        # detect collision with each other
        for target in range(OAN):
            q_target = q0_work_AN[target]
            for surface in range(OAN):
                if target == surface:
                    continue
                q_surface = q0_work_AN[surface]
                polygon = Polygon([(q_surface[2 * c], q_surface[2 * c + 1]) for c in range(nv)])
                for c in range(nv):
                    if polygon.contains(Point(q_target[2 * c], q_target[2 * c + 1])):
                        # we have a problem here
                        pass

        q0_AN = q0_work_AN
        u_AN = u_work_AN
        mapCons_AN = mapCons_work_AN

        ctime += dt

        output = {'time': ctime, 'data': [q0.tolist() for q0 in q0_AN]}
        outputData.append(output)

        relax_ratio = limit_f_times_dt / max([np.amax(ForceAll) for ForceAll in ForceAll_AN]) / dt
        if (dt < max_dt) and (relax_ratio > 1):
            dt = min((0.6 * relax_ratio + 0.4) * dt, max_dt)
            print('Increasing dt')

    print('Steps attempted: %d' % steps_attempted)
    print('Steps succeeded: %d' % (len(outputData) - 1))

    return {'meta': {'radius': r0, 'closed': True, 'ground': True, 'groundAngle': math.degrees(thetaNormal) - 90, 'numberOfStructure': OAN}, 'frames': outputData}


if __name__ == '__main__':
    cliRun(runDER)