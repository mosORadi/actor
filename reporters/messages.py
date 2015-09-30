from plugins import Reporter
import dbus


class MessagesReporter(Reporter):
    """
    Returns a list of raw sender names of users you have unread
    IM messages from.
    """

    identifier = 'messages'

    def __init__(self, context):
        super(MessagesReporter, self).__init__(context)

        try:
            self.bus = dbus.SessionBus()
            proxy = self.bus.get_object("im.pidgin.purple.PurpleService",
                                        "/im/pidgin/purple/PurpleObject")
            self.pidgin = dbus.Interface(
                proxy,
                dbus_interface="im.pidgin.purple.PurpleInterface"
            )
        except dbus.exceptions.DBusException:
            self.pidgin = None

    def get_message_senders(self):
        if not self.pidgin:
            return []

        messages = self.pidgin.PurpleGetIms()
        names = [self.pidgin.PurpleConversationGetName(m)
                 for m in messages]

        return names

    def report(self):
        return ', '.join(self.get_message_senders())
