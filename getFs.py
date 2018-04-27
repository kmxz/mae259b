import numpy as np
from math import sqrt


def gradEsAndHessEs(xk, yk, xkp1, ykp1, l_k):
    itm1 = ((xkp1 - xk) ** 2 + (ykp1 - yk) ** 2)
    itm2 = sqrt(itm1)
    itm3 = -(1 - itm2 / l_k) * itm1 ** (-0.5) / l_k

    F = np.empty(4)
    F[0] = itm3 * (-2 * xkp1 + 2 * xk)
    F[1] = itm3 * (-2 * ykp1 + 2 * yk)
    F[2] = itm3 * (2 * xkp1 - 2 * xk)
    F[3] = itm3 * (2 * ykp1 - 2 * yk)

    J11 = (1 / itm1 / l_k ** 2 * (-2 * xkp1 + 2 * xk) ** 2) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * ((-2 * xkp1 + 2 * xk) ** 2) / 2 - 2 * (1 - itm2 / l_k) * (itm1 ** (-0.5)) / l_k
    J12 = (1 / itm1 / l_k ** 2 * (-2 * ykp1 + 2 * yk) * (-2 * xkp1 + 2 * xk)) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * (-2 * xkp1 + 2 * xk) * (-2 * ykp1 + 2 * yk) / 2
    J13 = (1 / itm1 / l_k ** 2 * (2 * xkp1 - 2 * xk) * (-2 * xkp1 + 2 * xk)) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * (-2 * xkp1 + 2 * xk) * (2 * xkp1 - 2 * xk) / 2 + 2 * (1 - itm2 / l_k) * (itm1 ** (-0.5)) / l_k
    J14 = (1 / itm1 / l_k ** 2 * (2 * ykp1 - 2 * yk) * (-2 * xkp1 + 2 * xk)) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * (-2 * xkp1 + 2 * xk) * (2 * ykp1 - 2 * yk) / 2
    J22 = (1 / itm1 / l_k ** 2 * (-2 * ykp1 + 2 * yk) ** 2) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * ((-2 * ykp1 + 2 * yk) ** 2) / 2 - 2 * (1 - itm2 / l_k) * (itm1 ** (-0.5)) / l_k
    J23 = (1 / itm1 / l_k ** 2 * (2 * xkp1 - 2 * xk) * (-2 * ykp1 + 2 * yk)) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * (-2 * ykp1 + 2 * yk) * (2 * xkp1 - 2 * xk) / 2
    J24 = (1 / itm1 / l_k ** 2 * (2 * ykp1 - 2 * yk) * (-2 * ykp1 + 2 * yk)) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * (-2 * ykp1 + 2 * yk) * (2 * ykp1 - 2 * yk) / 2 + 2 * (1 - itm2 / l_k) * (itm1 ** (-0.5)) / l_k
    J33 = (1 / itm1 / l_k ** 2 * (2 * xkp1 - 2 * xk) ** 2) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * ((2 * xkp1 - 2 * xk) ** 2) / 2 - 2 * (1 - itm2 / l_k) * (itm1 ** (-0.5)) / l_k
    J34 = (1 / itm1 / l_k ** 2 * (2 * ykp1 - 2 * yk) * (2 * xkp1 - 2 * xk)) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * (2 * xkp1 - 2 * xk) * (2 * ykp1 - 2 * yk) / 2
    J44 = (1 / itm1 / l_k ** 2 * (2 * ykp1 - 2 * yk) ** 2) / 2 + (1 - itm2 / l_k) * (itm1 ** (-1.5)) / l_k * ((2 * ykp1 - 2 * yk) ** 2) / 2 - 2 * (1 - itm2 / l_k) * (itm1 ** (-0.5)) / l_k

    return F, np.array([J11, J12, J13, J14, J12, J22, J23, J24, J13, J23, J33, J34, J14, J24, J34, J44]).reshape((4, 4))


# the last paramter incicates whether it is a circular shape (i.e. the two ends are connected)
def getFs(q, EA, nv, refLen, isCircular=False):
    def loop(ci, l_k):
        xkm1 = q[ci]
        ykm1 = q[ci + 1]
        xk = q[ci + 2]
        yk = q[ci + 3]
        gradEs, hessEs = gradEsAndHessEs(xkm1, ykm1, xk, yk, l_k)
        return (
            0.5 * EA * gradEs * l_k,
            0.5 * EA * hessEs * l_k
        )

    Fs = np.zeros(len(q))
    Js = np.zeros((len(q), len(q)))
    for c in range(nv - 1):
        ci = 2 * c
        cf = 2 * c + 4

        gradEnergy, hessEnergy = loop(ci, refLen[c])

        Fs[ci:cf] -= gradEnergy

        Js[ci:cf, ci:cf] -= hessEnergy
    if isCircular:  # additional edge which connects two ends together
        gradEnergy, hessEnergy = loop(-2, refLen[nv - 1])

        Fs[-2:] -= gradEnergy[0:2]
        Fs[0:2] -= gradEnergy[2:4]

        Js[-2:, -2:] -= hessEnergy[0:2, 0:2]
        Js[-2:, 0:2] -= hessEnergy[0:2, 2:4]
        Js[0:2, -2:] -= hessEnergy[2:4, 0:2]
        Js[0:2, 0:2] -= hessEnergy[2:4, 2:4]
    return Fs, Js