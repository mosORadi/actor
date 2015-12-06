import datetime

from plugins import Checker
from util import convert_timestamp

class TimeIntervalChecker(Checker):
    """
    Checks whether the current time is in the defined interval.
    (interval computed as <a,b) - start inclusive, end exclusive)

    The start and end points are to be specified by datetime.time object
    or string of '%H.%M' form.
    """

    identifier = 'time_interval'

    def run(self, start, end):
        start = convert_timestamp(start)
        end = convert_timestamp(end)

        # If the start of the interval is later than the end, add one day
        if start > end:
            end = end + datetime.timedelta(days=1)

        time = self.report('time')
        time_shifted = time + datetime.timedelta(days=1)

        return any([start <= time and time < end,
                    start <= time_shifted and time_shifted < end])
