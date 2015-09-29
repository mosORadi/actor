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


class Reporter(Plugin):
    """Reports user activity to the AcTor"""

    __metaclass__ = PluginMount

    def __init__(self, context, **options):
        super(Reporter, self).__init__(context)

    def evaluate(self):
        return self.report_safe()

    def report(self):
        """Returns user activity value"""
        pass

    def report_safe(self):
        try:
            return self.report()
        except Exception as e:
            # TODO: Log the failure
            self.warning("Generation of the report failed: %s" % str(e))
            return None


class Checker(Plugin):
    """Evaluates user activity depending on the input from the responders"""

    __metaclass__ = PluginMount

    def __init__(self, context, **options):
        super(Checker, self).__init__(context)

    def check(self, **kwargs):
        """
        Returns evaluation of the situation - true or false, accorgding
        to the input from the reporters, passed to the check function,
        and custom logic of Checker itself.

        This function should return a dictionary, with mandatory key result
        which holds the value of the check itself, and any optional keys that
        are then passed to the fixer.
        """
        pass


class Fixer(Plugin):

    __metaclass__ = PluginMount

    def __init__(self, context):
        """
        The triggered_by option must be passed via the framework.
        """

        super(Fixer, self).__init__(context)

    def fix(self):
        """
        This function does execute the given action.
        """

        pass
