from sun import Sun
from storm import Storm

class Weather(object):
    def __init__(self, weather):
        self.weather = weather
        self._sun = Sun(weather.sun_azimuth_angle, weather.sun_altitude_angle)
        self._storm = Storm(weather.precipitation)

    def __str__(self):
        return '%s %s' % (self._sun, self._storm)