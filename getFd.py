# Computing forces and Jacobian of damping
import numpy as np

# should be using center-of-mass? but we just use geometrical center for now
def getFd(newQ, oldQ, nv, dt, factor):
    [oldX, oldY] = oldQ.reshape((nv, 2)).transpose()
    oldCenterX = np.mean(oldX)
    oldCenterY = np.mean(oldY)
    [newX, newY] = newQ.reshape((nv, 2)).transpose()
    newCenterX = np.mean(newX)
    newCenterY = np.mean(newY)
    centerVx = (newCenterX - oldCenterX) / dt
    centerVy = (newCenterY - oldCenterY) / dt
    Fd = np.empty(2 * nv)
    for c in range(nv):
        vx = (newQ[2 * c] - oldQ[2 * c]) / dt
        relativeVx = vx - centerVx
        vy = (newQ[2 * c + 1] - oldQ[2 * c + 1]) / dt
        relativeVy = vy - centerVy
        Fd[2 * c] = - relativeVx * factor
        Fd[2 * c + 1] = - relativeVy * factor
    Jd = - factor * np.eye(2 * nv) / dt
    return Fd, Jd
