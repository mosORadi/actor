import dbus

from plugins import IFixer


class NotifyFixer(IFixer):

    def notify(self, body, headline='AcTor Ready!', app_name='AcTor',
        app_icon='', timeout=50000, actions=["one", "two"],
        hints=dict(one="shit"), replaces_id=0):
        _bus_name = 'org.freedesktop.Notifications'
        _object_path = '/org/freedesktop/Notifications'
        _interface_name = _bus_name

        session_bus = dbus.SessionBus()
        obj = session_bus.get_object(_bus_name, _object_path)
        interface = dbus.Interface(obj, _interface_name)
        interface.Notify(app_name, replaces_id, app_icon,
                headline, body, actions, hints, timeout)

    def fix(self, **data):
        self.notify("This is a test notification!")