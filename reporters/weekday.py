import datetime
from plugins import IReporter


class WeekdayReporter(IReporter):

    export_as = 'weekday'

    def report(self):
        day = datetime.datetime.now().strftime("%w")

        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return weekdays[int(day)]
