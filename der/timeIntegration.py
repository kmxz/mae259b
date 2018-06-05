import numpy as np

from slopeUtils import slopeWall, nWall


def timeIntegration(q0, nv, mapCons, uProjected, dt, objfunBW, μₛ):

    for c in range(nv):
        if mapCons[2 * c + 1]:
            mapCons[2 * c] = 1  # always test for static friction

    # step 1: predictor

    q, ForceAll = objfunBW(q0, uProjected)

    # step 2: corrector

    changeMade = False  # flag to identify if another step is needed

    for c in range(nv):
        xPos = q[2 * c]
        yPos = q[2 * c + 1]
        boundaryY = slopeWall(xPos) * xPos

        if (not mapCons[2 * c + 1]) and yPos < boundaryY:
            print("Adding constraint (2-way) @ %d" % c)
            mapCons[2 * c] = 1
            mapCons[2 * c + 1] = 1

            uProjected[2 * c] = (q[2 * c] - q0[2 * c]) / dt
            uProjected[2 * c + 1] = (q[2 * c + 1] - q0[2 * c + 1]) / dt

            changeMade = True

    # detect and delete constrained dof

    for c in range(nv):
        xPos = q[2 * c]
        yPos = q[2 * c + 1]
        boundaryY = slopeWall(xPos) * xPos

        # Delete unnecessary constraints
        if mapCons[2 * c + 1]:
            fReaction = ForceAll[2 * c: 2 * c + 2]
            fNormal = np.dot(fReaction, nWall(xPos))

            # Based on reaction force, release the constraint
            if fNormal <= 0 and yPos >= boundaryY:  # reaction force is negative
                print("Removing constraint (2-way) @ %d" % c)
                mapCons[2 * c] = 0  # unconstrain totally
                mapCons[2 * c + 1] = 0  # unconstrain it
                changeMade = True

            if mapCons[2 * c]:
                fFriction = np.linalg.norm(fReaction - fNormal * nWall(xPos))
                if fFriction > fNormal * μₛ:
                    print("Removing constraint (x) @ %d" % c)
                    mapCons[2 * c] = 0  # unconstrain x
                    changeMade = True
                else:
                    print("STATIC FRICTION KEPT!")

    if changeMade:
        q, ForceAll = objfunBW(q0, uProjected)

    # step 3: one more corrector (for static-friction check)

    changeMade = False

    for c in range(nv):
        xPos = q[2 * c]
        yPos = q[2 * c + 1]
        boundaryY = slopeWall(xPos) * xPos

        # Delete unnecessary constraints
        if mapCons[2 * c + 1]:
            fReaction = ForceAll[2 * c: 2 * c + 2]
            fNormal = np.dot(fReaction, nWall(xPos))

            # Based on reaction force, release the constraint
            if fNormal <= 0 and yPos >= boundaryY:  # reaction force is negative
                print("Retrospectively removing constraint (2-way) @ %d" % c)
                mapCons[2 * c] = 0  # unconstrain totally
                mapCons[2 * c + 1] = 0  # unconstrain it
                changeMade = True

            if mapCons[2 * c]:
                fFriction = np.linalg.norm(fReaction - fNormal * nWall(xPos))
                if fFriction > fNormal * μₛ:
                    print("Retrospectively removing constraint (x) @ %d" % c)
                    mapCons[2 * c] = 0  # unconstrain x
                    changeMade = True

    if changeMade:
        q, ForceAll = objfunBW(q0, uProjected)

    return q, ForceAll
