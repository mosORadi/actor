from plugins import Fixer, DBusMixin, AsyncEvalMixin


class PromptInputFixer(AsyncEvalMixin, DBusMixin, Fixer):

    stateless = False

    identifier = 'prompt'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, ident, message):
        return self.interface.Prompt(message, ident,
            timeout=self.INFINITE_TIMEOUT)


class PromptYesNoFixer(AsyncEvalMixin, DBusMixin, Fixer):

    stateless = False

    identifier = 'prompt_yesno'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, ident, message):
        return self.interface.PromptYesNo(message, ident,
            timeout=self.INFINITE_TIMEOUT)
