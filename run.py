import datetime
from math import pi
import numpy as np
import json

from getFb import getFb
from getFs import getFs


def runDER(computeThread):
    # number of vertices
    nv = 20

    # time step
    dt = 1e-2

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
    totalTime = 5

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
    consIndStart = range(4)
    unconsInd = range(4, len(q0))

    u = np.zeros(2 * nv)
    uUncons = u[unconsInd]

    def objfun(qUncons):
        q0Uncons = q0[unconsInd]
        mUncons = m[unconsInd]
        mMat = np.diag(mUncons)
        # Newton-Raphson scheme
        iter = 0
        normf = tol * ScaleSolver * 10
        while normf > tol * ScaleSolver:
            qCurrentIterate = q0.copy()
            qCurrentIterate[consIndStart] = q0[consIndStart]
            qCurrentIterate[unconsInd] = qUncons

            # get forces
            Fb, Jb = getFb(qCurrentIterate, EI, ne, refLen)
            Fs, Js = getFs(qCurrentIterate, EA, ne, refLen)
            Fg = m * garr

            Forces = Fb + Fs + Fg
            Forces = Forces[unconsInd]

            # Equation of motion
            f = mUncons * (qUncons - q0Uncons) / dt ** 2 - mUncons * uUncons / dt - Forces

            # Manipulate the Jacobians
            Jelastic = Jb + Js
            Jelastic = Jelastic[unconsInd.start:unconsInd.stop, unconsInd.start:unconsInd.stop]
            J = mMat / dt ** 2 - Jelastic

            # Newton's update
            qUncons = qUncons - np.linalg.solve(J, f)

            # Get the norm
            normfNew = np.linalg.norm(f)

            # Update iteration number
            iter += 1
            print('Iter=%d, error=%f' % (iter - 1, normfNew))
            normf = normfNew

            if (iter > maximum_iter):
                raise Exception('Cannot converge')
        return qUncons

    # Time marching
    Nsteps = int(totalTime / dt)  # number of time steps

    ctime = 0

    outputData = []

    for timeStep in range(Nsteps):
        print('t = %f' % ctime)
        output = {'time': ctime, 'data': q0.tolist()}
        outputData.append(output)
        if computeThread:
            computeThread.put(output)

        qUncons = q0[unconsInd]
        qUncons = objfun(qUncons)

        q = q0.copy()
        q[unconsInd] = qUncons
        u = (q - q0) / dt
        print("q0", q0)
        print("q", q)
        print("u", u)
        ctime = ctime + dt
        uUncons = u[unconsInd]

        # Update x0
        q0 = q

    # also save final state
    output = {'time': ctime, 'data': q0.tolist()}
    outputData.append(output)
    if computeThread:
        computeThread.put(output)

    outputFileName = datetime.datetime.now().strftime('data/output-%m_%d-%H_%M_%S.json')
    json.dump(outputData, open(outputFileName, "w"))
    print("Result saved to " + outputFileName)
    if computeThread:
        computeThread.end(outputFileName)


if __name__ == '__main__':
    runDER(None)