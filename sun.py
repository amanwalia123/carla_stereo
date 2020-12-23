class Sun(object):
    def __init__(self, azimuth, altitude):
        self.azimuth = -90.0
        self.altitude = -90.0
        self._t = 0.0

    def __str__(self):
        return 'Sun(alt: %.2f, azm: %.2f)' % (self.altitude, self.azimuth)