# Manage constrained and unconstrained degree of freedoms in a system, allowing dynamically change a DOF from constrained to unconstrained state, or the other way around

import numpy as np


class DofHelper:

    def __init__(self, total):
        self.mapCons = np.zeros(total)
