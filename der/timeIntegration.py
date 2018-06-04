import numpy as np

from slopeUtils import slopeWall, nWall


def timeIntegration(q0, nv, mapCons, uProjected, dt, objfunBW):

    # step 1: predictor
    q, ForceAll = objfunBW(q0)

    changeMade = False  # flag to identify if another step is needed

    for c in range(nv):
        xPos = q[2 * c]
        yPos = q[2 * c + 1]
        boundaryY = slopeWall(xPos) * xPos

        if (not mapCons[2 * c + 1]) and yPos < boundaryY:
            mapCons[2 * c + 1] = 1

            uProjected[2 * c] = (q[2 * c] - q0[2 * c]) / dt
            uProjected[2 * c + 1] = (q[2 * c + 1] - q0[2 * c + 1]) / dt

            changeMade = True

    # step 2: corrector for new constrained dofs

    if changeMade:
        q, ForceAll = objfunBW(q0)

    # detect and delete constrained dof

    for c in range(nv):
        # Detect new constraints
        xPos = q[2 * c]
        yPos = q[2 * c + 1]
        boundaryY = slopeWall(xPos) * xPos

        if mapCons[2 * c + 1]:
            fReaction = ForceAll[2 * c: 2 * c + 1]
            fNormal = np.dot(fReaction, nWall(xPos))

            # Based on reaction force, release the constraint
            if (fNormal <= 0):  # reaction force is negative
                mapCons[2 * c + 1] = 0  # Unconstrain it
                changeMade = 1

        if yPos < boundaryY:
            mapCons[2 * c + 1] = 1  # constrain it

            uProjected[2 * c] = (q[2 * c] - q0[2 * c]) / dt
            uProjected[2 * c + 1] = (q[2 * c + 1] - q0[2 * c + 1]) / dt

            changeMade = 1

    # Step 3: Corrector for released dofs

    if changeMade:
        q, ForceAll = objfunBW(q0)

    return q, ForceAll
