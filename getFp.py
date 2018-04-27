from math import sqrt
import numpy as np


# the last paramter incicates whether it is a circular shape (i.e. the two ends are connected)
def getFp(q, nv, refLen, forcePerUnitLength):
    Fp = np.zeros(len(q))
    Jp = np.zeros((len(q), len(q)))
    for c in range(nv):
        ci = 2 * c - 2  # edge between node c - 1 and node c
        x0 = q[ci]
        y0 = q[ci + 1]
        x1 = q[ci + 2]
        y1 = q[ci + 3]
        forceMagnitude = refLen[c - 1] * forcePerUnitLength

        itm1 = sqrt((-x0 + x1) ** 2 + (-y0 + y1) ** 2)
        itm2 = (2 * ((-x0 + x1) ** 2 + (-y0 + y1) ** 2) ** (3 / 2))

        Fp[ci] += (-y0 + y1) / (2 * itm1) * forceMagnitude
        Fp[ci + 1] += (x0 - x1) / (2 * itm1) * forceMagnitude
        Fp[ci + 2] += (-y0 + y1) / (2 * itm1) * forceMagnitude
        Fp[ci + 3] += (x0 - x1) / (2 * itm1) * forceMagnitude

        J11 = (-x0 + x1) * (-y0 + y1) / itm2 * forceMagnitude
        J12 = (-y0 + y1) ** 2 / itm2 - 1 / (2 * itm1) * forceMagnitude
        J13 = (x0 - x1) * (-y0 + y1) / itm2 * forceMagnitude
        J14 = (-y0 + y1) * (y0 - y1) / itm2 + 1 / (2 * itm1) * forceMagnitude
        J21 = (-x0 + x1) * (x0 - x1) / itm2 + 1 / (2 * itm1) * forceMagnitude
        J22 = (x0 - x1) * (-y0 + y1) / itm2 * forceMagnitude
        J23 = (x0 - x1) ** 2 / itm2 - 1 / (2 * itm1) * forceMagnitude
        J24 = (x0 - x1) * (y0 - y1) / itm2 * forceMagnitude
        J31 = (-x0 + x1) * (-y0 + y1) / itm2 * forceMagnitude
        J32 = (-y0 + y1) ** 2 / itm2 - 1 / (2 * itm1) * forceMagnitude
        J33 = (x0 - x1) * (-y0 + y1) / itm2 * forceMagnitude
        J34 = (-y0 + y1) * (y0 - y1) / itm2 + 1 / (2 * itm1) * forceMagnitude
        J41 = (-x0 + x1) * (x0 - x1) / itm2 + 1 / (2 * itm1) * forceMagnitude
        J42 = (x0 - x1) * (-y0 + y1) / itm2 * forceMagnitude
        J43 = (x0 - x1) ** 2 / itm2 - 1 / (2 * itm1) * forceMagnitude
        J44 = (x0 - x1) * (y0 - y1) / itm2 * forceMagnitude

        Jp[ci, ci] += J11
        Jp[ci, ci + 1] += J12
        Jp[ci, ci + 2] += J13
        Jp[ci, ci + 3] += J14
        Jp[ci + 1, ci] += J21
        Jp[ci + 1, ci + 1] += J22
        Jp[ci + 1, ci + 2] += J23
        Jp[ci + 1, ci + 3] += J24
        Jp[ci + 2, ci] += J31
        Jp[ci + 2, ci + 1] += J32
        Jp[ci + 2, ci + 2] += J33
        Jp[ci + 2, ci + 3] += J34
        Jp[ci + 3, ci] += J41
        Jp[ci + 3, ci + 1] += J42
        Jp[ci + 3, ci + 2] += J43
        Jp[ci + 3, ci + 3] += J44

    return Fp, Jp
