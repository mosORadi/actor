from plugins import IReporter
import dbus


class MessagesReporter(IReporter):
    """
    Returns a list of raw sender names of users you have unread
    IM messages from.
    """

    export_as = 'messages'

    def __init__(self, **options):
        super(MessagesReporter, self).__init__(**options)

        self.bus = dbus.SessionBus()
        proxy = self.bus.get_object("im.pidgin.purple.PurpleService",
                                    "/im/pidgin/purple/PurpleObject")
        self.pidgin = dbus.Interface(
                          proxy,
                          dbus_interface="im.pidgin.purple.PurpleInterface")

    def get_message_senders(self):
        messages = self.pidgin.PurpleGetIms()
        names = [self.pidgin.PurpleConversationGetName(m)
                 for m in messages]

        return names

    def report(self):
        return ', '.join(self.get_message_senders())
