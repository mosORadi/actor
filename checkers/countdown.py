from plugins import IChecker
import dbus
import datetime


class CountdownChecker(IChecker):
    """
    Returns false unless countdown has finished. Countdown is started by
    emitting a D-Bus CountdownStartSignal on org.freedesktop.AcTor interface.

    Expected options:
        delay - coundown duration in seconds
        id - identifier of countdown checker, should be unique across all
             activities
    """

    export_as = 'countdown'
    required_plugin_options = ['delay', 'id']

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
        if self.countdown_start is None and countdown_id == self.options.get('id'):
            self.countdown_start = datetime.datetime.now()

    def check(self, **reports):
        if self.countdown_start is None:
            return False
        else:
            return datetime.datetime.now() - self.countdown_start > self.delta
