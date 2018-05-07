# Computing forces and Jacobian of bending mode (which is the gradient and Hessian of bending energy)
# It takes the result of differentiation carried out by "diff/diffWithInitialCurvature.py"

import numpy as np
from math import tan, atan


def gradEbAndHessEb(xkm1, ykm1, xk, yk, xkp1, ykp1, φk0):
    itm1 = 2 * tan(0.5 * φk0)
    itm2 = ((-xk + xkp1) * (xk - xkm1) + (-yk + ykp1) * (yk - ykm1))
    itm3 = ((-xk + xkp1) * (yk - ykm1) - (xk - xkm1) * (-yk + ykp1))
    itm4 = itm3 / itm2 ** 2
    itm5 = tan(0.5 * atan(itm3 / itm2))
    itm6 = (1 + itm3 ** 2 / itm2 ** 2)
    itm7 = ((ykm1 - ykp1) / itm2 + itm3 * (2 * xk - xkm1 - xkp1) / itm2 ** 2)
    itm8 = ((-xkm1 + xkp1) / itm2 + itm3 * (2 * yk - ykm1 - ykp1) / itm2 ** 2)
    itm9 = ((-xk + xkm1) / itm2 + (-yk + ykm1) * itm4)
    itm10 = ((-xk + xkm1) * itm4 + (yk - ykm1) / itm2)
    itm11 = (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * itm5 / itm6 ** 2
    itm12 = (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) / itm6
    itm13 = itm12 / itm6
    itm14 = itm3 ** 2 / itm2 ** 3

    F = np.empty(6)
    F[0] = 2 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm12
    F[1] = 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm12
    F[2] = 2 * itm7 * itm12
    F[3] = 2 * itm8 * itm12
    F[4] = 2 * itm10 * itm12
    F[5] = 2 * itm9 * itm12

    J11 = 2 * ((-2 * xk + 2 * xkp1) * (-xk + xkp1) * itm3 / itm2 ** 3 + 2 * (-xk + xkp1) * (-yk + ykp1) / itm2 ** 2) * itm12 + 2 * (-(-2 * xk + 2 * xkp1) * itm14 - (-2 * yk + 2 * ykp1) * itm4) * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm13 + 2 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) ** 2 * itm11 + 2 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) ** 2 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2
    J12 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkp1) * (xk - xkp1) / itm2 ** 2 + (-xk + xkp1) * (-2 * yk + 2 * ykp1) * itm3 / itm2 ** 3 + (-yk + ykp1) ** 2 / itm2 ** 2) / itm6 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm11 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (-(2 * xk - 2 * xkp1) * itm4 - (-2 * yk + 2 * ykp1) * itm14) * itm13
    J13 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkp1) * (ykm1 - ykp1) / itm2 ** 2 + (-xk + xkp1) * itm3 * (4 * xk - 2 * xkm1 - 2 * xkp1) / itm2 ** 3 + (-yk + ykp1) * (2 * xk - xkm1 - xkp1) / itm2 ** 2 - itm4) / itm6 + 2 * itm7 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm11 + 2 * itm7 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (-(2 * ykm1 - 2 * ykp1) * itm4 - itm3 ** 2 * (4 * xk - 2 * xkm1 - 2 * xkp1) / itm2 ** 3) * itm13
    J14 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkp1) * (-xkm1 + xkp1) / itm2 ** 2 + (-xk + xkp1) * itm3 * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3 + (-yk + ykp1) * (2 * yk - ykm1 - ykp1) / itm2 ** 2 - 1 / itm2) / itm6 + 2 * itm8 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm11 + 2 * itm8 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (-(-2 * xkm1 + 2 * xkp1) * itm4 - itm3 ** 2 * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3) * itm13
    J15 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-2 * xk + 2 * xkm1) * (-xk + xkp1) * itm3 / itm2 ** 3 + (-xk + xkm1) * (-yk + ykp1) / itm2 ** 2 + (-xk + xkp1) * (yk - ykm1) / itm2 ** 2 + itm4) / itm6 + 2 * (-(-2 * xk + 2 * xkm1) * itm14 - (2 * yk - 2 * ykm1) * itm4) * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm13 + 2 * itm10 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm11 + 2 * itm10 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (itm5 ** 2 + 1) ** 2 / itm6 ** 2
    J16 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkm1) * (-xk + xkp1) / itm2 ** 2 + (-xk + xkp1) * (-2 * yk + 2 * ykm1) * itm3 / itm2 ** 3 + (-yk + ykm1) * (-yk + ykp1) / itm2 ** 2 + 1 / itm2) / itm6 + 2 * itm9 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm11 + 2 * itm9 * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * (-(-2 * xk + 2 * xkm1) * itm4 - (-2 * yk + 2 * ykm1) * itm14) * ((-xk + xkp1) * itm4 + (-yk + ykp1) / itm2) * itm13
    J22 = 2 * (2 * (xk - xkp1) * (-yk + ykp1) / itm2 ** 2 + (-2 * yk + 2 * ykp1) * (-yk + ykp1) * itm3 / itm2 ** 3) * itm12 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) ** 2 * itm11 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) ** 2 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * (-(2 * xk - 2 * xkp1) * itm4 - (-2 * yk + 2 * ykp1) * itm14) * itm13
    J23 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((xk - xkp1) * (2 * xk - xkm1 - xkp1) / itm2 ** 2 + (-yk + ykp1) * (ykm1 - ykp1) / itm2 ** 2 + (-yk + ykp1) * itm3 * (4 * xk - 2 * xkm1 - 2 * xkp1) / itm2 ** 3 + 1 / itm2) / itm6 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm7 * itm11 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm7 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * (-(2 * ykm1 - 2 * ykp1) * itm4 - itm3 ** 2 * (4 * xk - 2 * xkm1 - 2 * xkp1) / itm2 ** 3) * itm13
    J24 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((xk - xkp1) * (2 * yk - ykm1 - ykp1) / itm2 ** 2 + (-xkm1 + xkp1) * (-yk + ykp1) / itm2 ** 2 + (-yk + ykp1) * itm3 * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3 - itm4) / itm6 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm8 * itm11 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm8 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * (-(-2 * xkm1 + 2 * xkp1) * itm4 - itm3 ** 2 * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3) * itm13
    J25 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-2 * xk + 2 * xkm1) * (-yk + ykp1) * itm3 / itm2 ** 3 + (-xk + xkm1) * (xk - xkp1) / itm2 ** 2 + (-yk + ykp1) * (yk - ykm1) / itm2 ** 2 - 1 / itm2) / itm6 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * (-(-2 * xk + 2 * xkm1) * itm14 - (2 * yk - 2 * ykm1) * itm4) * itm13 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm10 * itm11 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm10 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2
    J26 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkm1) * (-yk + ykp1) / itm2 ** 2 + (xk - xkp1) * (-yk + ykm1) / itm2 ** 2 + (-2 * yk + 2 * ykm1) * (-yk + ykp1) * itm3 / itm2 ** 3 + itm4) / itm6 + 2 * itm9 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * itm11 + 2 * itm9 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * ((xk - xkp1) / itm2 + (-yk + ykp1) * itm4) * (-(-2 * xk + 2 * xkm1) * itm4 - (-2 * yk + 2 * ykm1) * itm14) * itm13
    J33 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * (2 * (ykm1 - ykp1) * (2 * xk - xkm1 - xkp1) / itm2 ** 2 + 2 * itm4 + itm3 * (2 * xk - xkm1 - xkp1) * (4 * xk - 2 * xkm1 - 2 * xkp1) / itm2 ** 3) / itm6 + 2 * itm7 ** 2 * itm11 + 2 * itm7 ** 2 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * itm7 * (-(2 * ykm1 - 2 * ykp1) * itm4 - itm3 ** 2 * (4 * xk - 2 * xkm1 - 2 * xkp1) / itm2 ** 3) * itm13
    J34 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xkm1 + xkp1) * (2 * xk - xkm1 - xkp1) / itm2 ** 2 + (ykm1 - ykp1) * (2 * yk - ykm1 - ykp1) / itm2 ** 2 + itm3 * (2 * xk - xkm1 - xkp1) * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3) / itm6 + 2 * itm8 * itm7 * itm11 + 2 * itm8 * itm7 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * itm7 * (-(-2 * xkm1 + 2 * xkp1) * itm4 - itm3 ** 2 * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3) * itm13
    J35 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-2 * xk + 2 * xkm1) * itm3 * (2 * xk - xkm1 - xkp1) / itm2 ** 3 + (-xk + xkm1) * (ykm1 - ykp1) / itm2 ** 2 + (yk - ykm1) * (2 * xk - xkm1 - xkp1) / itm2 ** 2 - itm4) / itm6 + 2 * itm7 * (-(-2 * xk + 2 * xkm1) * itm14 - (2 * yk - 2 * ykm1) * itm4) * itm13 + 2 * itm7 * itm10 * itm11 + 2 * itm7 * itm10 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2
    J36 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkm1) * (2 * xk - xkm1 - xkp1) / itm2 ** 2 + (-2 * yk + 2 * ykm1) * itm3 * (2 * xk - xkm1 - xkp1) / itm2 ** 3 + (-yk + ykm1) * (ykm1 - ykp1) / itm2 ** 2 - 1 / itm2) / itm6 + 2 * itm9 * itm7 * itm11 + 2 * itm9 * itm7 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * itm7 * (-(-2 * xk + 2 * xkm1) * itm4 - (-2 * yk + 2 * ykm1) * itm14) * itm13
    J44 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * (2 * (-xkm1 + xkp1) * (2 * yk - ykm1 - ykp1) / itm2 ** 2 + 2 * itm4 + itm3 * (2 * yk - ykm1 - ykp1) * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3) / itm6 + 2 * itm8 ** 2 * itm11 + 2 * itm8 ** 2 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * itm8 * (-(-2 * xkm1 + 2 * xkp1) * itm4 - itm3 ** 2 * (4 * yk - 2 * ykm1 - 2 * ykp1) / itm2 ** 3) * itm13
    J45 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-2 * xk + 2 * xkm1) * itm3 * (2 * yk - ykm1 - ykp1) / itm2 ** 3 + (-xk + xkm1) * (-xkm1 + xkp1) / itm2 ** 2 + (yk - ykm1) * (2 * yk - ykm1 - ykp1) / itm2 ** 2 + 1 / itm2) / itm6 + 2 * itm8 * (-(-2 * xk + 2 * xkm1) * itm14 - (2 * yk - 2 * ykm1) * itm4) * itm13 + 2 * itm8 * itm10 * itm11 + 2 * itm8 * itm10 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2
    J46 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkm1) * (2 * yk - ykm1 - ykp1) / itm2 ** 2 + (-xkm1 + xkp1) * (-yk + ykm1) / itm2 ** 2 + (-2 * yk + 2 * ykm1) * itm3 * (2 * yk - ykm1 - ykp1) / itm2 ** 3 - itm4) / itm6 + 2 * itm9 * itm8 * itm11 + 2 * itm9 * itm8 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * itm8 * (-(-2 * xk + 2 * xkm1) * itm4 - (-2 * yk + 2 * ykm1) * itm14) * itm13
    J55 = 2 * ((-2 * xk + 2 * xkm1) * (-xk + xkm1) * itm3 / itm2 ** 3 + 2 * (-xk + xkm1) * (yk - ykm1) / itm2 ** 2) * itm12 + 2 * (-(-2 * xk + 2 * xkm1) * itm14 - (2 * yk - 2 * ykm1) * itm4) * itm10 * itm13 + 2 * itm10 ** 2 * itm11 + 2 * itm10 ** 2 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2
    J56 = 2 * (-itm1 + 2 * itm5) * (itm5 ** 2 + 1) * ((-xk + xkm1) ** 2 / itm2 ** 2 + (-xk + xkm1) * (-2 * yk + 2 * ykm1) * itm3 / itm2 ** 3 + (-yk + ykm1) * (yk - ykm1) / itm2 ** 2) / itm6 + 2 * itm9 * itm10 * itm11 + 2 * itm9 * itm10 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * (-(-2 * xk + 2 * xkm1) * itm4 - (-2 * yk + 2 * ykm1) * itm14) * itm10 * itm13
    J66 = 2 * (2 * (-xk + xkm1) * (-yk + ykm1) / itm2 ** 2 + (-2 * yk + 2 * ykm1) * (-yk + ykm1) * itm3 / itm2 ** 3) * itm12 + 2 * itm9 ** 2 * itm11 + 2 * itm9 ** 2 * (itm5 ** 2 + 1) ** 2 / itm6 ** 2 + 2 * itm9 * (-(-2 * xk + 2 * xkm1) * itm4 - (-2 * yk + 2 * ykm1) * itm14) * itm13

    return F, np.array([J11, J12, J13, J14, J15, J16, J12, J22, J23, J24, J25, J26, J13, J23, J33, J34, J35, J36, J14, J24, J34, J44, J45, J46, J15, J25, J35, J45, J55, J56, J16, J26, J36, J46, J56, J66]).reshape((6, 6))


