from plugins import IChecker

import datetime

class TimeIntervalChecker(IChecker):
    """
    Checks whether the reported timestamp is in the defined interval.
    (interval computed as <a,b) - start inclusive, end exclusive)

    Options:
      - start : The start of the interval, H:M format
      - end : The end of the interval, H:M format
    """

    def __init__(self, **options):
        # This saves the time in the timestamp of the following form:
        #     datetime.datetime(1900, 1, 1, 12, 23)
        if options == {}:
            return

        self.start = datetime.datetime.strptime(str(options['start']), "%H.%M")
        self.end = datetime.datetime.strptime(str(options['end']), "%H.%M")

    def check(self, *reports):
        # here assuming that time is passed as the first argument
        # todo: use dictionary here
        time = datetime.datetime.strptime(reports[0], "%H.%M")
        
        return self.start <= time and time < self.end
