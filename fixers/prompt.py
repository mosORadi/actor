from plugins import Fixer, DBusMixin, AsyncEvalMixin


class PromptFixer(AsyncEvalMixin, DBusMixin, Fixer):

    stateless = False

    identifier = 'prompt'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, ident, message):
        return self.interface.Prompt(ident, message,
            timeout=self.INFINITE_TIMEOUT)
