# Get Fi and Jij for bending modes, with initial curvature φₖₒ
# Print the code that can be directly pasted into getFb.py

from sympy import symbols, diff, tan, atan

def φₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ):
    return atan(((xₖₚ - xₖ) * (yₖ - yₖₘ) - (xₖ - xₖₘ) * (yₖₚ - yₖ)) / ((xₖₚ - xₖ) * (xₖ - xₖₘ) + (yₖₚ - yₖ) * (yₖ - yₖₘ)))

def Ebₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ, φₖₒ):
    return (2 * tan(φₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ) / 2.0) - 2 * tan(φₖₒ / 2.0)) ** 2

xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ, φₖₒ = symbols('xkm1 xk xkp1 ykm1 yk ykp1 φk0')

Eb = Ebₖ(xₖₘ, xₖ, xₖₚ, yₖₘ, yₖ, yₖₚ, φₖₒ)

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
J22 = diff(F2, yₖₘ)
J23 = diff(F2, xₖ)
print("    J23 =", J23)
J24 = diff(F2, yₖ)
print("    J24 =", J24)
J25 = diff(F2, xₖₚ)
print("    J25 =", J25)
J26 = diff(F2, yₖₚ)
print("    J26 =", J26)
J33 = diff(F3, xₖ)
print("    J33 =", J33)
J34 = diff(F3, yₖ)
print("    J34 =", J34)
J35 = diff(F3, xₖₚ)
print("    J35 =", J35)
J36 = diff(F3, yₖₚ)
print("    J36 =", J36)
J44 = diff(F4, yₖ)
print("    J44 =", J44)
J45 = diff(F4, xₖₚ)
print("    J45 =", J45)
J46 = diff(F4, yₖₚ)
print("    J46 =", J46)
J55 = diff(F5, xₖₚ)
print("    J55 =", J55)
J56 = diff(F5, yₖₚ)
print("    J56 =", J56)
J66 = diff(F6, yₖₚ)
print("    J66 =", J66)