from plugins import Fixer, AsyncDBusEvalMixin


class PromptInputFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'prompt'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, title, message):
        return self.interface.Prompt(message, title,
            timeout=self.INFINITE_TIMEOUT,
            reply_handler=self.reply_handler,
            error_handler=self.error_handler)


class PromptYesNoFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'prompt_yesno'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, title, message):
        return self.interface.PromptYesNo(message, title,
            timeout=self.INFINITE_TIMEOUT,
            reply_handler=self.reply_handler,
            error_handler=self.error_handler)


class OverlayInputFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'overlay'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, header, message):
        return self.interface.Overlay(header, message,
            timeout=self.INFINITE_TIMEOUT,
            reply_handler=self.reply_handler,
            error_handler=self.error_handler)
