import datetime
from plugins import Reporter


class TimeReporter(Reporter):

    identifier = 'time'

    def report(self):
        time = datetime.datetime.now()
        return time.strftime("%H.%M")


class WeekdayReporter(Reporter):

    identifier = 'weekday'

    def report(self):
        day = datetime.datetime.now().strftime("%w")

        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return weekdays[int(day)]
