from plugins import Reporter
import dbus


class DBusSignalReporter(Reporter):
    signal = None
    identifier = 'signal'

    def __init__(self, context):
        super(DBusSignalReporter, self).__init__(context)
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(
            self.save_signal,
            dbus_interface="org.freedesktop.AcTor",
            signal_name="AuditSignal")

    def save_signal(self, message):
        self.signal = message

    def report(self):
        return self.signal
