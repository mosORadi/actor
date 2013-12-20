import dbus

from plugins import IFixer


class SuspendFixer(IFixer):
    """
    Simple fixer that suspends your workstation.
    """

    export_as = "suspend"
    interface = None

    def suspend(self):

        if not self.interface:
            bus_name = 'org.freedesktop.PowerManagement'
            object_path = '/org/freedesktop/PowerManagement'
            interface_name = bus_name

            session_bus = dbus.SessionBus()
            dbus_object = session_bus.get_object(bus_name, object_path)
            self.interface = dbus.Interface(dbus_object, interface_name)

        self.interface.Suspend()

    def fix(self):
        self.suspend()
