import dbus

from plugins import Fixer


class LockScreenFixer(Fixer):
    """
    Simple fixer that locks your screen.
    """

    identifier = "lock_screen"

    def __init__(self, context):
        super(LockScreenFixer, self).__init__(context)

        bus_name = 'org.freedesktop.ScreenSaver'
        object_path = '/ScreenSaver'
        interface_name = bus_name

        session_bus = dbus.SessionBus()
        dbus_object = session_bus.get_object(bus_name, object_path)
        self.interface = dbus.Interface(dbus_object, interface_name)

    def run(self):
        if not self.interface.GetActive():
            self.interface.Lock()
