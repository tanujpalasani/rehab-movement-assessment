class MovementAnalyzer:
    def __init__(self):
        self.min_angle = float("inf")
        self.max_angle = 0

    def update(self, angle):
        if angle < self.min_angle:
            self.min_angle = angle

        if angle > self.max_angle:
            self.max_angle = angle

        rom = self.max_angle - self.min_angle

        return rom, self.min_angle, self.max_angle
