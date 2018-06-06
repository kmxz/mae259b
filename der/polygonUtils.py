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


def intersect(p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
    s1_x = p1_x - p0_x
    s1_y = p1_y - p0_y
    s2_x = p3_x - p2_x
    s2_y = p3_y - p2_y
    d1 = -s2_x * s1_y + s1_x * s2_y
    d2 = -s2_x * s1_y + s1_x * s2_y
    if d1 == 0 or d2 == 0:  # parallel?
        return None
    s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / d1
    t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / d2

    if 0 <= s <= 1 and 0 <= t <= 1:
        return (p0_x + (t * s1_x)), (p0_y + (t * s1_y))
    else:
        return None
