import numpy as np
from math import *


class PVPanels:
    def __init__(self, circuit_label, pmpp=7.2, temp_factor=None):
        if temp_factor is None:
            temp_factor = [[0, 25, 75, 100], [1.2, 1.0, 0.8, 0.6]]
        self._circuit_label = circuit_label
        self._temp_factor = temp_factor
        self._pmpp = pmpp

    @property
    def circuit_label(self):
        return self._circuit_label

    def get_temp_factor(self, temp):
        return np.interp(temp, self._temp_factor[0], self._temp_factor[1])

    def get_dc_power(self, irrad, temp):
        return self._pmpp * irrad * self.get_temp_factor(temp)

    @classmethod
    def get_dc_power_cls(cls, pmpp, irrad, temp, temp_factor=None):
        """Class method to compute DC power without an instance."""
        # Set default temp_factor if not provided
        if temp_factor is None:
            temp_factor = [[0, 25, 75, 100], [1.2, 1.0, 0.8, 0.6]]

        # Extract temperature vs. factor curve
        temp_x, temp_y = temp_factor
        # Interpolate temperature factor
        factor = np.interp(temp, temp_x, temp_y)
        # Compute DC power
        return pmpp * irrad * factor