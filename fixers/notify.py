import dbus

from plugins import Fixer


class NotifyFixer(Fixer):
    """
    Simple fixer, that sends a D-Bus notification.

    Accepted options (defaults in parentheses):
      - headline: Headline of the notification (AcTor Alert!)
      - message : Text of the message sent (Sample message!)
      - app_name: Application name (AcTor)
      - timeout : Timeout of the notification (0)
      - app_icon: Icon of the notification ('')
    """

    export_as = "notify"
    required_plugin_options = ['message']
    optional_plugin_options = ['timeout', 'app_icon', 'app_name', 'headline']

    def __init__(self, **options):
        super(NotifyFixer, self).__init__(**options)
        self.last_notification = 0

    def notify(self):

        headline = self.options.get('headline', 'AcTor Alert!')
        app_name = self.options.get('app_name', 'AcTor')
        app_icon = self.options.get('app_icon', '')
        timeout = self.options.get('timeout', 0)
        message = self.options.get('message', 'Sample message!')

        replaces_id = self.last_notification
        
        bus_name = 'org.freedesktop.Notifications'
        object_path = '/org/freedesktop/Notifications'
        interface_name = bus_name

        session_bus = dbus.SessionBus()
        dbus_object = session_bus.get_object(bus_name, object_path)
        interface = dbus.Interface(dbus_object, interface_name)

        self.last_notification = interface.Notify(app_name, replaces_id, app_icon,
                                                  headline, message, [], {},
                                                  timeout)

    def fix(self, **reports):
        self.notify()
