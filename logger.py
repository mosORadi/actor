import logging


class LoggerMixin(object):
    """
    This mixin adds logging capabilities to the class. All clases inheriting
    from this mixin use the 'main' logger unless overriden otherwise.

    LoggerMixin also provides convenient shortcut methods for logging.
    """

    logger = logging.getLogger('main')

    # Logging-related helpers
    def log(self, log_func, message, *args):
        log_func("%s: %s" % (self.__class__.__name__, message), *args)

    # Interface to be leveraged by the class
    def debug(self, message, *args):
        self.log(self.logger.debug, message, *args)

    def info(self, message, *args):
        self.log(self.logger.info, message, *args)

    def warning(self, message, *args):
        self.log(self.logger.warning, message, *args)

    def error(self, message, *args):
        self.log(self.logger.error, message, *args)

    def critical(self, message, *args):
        self.log(self.logger.critical, message, *args)
