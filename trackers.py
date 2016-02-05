import datetime

from plugins import Plugin, PluginMount


class Tracker(Plugin):
    """
    Base class for Trackers.
    """

    __metaclass__ = PluginMount

    identifier = None
    availability = None
    message = None

    def __init__(self, *args, **kwargs):
        super(Tracker, self).__init__(*args, **kwargs)

        self.prompt = self.factory_fix('prompt')

    @property
    def recorded(self):
        return self.report('track', self.identifier, self.key) is not None

    @property
    def obtainable(self):
        line = datetime.datetime.strptime(self.availability, "%H:%M").time()
        return datetime.datetime.now().time() > line

    @property
    def key(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def process_value(self, value):
        return value

    def run(self):
        if self.obtainable and not self.recorded:
            value = self.prompt.evaluate(message=self.message,
                                         title=self.identifier)

            if value is None:
                return

            self.fix(
                'track',
                ident=self.identifier,
                key=self.key,
                value=self.process_value(value)
            )

            self.prompt.reset()


class InputTracker(Tracker):
    """
    Tracker that requires manual text input from the user.
    """

    noplugin = True

    def __init__(self, *args, **kwargs):
        super(InputTracker, self).__init__(*args, **kwargs)

        self.prompt = self.factory_fix('prompt')


class BoolTracker(Tracker):
    """
    Tracker that requires manual yes/no input from the user.
    """

    noplugin = True

    def __init__(self, *args, **kwargs):
        super(BoolTracker, self).__init__(*args, **kwargs)
        self.prompt = self.factory_fix('prompt_yesno')

    def process_value(self, value):
        return "Yes" if value else "No"


class IntervalTracker(Tracker):
    """
    Tracker that is triggered in a periodic intervals from the startup.

    Does not survive Actor restarts.
    """

    noplugin = True

    identifier = None
    message = None
    interval = None

    def __init__(self, *args, **kwargs):
        super(IntervalTracker, self).__init__(*args, **kwargs)
        self.last_recorded = datetime.datetime.now()

        if not isinstance(self.interval, int) or self.interval < 1:
            raise ValueError("Interval needs to be a positive integer")

    @property
    def obtainable(self):
        threshold = self.last_recorded + \
            datetime.timedelta(minutes=self.interval)

        return datetime.datetime.now() > threshold

    @property
    def key(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H.%M")

    def run(self):
        if self.obtainable:
            value = self.prompt.evaluate(message=self.message,
                                         title=self.identifier)
            if value is None:
                return

            self.fix(
                'track',
                ident=self.identifier,
                key=self.key,
                value=self.process_value(value)
            )

            self.last_recorded = datetime.datetime.now()
            self.prompt.reset()
