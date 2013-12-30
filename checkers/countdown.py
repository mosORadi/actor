from plugins import IChecker
import dbus
import datetime


class CountdownChecker(IChecker):
    export_as = 'countdown'

    def __init__(self, **options):
        super(CountdownChecker, self).__init__(**options)

        self.bus = dbus.SessionBus()
        self.bus.add_signal_receiver(
            self.start_countdown,
            dbus_interface="org.freedesktop.AcTor",
            signal_name="CountdownStartSignal")

        self.countdown_start = None

        delay_seconds = self.options.get('delay', 300)
        self.delta = datetime.timedelta(0, delay_seconds, 0)

    def start_countdown(self, countdown_id, **options):
        if self.countdown_start is None:
            self.countdown_start = datetime.datetime.now()
            print "The signal was caught"

    def check(self, **reports):
        if self.countdown_start is None:
            return False
        else:
            return datetime.datetime.now() - self.countdown_start > self.delta
