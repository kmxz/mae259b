# shoelace formula
def area(q, nv):
    out = 0
    for c in range(1, nv):
        out += q[2 * (c - 1)] * q[2 * c + 1]
        out -= q[2 * (c - 1) + 1] * q[2 * c]
    out += q[2 * (nv - 1)] * q[1]
    out -= q[2 * (nv - 1) + 1] * q[0]
    return out / 2


# derivative of area
def dArea(q, nv, i):
    out = 0
    if i % 2:  # y
        out += q[i - 3]  # from y_c to x_(c-1)
        out -= q[(i + 1) % (2 * nv)]  # from y_c to x_(c+1)
    else:  # x
        out += q[(i + 3) % (2 * nv)]  # from x_c to y_(c+1)
        out -= q[i - 1]  # from x_c to y_(c-1)
    return out / 2