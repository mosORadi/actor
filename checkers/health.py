from plugins import Checker
import dbus
import datetime


class HealthChecker(Checker):
    """
    Returns false unless the checker has no health left. Damage is taken by
    receiving D-Bus HealthDecreseSignal on org.freedesktop.AcTor interface.

    The health amount is reset on each day.

    Expected options:
        delay - coundown duration in seconds
        id - identifier of countdown checker, should be unique across all
             activities
    """

    export_as = 'health'
    required_plugin_options = ['health_amount', 'id']

    def __init__(self, **options):
        super(HealthChecker, self).__init__(**options)

        self.bus = dbus.SessionBus()
        self.bus.add_signal_receiver(
            self.decrease_health,
            dbus_interface="org.freedesktop.AcTor",
            signal_name="HealthDecreaseSignal")

        self.health_id = self.options.get('id')
        self.health_remaining = self.options.get('health_amount', 0)
        self.today = datetime.date.today()

    def decrease_health(self, health_id, **options):
        if self.health_id != health_id:
            return

        if datetime.date.today() != self.today:
            self.today = datetime.date.today()
            self.health_remaining = self.options.get('health')

        self.health_remaining = self.health_remaining - 1

    def check(self, **reports):
        self.debug("Remaining! : %s" % str(self.health_remaining))
        return self.health_remaining < 0
