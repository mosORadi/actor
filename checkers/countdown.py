from plugins import Checker
import datetime


class CountdownChecker(Checker):
    """
    Returns false unless countdown has finished. Countdown is started by
    calling start method.
    """

    identifier = 'countdown'
    stateless = False

    def __init__(self, delay):
        super(CountdownChecker, self).__init__(**options)

        self.countdown_start = None
        self.delta = datetime.timedelta(seconds=delay)

    def start(self):
        if self.countdown_start is None:
            self.countdown_start = datetime.datetime.now()

    def reset(self, delay=None):
        self.countdown_start = None

        if delay:
            self.delta = datetime.timedelta(seconds=delay)

    def run(self):
        if self.countdown_start is None:
            return False
        else:
            return datetime.datetime.now() - self.countdown_start > self.delta
