from plugins import IChecker

import datetime

class TimeIntervalChecker(IChecker):
    """
    Checks whether the reported timestamp is in the defined interval.
    (interval computed as <a,b) - start inclusive, end exclusive)

    Expects reports:
      - time - Current time in the format %H.%M

    Options:
      - start : The start of the interval, H.M format
      - end : The end of the interval, H.M format
    """

    export_as = 'time_interval'
    required_plugin_options = ['start', 'end']

    def __init__(self, **options):
        # This saves the time in the timestamp of the following form:
        #     datetime.datetime(1900, 1, 1, 12, 23)
        super(TimeIntervalChecker, self).__init__(**options)
        self.start = datetime.datetime.strptime(str(options['start']), "%H.%M")
        self.end = datetime.datetime.strptime(str(options['end']), "%H.%M")

        # If the start of the interval is later than the end, add one day
        if self.start > self.end:
            self.end = self.end + datetime.timedelta(days=1)

    def check(self, **reports):
        time = datetime.datetime.strptime(reports['time'], "%H.%M")
        time_shifted = time + datetime.timedelta(days=1)

        return ((self.start <= time and time < self.end) or
                (self.start <= time_shifted and time_shifted < self.end))
