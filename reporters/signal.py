from plugins import Reporter
import dbus


class DBusSignalReporter(Reporter):
    signal = None
    export_as = 'signal'

    def __init__(self, **options):
        super(DBusSignalReporter, self).__init__(**options)
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(
            self.save_signal,
            dbus_interface="org.freedesktop.AcTor",
            signal_name="AuditSignal")

    def save_signal(self, message):
        self.signal = message

    def report(self):
        return self.signal
