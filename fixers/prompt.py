from plugins import Fixer, AsyncDBusEvalMixin


class PromptInputFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'prompt'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, ident, message):
        return self.interface.Prompt(message, ident,
            timeout=self.INFINITE_TIMEOUT,
            reply_handler=self.reply_handler,
            error_handler=self.error_handler)


class PromptYesNoFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'prompt_yesno'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, ident, message):
        return self.interface.PromptYesNo(message, ident,
            timeout=self.INFINITE_TIMEOUT,
            reply_handler=self.reply_handler,
            error_handler=self.error_handler)
