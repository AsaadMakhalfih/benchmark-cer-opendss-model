class Vehicle:
    def __init__(self, circuit_label, daily_driving_distance: float = 30.0, driving_times: [tuple] = None, battery_range: float = 350.0, step_size: int = None):
        self._circuit_label = circuit_label
        self._daily_driving_distance = daily_driving_distance
        self._driving_times = driving_times
        self._battery_range = battery_range
        self._step_size = step_size
        self._distance = 0.0
        self.set_driving_distance_per_time_step()

    @property
    def circuit_label(self):
        return self._circuit_label

    @property
    def distance(self):
        return self._distance

    @property
    def battery_range(self):
        return self._battery_range

    def get_distance(self):
        return self._step_size * self._daily_driving_distance / self.get_total_driving_time_in_minutes()

    def set_driving_distance_per_time_step(self):
        self._distance = self._step_size * self._daily_driving_distance / self.get_total_driving_time_in_minutes()

    def get_total_driving_time_in_minutes(self):
        total_time = 0
        for interval in self._driving_times:
            total_time += (interval[1] - interval[0]) * 60
        return total_time

    def check_ev_at_home(self, time_step):
        if sum([1 if interval[0] <= time_step * (self._step_size / 60) < interval[1] else 0 for interval in self._driving_times]) == 0:
            return True
        else:
            return False

    def check_ev_on_road(self, time_step):
        return not self.check_ev_at_home(time_step)
