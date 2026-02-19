from src.models.load import Load
from src.models.inverter import Inverter, HybridInverter
from src.models.ev import EVSystem


class Meter:
    def __init__(self, circuit_label, loads: list[Load] = None, evs: list[EVSystem] = None, inverters: list[Inverter] = None):
        self._total_ev_power = 0
        self._total_load_power = 0
        self._total_inverter_power = 0
        self._total_grid_power = 0
        self._circuit_label = circuit_label
        self._loads = list(loads) if loads is not None else []
        self._evs = list(evs) if evs is not None else []
        self._inverters = list(inverters) if inverters is not None else []

    def add_load(self, load: Load):
        self._loads.append(load)

    def add_ev(self, ev: EVSystem):
        self._evs.append(ev)

    def add_inverter(self, inverter: Inverter):
        self._inverters.append(inverter)

    def get_total_load_power(self):
        self._total_load_power = sum(load.p_in for load in self._loads)
        return self._total_load_power

    def get_total_ev_power(self):
        if not self._evs:
            return 0
        self._total_ev_power = sum(ev.p_in for ev in self._evs)
        return self._total_ev_power

    def get_total_inverter_power(self):
        self._total_inverter_power = sum(inverter.p_out for inverter in self._inverters)
        return self._total_inverter_power

    @property
    def total_inverter_power(self):
        return self.get_total_inverter_power()

    @property
    def total_load_power(self):
        return self.get_total_load_power()

    @property
    def total_ev_power(self):
        return self.get_total_ev_power()

    def get_grid_power(self):
        """
        The power from the load (PQ Load) is always positive and retrieved via p_in.
        The power from the inverter is positive when it is exported and negative when it is imported, retrieved by p_out.
        The power from the ev is negative when it is exported and positive when it is imported, retrieved by p_in.
        The power exported from grid is negative, power exported to the grid is positive.
        Following the previous convention we have:
        P_grid = P_inv - P_ev - P_load
        """

        return self.total_inverter_power - self.total_ev_power - self.total_load_power

    @property
    def inverter_to_load(self):
        """Power from inverters to loads."""
        inverter_export = max(self.total_inverter_power, 0)
        return min(inverter_export, self.total_load_power)

    @property
    def battery_power(self) -> float:
        """Power to/from batteries (only for HybridInverter types)."""
        total = 0.0
        for inv in self._inverters:
            if isinstance(inv, HybridInverter):
                # Replace `.battery_power` with your actual HybridInverter attribute/method
                total += inv.battery_power
        return total

    @property
    def inverter_to_ev(self):
        """Power from inverters to EVs (charging)."""
        if self.total_ev_power < 0:
            return 0  # EV is discharging, not charging
        remaining_inv = max(self.total_inverter_power - self.inverter_to_load, 0)
        return min(remaining_inv, self.total_ev_power)

    @property
    def inverter_to_grid(self):
        """Excess inverter power exported to the grid."""
        remaining_inv = max(self.total_inverter_power - self.inverter_to_load - self.inverter_to_ev, 0)
        return remaining_inv if self.get_grid_power() > 0 else 0

    @property
    def ev_to_load(self):
        """Power from discharging EVs to loads."""
        ev_discharge = max(-self.total_ev_power, 0)
        unmet_load = max(self.total_load_power - self.inverter_to_load, 0)
        return min(ev_discharge, unmet_load)

    @property
    def ev_to_inverter(self):
        """Power from discharging EVs to inverters (if inverters are importing)."""
        if self.total_inverter_power >= 0:
            return 0  # Inverters are not importing
        ev_discharge_remaining = max(-self.total_ev_power - self.ev_to_load, 0)
        inverter_import = abs(self.total_inverter_power)
        return min(ev_discharge_remaining, inverter_import)

    @property
    def ev_to_grid(self):
        """Excess EV discharge power exported to the grid."""
        ev_discharge_remaining = max(
            -self.total_ev_power - self.ev_to_load - self.ev_to_inverter, 0
        )
        return ev_discharge_remaining if self.get_grid_power() > 0 else 0

    @property
    def grid_to_load(self):
        """Power from the grid to loads."""
        unmet_load = max(
            self.total_load_power - self.inverter_to_load - self.ev_to_load, 0
        )
        return unmet_load if self.get_grid_power() < 0 else 0

    @property
    def grid_to_ev(self):
        """Power from the grid to EVs (charging)."""
        if self.total_ev_power < 0:
            return 0  # EV is discharging, not charging
        unmet_ev = max(self.total_ev_power - self.inverter_to_ev, 0)
        return unmet_ev if self.get_grid_power() < 0 else 0

    @property
    def grid_to_inverter(self):
        """Power from the grid to inverters (if inverters are importing)."""
        if self.total_inverter_power >= 0:
            return 0  # Inverters are exporting
        return abs(self.total_inverter_power) if self.get_grid_power() < 0 else 0

    def initialise_energy_flow_results(self) -> dict:
        summary_data = {
            "Load Power (kW)": [],
            "Inverter Power (kW)": [],
            "EV Power (kW)": [],
            "Inverter to Load (kW)": [],
            "Inverter to Grid (kW)": [],
            "Inverter to EV (kW)": [],
            "Battery Power (kW)": [],
            "Grid to Load (kW)": [],
            "Grid to EV (kW)": [],
            "EV to Load (kW)": [],
            "EV to Grid (kW)": []
        }

        # Check for loads (corrected from `is None` to `not self._loads`)
        if not self._loads:
            del summary_data["Load Power (kW)"]
            del summary_data["Inverter to Load (kW)"]
            del summary_data["EV to Load (kW)"]
            del summary_data["Grid to Load (kW)"]

        # Check for inverters
        if not self._inverters:
            del summary_data["Inverter Power (kW)"]
            del summary_data["Inverter to Load (kW)"]
            del summary_data["Inverter to EV (kW)"]
            del summary_data["Inverter to Grid (kW)"]
            del summary_data["Battery Power (kW)"]  # Remove if no inverters
        else:
            # Remove "Inverter to Battery" if no HybridInverters exist
            has_hybrid = any(isinstance(inv, HybridInverter) for inv in self._inverters)
            if not has_hybrid:
                del summary_data["Battery Power (kW)"]

        # Check for EVs
        if not self._evs:
            del summary_data["EV Power (kW)"]
            try:
                del summary_data["EV to Load (kW)"]
            except:
                pass
            try:
                del summary_data["EV to Grid (kW)"]
            except:
                pass
            try:
                del summary_data["Grid to EV (kW)"]
            except:
                pass
            try:
                del summary_data["Inverter to EV (kW)"]
            except:
                pass

        return summary_data

    def get_energy_flow_results(self) -> dict:
        summary = {}

        if self._inverters:
            summary["Inverter Power (kW)"] = self.total_inverter_power
            # Add inverter-to-battery only if HybridInverters exist
            if any(isinstance(inv, HybridInverter) for inv in self._inverters):
                summary["Battery Power (kW)"] = self.battery_power

        if self._loads:
            summary["Load Power (kW)"] = self.total_load_power

        if self._inverters and self._loads:
            summary["Inverter to Load (kW)"] = self.inverter_to_load

        if self._inverters:
            summary["Inverter to Grid (kW)"] = self.inverter_to_grid

        if self._inverters and self._evs:
            summary["Inverter to EV (kW)"] = self.inverter_to_ev

        if self._loads:
            summary["Grid to Load (kW)"] = self.grid_to_load

        if self._evs:
            summary["Grid to EV (kW)"] = self.grid_to_ev

        if self._evs and self._loads:
            summary["EV to Load (kW)"] = self.ev_to_load

        if self._evs:
            summary["EV to Grid (kW)"] = self.ev_to_grid

        if self._evs:
            summary["EV Power (kW)"] = self.total_ev_power

        return summary
