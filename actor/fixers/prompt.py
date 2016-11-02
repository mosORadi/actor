from actor.core.plugins import Fixer, AsyncDBusEvalMixin
# pylint: disable=too-many-ancestors


class PromptInputFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'prompt'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, title, message):
        # pylint: disable=arguments-differ

        return self.interface.Prompt(title, message,
                                     timeout=self.INFINITE_TIMEOUT,
                                     reply_handler=self.reply_handler,
                                     error_handler=self.error_handler)


class PromptYesNoFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'prompt_yesno'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, title, message):
        # pylint: disable=arguments-differ

        return self.interface.PromptYesNo(title, message,
                                          timeout=self.INFINITE_TIMEOUT,
                                          reply_handler=self.reply_handler,
                                          error_handler=self.error_handler)


class OverlayInputFixer(AsyncDBusEvalMixin, Fixer):

    identifier = 'overlay'

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def run(self, header, message):
        # pylint: disable=arguments-differ

        return self.interface.Overlay(header, message,
                                      timeout=self.INFINITE_TIMEOUT,
                                      reply_handler=self.reply_handler,
                                      error_handler=self.error_handler)
