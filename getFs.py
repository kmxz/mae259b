import numpy as np
from sympy import symbols, diff, N, sqrt


def Esₖ(xₖ, xₖₚ, yₖ, yₖₚ, lₖ):  # still need to * EA/2
    return ((1 - sqrt((xₖₚ - xₖ) ** 2 + (yₖₚ - yₖ) ** 2) / lₖ) ** 2) * lₖ


xₖ, xₖₚ, yₖ, yₖₚ, lₖ = symbols('xₖ xₖₚ yₖ yₖₚ lₖ')

Es = Esₖ(xₖ, xₖₚ, yₖ, yₖₚ, lₖ)

F1 = diff(Es, xₖ)
F2 = diff(Es, yₖ)
F3 = diff(Es, xₖₚ)
F4 = diff(Es, yₖₚ)

J11 = diff(F1, xₖ)
J12 = diff(F1, yₖ)
J13 = diff(F1, xₖₚ)
J14 = diff(F1, yₖₚ)
J21 = J12
J22 = diff(F2, yₖ)
J23 = diff(F2, xₖₚ)
J24 = diff(F2, yₖₚ)
J31 = J13
J32 = J23
J33 = diff(F3, xₖₚ)
J34 = diff(F3, yₖₚ)
J41 = J14
J42 = J24
J43 = J34
J44 = diff(F4, yₖₚ)


def gradEs(xk0, yk0, xkp1, ykp1, l_k):
    return np.array([N(F.subs([(xₖ, xk0), (yₖ, yk0), (xₖₚ, xkp1), (yₖₚ, ykp1), (lₖ, l_k)])) for F in [F1, F2, F3, F4]])


def hessEs(xk0, yk0, xkp1, ykp1, l_k):
    return np.array([N(J.subs([(xₖ, xk0), (yₖ, yk0), (xₖₚ, xkp1), (yₖₚ, ykp1), (lₖ, l_k)])) for J in [J11, J12, J13, J14, J21, J22, J23, J24, J31, J32, J33, J34, J41, J42, J43, J44]]).reshape((4, 4))


def getFs(q, EA, ne, refLen):
    Fs = np.zeros(len(q))
    Js = np.zeros((len(q), len(q)))
    for c in range(ne):
        ci = 2 * c
        cf = 2 * c + 4

        xkm1 = q[ci]
        ykm1 = q[ci + 1]
        xk = q[ci + 2]
        yk = q[ci + 3]
        l_k = refLen[c]

        gradEnergy = gradEs(xkm1, ykm1, xk, yk, l_k)
        Fs[ci:cf] = Fs[ci:cf] - 0.5 * EA * gradEnergy * refLen[c]

        hessEnergy = hessEs(xkm1, ykm1, xk, yk, l_k)
        Js[ci:cf, ci:cf] = Js[ci:cf, ci:cf] - 0.5 * EA * hessEnergy * refLen[c]
    return Fs, Js