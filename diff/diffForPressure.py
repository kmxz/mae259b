# Get Fi and Jij for normal force on rod (air pressure)
# Print the code that can be directly pasted into getFp.py

from sympy import symbols, sqrt, diff

x0, x1, y0, y1 = symbols('x0 x1 y0 y1')

norm = sqrt(((y1 - y0) ** 2) + ((x1 - x0) ** 2))

fx = (y1 - y0) / norm
fy = (x0 - x1) / norm

F1 = fx / 2
print("    F[0] =", F1)
F2 = fy / 2
print("    F[1] =", F2)
F3 = fx / 2
print("    F[2] =", F3)
F4 = fy / 2
print("    F[3] =", F4)

J11 = diff(F1, x0)
print("    J11 =", J11)
J12 = diff(F1, y0)
print("    J12 =", J12)
J13 = diff(F1, x1)
print("    J13 =", J13)
J14 = diff(F1, y1)
print("    J14 =", J14)

J21 = diff(F2, x0)
print("    J21 =", J21)
J22 = diff(F2, y0)
print("    J22 =", J22)
J23 = diff(F2, x1)
print("    J23 =", J23)
J24 = diff(F2, y1)
print("    J24 =", J24)

J31 = diff(F3, x0)
print("    J31 =", J31)
J32 = diff(F3, y0)
print("    J32 =", J32)
J33 = diff(F3, x1)
print("    J33 =", J33)
J34 = diff(F3, y1)
print("    J34 =", J34)

J41 = diff(F4, x0)
print("    J41 =", J41)
J42 = diff(F4, y0)
print("    J42 =", J42)
J43 = diff(F4, x1)
print("    J43 =", J43)
J44 = diff(F4, y1)
print("    J44 =", J44)


