import numpy as np


class DofHelper:

    def __init__(self, total):
        self.total = total
        self._constrained = list()
        self._unconstrained = list(range(0, total))

    def constrained_v(self, v):  # sub-vector containing only constrained indices
        return v[self._constrained]

    def unconstrained_v(self, v):  # sub-vector containing only unconstrained indices
        return v[self._unconstrained]

    def unconstrained_m(self, m):  # sub-matrix containing only unconstrained indices
        return m[np.ix_(self._unconstrained, self._unconstrained)]

    def overwrite_with_constraints(self, dst, src):  # overwrite constrained indices in vector dst with the corresponding values from vector src (in-place)
        assert (len(dst) == self.total)
        assert (len(src) == self.total)
        dst[self._constrained] = src[self._constrained]

    def write_unconstrained_back(self, dst, src):  # overwrite dst with the unconstrained indices set to src
        assert (len(dst) == self.total)
        assert (len(src) == len(self._unconstrained))
        dst[self._unconstrained] = src

    def constraint(self, indices):  # constraint multiple indices (free -> constrained)
        for index in indices:
            try:
                self._unconstrained.remove(index)
                self._constrained.append(index)
            except ValueError:
                pass

    def unconstraint(self, indices):  # un-constraint multiple indices (free -> constrained)
        for index in indices:
            try:
                self._constrained.remove(index)
                self._unconstrained.append(index)
            except ValueError:
                pass