# the last paramter incicates whether it is a circular shape (i.e. the two ends are connected)
def getFb(q, EI, nv, voronoiRefLen, φk0, isCircular=False):
    def loop(ci, l_k):
        xkm1 = q[ci]
        ykm1 = q[ci + 1]
        xk = q[ci + 2]
        yk = q[ci + 3]
        xkp1 = q[ci + 4]
        ykp1 = q[ci + 5]

        gradEb, hessEb = gradEbAndHessEb(xkm1, ykm1, xk, yk, xkp1, ykp1, φk0)
        return (0.5 * EI * gradEb / l_k, 0.5 * EI * hessEb / l_k)

    Fb = np.zeros(len(q))
    Jb = np.zeros((len(q), len(q)))
    for c in range(1, nv - 1):
        ci = 2 * c - 2
        cf = 2 * c + 4

        gradEnergy, hessEnergy = loop(ci, voronoiRefLen[c])

        Fb[ci:cf] -= gradEnergy

        Jb[ci:cf, ci:cf] -= hessEnergy
    if isCircular:  # additional node at start (i.e. c = 0)
        gradEnergy, hessEnergy = loop(-2, voronoiRefLen[0])

        Fb[-2:] -= gradEnergy[0:2]
        Fb[0:4] -= gradEnergy[2:6]

        Jb[-2:, -2:] -= hessEnergy[0:2, 0:2]
        Jb[-2:, 0:4] -= hessEnergy[0:2, 2:6]
        Jb[0:4, -2:] -= hessEnergy[2:6, 0:2]
        Jb[0:4, 0:4] -= hessEnergy[2:6, 2:6]
    if isCircular:  # additional node at end (i.e. c = nv - 1)
        gradEnergy, hessEnergy = loop(-4, voronoiRefLen[nv - 1])

        Fb[-4:] -= gradEnergy[0:4]
        Fb[0:2] -= gradEnergy[4:6]

        Jb[-4:, -4:] -= hessEnergy[0:4, 0:4]
        Jb[-4:, 0:2] -= hessEnergy[0:4, 4:6]
        Jb[0:2, -4:] -= hessEnergy[4:6, 0:4]
        Jb[0:2, 0:2] -= hessEnergy[4:6, 4:6]
    return Fb, Jb
