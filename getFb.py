import numpy as np
from sympy import symbols, diff, N, tan, atan


def φₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ):
    return atan(((xₖₚ - xₖ) * (yₖ - yₖₘ) - (xₖ - xₖₘ) * (yₖₚ - yₖ)) / ((xₖₚ - xₖ) * (xₖ - xₖₘ) + (yₖₚ - yₖ) * (yₖ - yₖₘ)))


def Ebₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ):
    return (2 * tan(φₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ) / 2)) ** 2


xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ = symbols('xₖₘ xₖ xₖₚ yₖₘ yₖ yₖₚ')

Eb = Ebₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ)

F1 = diff(Eb, xₖₘ)
F2 = diff(Eb, yₖₘ)
F3 = diff(Eb, xₖ)
F4 = diff(Eb, yₖ)
F5 = diff(Eb, xₖₚ)
F6 = diff(Eb, yₖₚ)

J11 = diff(F1, xₖₘ)
J12 = diff(F1, yₖₘ)
J13 = diff(F1, xₖ)
J14 = diff(F1, yₖ)
J15 = diff(F1, xₖₚ)
J16 = diff(F1, yₖₚ)
J21 = J12
J22 = diff(F2, yₖₘ)
J23 = diff(F2, xₖ)
J24 = diff(F2, yₖ)
J25 = diff(F2, xₖₚ)
J26 = diff(F2, yₖₚ)
J31 = J13
J32 = J23
J33 = diff(F3, xₖ)
J34 = diff(F3, yₖ)
J35 = diff(F3, xₖₚ)
J36 = diff(F3, yₖₚ)
J41 = J14
J42 = J24
J43 = J34
J44 = diff(F4, yₖ)
J45 = diff(F4, xₖₚ)
J46 = diff(F4, yₖₚ)
J51 = J15
J52 = J25
J53 = J35
J54 = J45
J55 = diff(F5, xₖₚ)
J56 = diff(F5, yₖₚ)
J61 = J16
J62 = J26
J63 = J36
J64 = J46
J65 = J56
J66 = diff(F6, yₖₚ)


def gradEb(xkm1, ykm1, xk0, yk0, xkp1, ykp1):
    return np.array([N(F.subs([(xₖₘ, xkm1), (yₖₘ, ykm1), (xₖ, xk0), (yₖ, yk0), (xₖₚ, xkp1), (yₖₚ, ykp1)])) for F in [F1, F2, F3, F4, F5, F6]])


def hessEb(xkm1, ykm1, xk0, yk0, xkp1, ykp1):
    return np.array([N(J.subs([(xₖₘ, xkm1), (yₖₘ, ykm1), (xₖ, xk0), (yₖ, yk0), (xₖₚ, xkp1), (yₖₚ, ykp1)])) for J in [J11, J12, J13, J14, J15, J16, J21, J22, J23, J24, J25, J26, J31, J32, J33, J34, J35, J36, J41, J42, J43, J44, J45, J46, J51, J52, J53, J54, J55, J56, J61, J62, J63, J64, J65, J66]]).reshape((6, 6))


def getFb(q, EI, ne, refLen):
    Fb = np.zeros(len(q))
    Jb = np.zeros((len(q), len(q)))
    for c in range(1, ne):
        ci = 2 * c - 2
        cf = 2 * c + 4

        xkm1 = q[ci]
        ykm1 = q[ci + 1]
        xk = q[ci + 2]
        yk = q[ci + 3]
        xkp1 = q[ci + 4]
        ykp1 = q[ci + 5]

        gradEnergy = gradEb(xkm1, ykm1, xk, yk, xkp1, ykp1)
        Fb[ci:cf] = Fb[ci:cf] - 0.5 * EI * gradEnergy / refLen[c]

        hessEnergy = hessEb(xkm1, ykm1, xk, yk, xkp1, ykp1)
        Jb[ci:cf, ci:cf] = Jb[ci: cf, ci: cf] - 0.5 * EI * hessEnergy / refLen[c]
    return Fb, Jb
