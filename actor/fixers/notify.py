import dbus

from actor.core.plugins import Fixer, DBusMixin
from actor.core.util import Periodic


class NotifyFixer(DBusMixin, Fixer):
    """
    Simple fixer, that sends a D-Bus notification.

    Accepted options (defaults in parentheses):
      - message : Text of the message sent
      - headline: Headline of the notification (AcTor Alert!)
      - app_name: Application name (AcTor)
      - timeout : Timeout of the notification (0)
      - app_icon: Icon of the notification ('')
    """

    identifier = "notify"
    stateless = False

    bus_name = 'org.freedesktop.Notifications'
    object_path = '/org/freedesktop/Notifications'

    def __init__(self, context):
        super(NotifyFixer, self).__init__(context)

        self.last_notification = 0

    def run(self, message, headline="Actor Alert!",
            app_name="Actor", app_icon='', timeout=0):
        # pylint: disable=arguments-differ

        replaces_id = self.last_notification
        self.last_notification = self.interface.Notify(app_name, replaces_id, app_icon,
                                                       headline, message, [], {},
                                                       timeout)
