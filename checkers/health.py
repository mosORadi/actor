from plugins import Checker
import datetime


class HealthChecker(Checker):
    """
    Returns false unless the checker has no health left. Damage is taken by
    calling 'decrease' method. It can be also increased by using the
    'increase' method.

    The health amount is reset on each day, unless reset_daily flag is set
    to False during initlialization.

    Expected setup options:
        maximum - the maximum amount of HP
    """

    identifier = 'health'
    stateless = False

    def __init__(self, maximum, reset_daily=True):
        super(HealthChecker, self).__init__(**options)
        self.today = datetime.date.today()
        self.maximum = maximum
        self.reset_daily = reset_daily

    def decrease(self, delta=1):
        self.health = self.health - delta

    def increase(self, delta=1):
        self.health = self.health + delta

    def reset(self):
        self.health = self.maximum

    def check_day_reset(self):
        # Do not do anything if we're not configured to reset daily
        if not self.reset_daily:
            return

        if datetime.date.today() > self.today:
            self.today = datetime.date.today()
            self.reset()

    def run(self):
        # Check the daily reset first
        self.check_day_reset()

        return self.health < 0
