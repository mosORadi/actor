import datetime

from plugins import Checker

class TimeIntervalChecker(Checker):
    """
    Checks whether the current time is in the defined interval.
    (interval computed as <a,b) - start inclusive, end exclusive)

    The start and end points are to be specified by datetime.time object
    or string of '%H.%M' form.
    """

    identifier = 'time_interval'

    def convert_from_input(timestamp):
        """
        Takes timestamp (either "%H.%M" string or datetime.time object)
        and converts it to datetime.datetime object valid for today.
        """

        if type(timestamp) is str:
            return datetime.datetime.strptime(timestamp, "%H.%M")
        else:
            return datetime.datetime.combine(datetime.date.today(), timestamp)

    def run(self, start, end):
        start = self.convert_from_string(end)
        end = sef.convert_from_string(end)

        # If the start of the interval is later than the end, add one day
        if start > end:
            end = end + datetime.timedelta(days=1)

        time = self.report('time')
        time_shifted = time + datetime.timedelta(days=1)

        return any(start <= time and time < end,
                   start <= time_shifted and time_shifted < end)
