import logging

class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class Plugin(object):

    def __init__(self, context):
        self.context = context

    def log(self, log_func, message):
        log_func("%s: %s" % (self.__class__.__name__, message))

    def debug(self, message):
        self.log(logging.debug, message)

    def info(self, message):
        self.log(logging.info, message)

    def warning(self, message):
        self.log(logging.warning, message)

    def error(self, message):
        self.log(logging.error, message)

    def critical(self, message):
        self.log(logging.critical, message)


class Worker(Plugin):
    """
    A base class for Reporter, Checker and Fixer.
    """

    stateless = True
    side_effects = False

    def evaluate(self, *args, **kwargs):
        # TODO: Wrap in exception handling
        return self.run(*args, **kwargs)


class Reporter(Worker):
    """
    Reports user activity to the AcTor.
    """

    __metaclass__ = PluginMount


class Checker(Worker):
    """
    Evaluates user activity depending on the input from the responders.
    """

    __metaclass__ = PluginMount


class Fixer(Worker):
    """
    Performs a custom action on the machine.
    """

    side_effects = True

    __metaclass__ = PluginMount
