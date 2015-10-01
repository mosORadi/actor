from plugins import Reporter, DBusMixin


class MessagesReporter(DBusMixin, Reporter):
    """
    Returns a list of raw sender names of users you have unread
    IM messages from.
    """

    identifier = 'messages'

    bus_name = "im.pidgin.purple.PurpleService"
    object_path = "/im/pidgin/purple/PurpleObject"
    interface_name ="im.pidgin.purple.PurpleInterface"

    def run(self):
        if not self.interface:
            return []

        messages = self.interface.PurpleGetIms()
        names = [self.interface.PurpleConversationGetName(m)
                 for m in messages]

        return names
