# Verify the result of differentiation done by sympy (w/ and w/o initial curvature term)
# and compare with result in sample MATLAB code provided in the course material

from math import tan, atan
from sympy import symbols, diff, tan, atan


def φₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ):
    return atan(((xₖₚ - xₖ) * (yₖ - yₖₘ) - (xₖ - xₖₘ) * (yₖₚ - yₖ)) / ((xₖₚ - xₖ) * (xₖ - xₖₘ) + (yₖₚ - yₖ) * (yₖ - yₖₘ)))


def Ebₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ):
    return (2 * tan(φₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ) / 2.0)) ** 2


def EbₖWc(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ, φₖₒ):
    return (2 * tan(φₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ) / 2.0) - 2 * tan(φₖₒ / 2.0)) ** 2


xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ, φₖₒ = symbols('xkm1 ykm1 xk yk xkp1 ykp1 φk0')

Eb = Ebₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ)
EbWc = EbₖWc(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ, φₖₒ)

F1 = diff(Eb, xₖₘ)
F1Wc = diff(EbWc, xₖₘ)
F2 = diff(Eb, yₖₘ)
F2Wc = diff(EbWc, yₖₘ)
F3 = diff(Eb, xₖ)
F3Wc = diff(EbWc, xₖ)
F4 = diff(Eb, yₖ)
F4Wc = diff(EbWc, yₖ)
F6 = diff(Eb, yₖₚ)
F6Wc = diff(EbWc, yₖₚ)
J15 = diff(F1, xₖₚ)
J15Wc = diff(F1Wc, xₖₚ)
J22 = diff(F2, yₖₘ)
J22Wc = diff(F2Wc, yₖₘ)

print(F1Wc)
print(F2Wc)


def calc(x0, y0, x1, y1, x2, y2):
    F3v = F3.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2 })
    F4v = F4.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2 })
    F6v = F6.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2 })
    J15v = J15.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2 })
    J22v = J22.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2 })
    print("TEST RESULTS %f %f %f %f %f" % (F3v, F4v, F6v, J15v, J22v))

def calcWc(x0, y0, x1, y1, x2, y2):
    F3v = F3Wc.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2, φₖₒ: 0 })
    F4v = F4Wc.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2, φₖₒ: 0 })
    F6v = F6Wc.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2, φₖₒ: 0 })
    J15v = J15Wc.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2, φₖₒ: 0 })
    J22v = J22Wc.subs({ xₖₘ: x0, yₖₘ: y0, xₖ: x1, yₖ: y1, xₖₚ: x2, yₖₚ: y2, φₖₒ: 0 })
    print("TEWC RESULTS %f %f %f %f %f" % (F3v, F4v, F6v, J15v, J22v))


def reference(xkm1, ykm1, xk, yk, xkp1, ykp1):
    F3v = 0.4e1 * tan(atan((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk))) / 0.2e1) * ((-ykp1 + ykm1) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (xkp1 - 0.2e1 * xk + xkm1)) / ((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 0.1e1) * (0.1e1 + tan(atan((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk))) / 0.2e1) ** 2)
    F4v = 0.4e1 * tan(atan((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk))) / 0.2e1) * ((-xkm1 + xkp1) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (ykp1 - 0.2e1 * yk + ykm1)) / ((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 0.1e1) * (0.1e1 + tan(atan((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk))) / 0.2e1) ** 2)
    F6v = 0.4e1 * tan(atan((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk))) / 0.2e1) * ((-xk + xkm1) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (yk - ykm1)) / ((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 0.1e1) * (0.1e1 + tan(atan((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk))) / 0.2e1) ** 2)
    J15v = 0.2e1 * ((yk - ykm1) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (xk - xkm1)) / (((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) ** 2) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2) ** 2 * ((ykp1 - yk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-xkp1 + xk)) + 0.4e1 * tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) * (-(ykp1 - yk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (xk - xkm1) - (yk - ykm1) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-xkp1 + xk) + 2 * (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 3 * (-xkp1 + xk) * (xk - xkm1) + (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2) / ((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2) - 0.4e1 * tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) * ((ykp1 - yk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-xkp1 + xk)) / (((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) ** 2) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2) * (2 * (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (yk - ykm1) - 2 * (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 3 * (xk - xkm1)) + 0.4e1 * tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2 * ((ykp1 - yk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-xkp1 + xk)) / (((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) ** 2) * ((yk - ykm1) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (xk - xkm1)) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2)
    J22v = 0.2e1 * (((-xkp1 + xk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-ykp1 + yk)) ** 2) / (((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) ** 2) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2) ** 2 + 0.4e1 * tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) * (-2 * (-xkp1 + xk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-ykp1 + yk) + 2 * (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 3 * (-ykp1 + yk) ** 2) / ((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2) - 0.4e1 * tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) * ((-xkp1 + xk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-ykp1 + yk)) / (((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) ** 2) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2) * (2 * (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-xkp1 + xk) - 2 * (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 3 * (-ykp1 + yk)) + 0.4e1 * tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2 * (((-xkp1 + xk) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) - (-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 * (-ykp1 + yk)) ** 2) / (((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) ** 2 / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)) ** 2 + 1) ** 2) * (0.1e1 + tan(atan(((-(xk - xkm1) * (ykp1 - yk) + (yk - ykm1) * (xkp1 - xk)) / ((xk - xkm1) * (xkp1 - xk) + (yk - ykm1) * (ykp1 - yk)))) / 0.2e1) ** 2)
    print("REFN RESULTS %f %f %f %f %f" % (F3v, F4v, F6v, J15v, J22v))


def test(x0, y0, x1, y1, x2, y2):
    reference(x0, y0, x1, y1, x2, y2)
    calc(x0, y0, x1, y1, x2, y2)
    calcWc(x0, y0, x1, y1, x2, y2)


test(0.020984747136415415, -0.0012902081858690102, 0.03126494881323715, -0.0036105785613046253, 0.0413292993969044, -0.0067391086517100155)
test(0.12553979532274281, -0.011836145483011809, 0.13604952652987384, -0.011244992591174103, 0.14652474317686826, -0.010207473520665747)
test(0.10449254494569678, -0.011660384248668807, 0.11501431460517171, -0.011971401806919912, 0.12553975745469265, -0.011836427627982243)
test(0.02082494202358598, -0.002195205565781611, 0.030570414905444623, -0.006191194095104579, 0.03960497534133094, -0.011609650757539766)
test(0.02, -0.003, 0.03, 0.0, 0.04, -0.005)