import datetime
from plugins import Reporter


class TimeReporter(Reporter):
    """
    Returns the current time, as the datetime object.
    """

    identifier = 'time'

    def run(self):
        return datetime.datetime.now()


class WeekdayReporter(Reporter):
    """
    Returns the current week day, represented as string.
    """

    identifier = 'weekday'

    def run(self):
        day = datetime.datetime.now().strftime("%w")

        weekdays = [
            'Sunday',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday']
        return weekdays[int(day)]
