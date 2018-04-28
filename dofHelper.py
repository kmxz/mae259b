import numpy as np


class DofHelper:

    def __init__(self, total):
        self.total = total
        self.__constrained = list()
        self.__unconstrained = list(range(0, total))

    def unconstrained_v(self, v):  # sub-vector containing only unconstrained indices
        return v[self.__unconstrained]

    def unconstrained_m(self, m):  # sub-matrix containing only unconstrained indices
        return m[np.ix_(self.__unconstrained, self.__unconstrained)]

    def overwrite_with_constraints(self, dst, src):  # overwrite constrained indices in vector dst with the corresponding values from vector src (in-place)
        assert (len(dst) == self.total)
        assert (len(src) == self.total)
        dst[self.__constrained] = src[self.__constrained]

    def write_unconstrained_back(self, dst, src):  # overwrite dst with the unconstained indices set to src
        assert (len(dst) == self.total)
        assert (len(src) == len(self.__unconstrained))
        dst[self.__unconstrained] = src

    def constraint(self, indices):  # constraint multiple indices
        for index in indices:
            try:
                self.__unconstrained.remove(index)
                self.__constrained.append(index)
            except ValueError:
                pass

    def free(self, indices):  # un-constraint one index at a time
        for index in indices:
            try:
                self.__constrained.remove(index)
                self.__unconstrained.append(index)
            except ValueError:
                pass
