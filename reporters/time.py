import datetime

from plugins import IReporter


class TimeReporter(IReporter):

    def report(self):
        time = datetime.datetime.now()
        return time.strftime("%H.%M")
