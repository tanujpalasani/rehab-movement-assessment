class MovementAnalyzer:
    def __init__(self, filter_alpha=1.0):
        self.min_angle = float("inf")
        self.max_angle = 0.0
        self.smoothed_angle = None
        self.alpha = filter_alpha

    def update(self, angle):
        angle = float(angle)
        if self.smoothed_angle is None or self.alpha >= 1.0:
            self.smoothed_angle = angle
        else:
            self.smoothed_angle = (self.alpha * angle) + ((1 - self.alpha) * self.smoothed_angle)

        working_angle = self.smoothed_angle
        if working_angle < self.min_angle:
            self.min_angle = working_angle

        if working_angle > self.max_angle:
            self.max_angle = working_angle

        rom = self.max_angle - self.min_angle
        return rom, self.min_angle, self.max_angle
