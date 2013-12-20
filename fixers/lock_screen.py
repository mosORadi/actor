import dbus

from plugins import IFixer


class LockScreenFixer(IFixer):
    """
    Simple fixer that locks your screen.
    """

    export_as = "lock_screen"
    interface = None

    def lock(self):

        if not self.interface:
            bus_name = 'org.freedesktop.ScreenSaver'
            object_path = '/ScreenSaver'
            interface_name = bus_name

            session_bus = dbus.SessionBus()
            dbus_object = session_bus.get_object(bus_name, object_path)
            self.interface = dbus.Interface(dbus_object, interface_name)

        if not self.interface.GetActive():
            self.interface.Lock()

    def fix(self):
        self.lock()
