import os
import sys
import logging
import traceback

from config import config


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

    def log_exception(self):
        exception_type, value, trace = sys.exc_info()

        self.error("Exception: %s", exception_type)
        self.error("Value: %s", value)
        self.error("Traceback (on a new line):\n%s",
                   "\n".join(traceback.format_tb(trace)))

    # Logging setup related methods
    @classmethod
    def setup_logging(cls, level='info'):
        # Setup Actor logging
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }

        logging_level = level_map.get(level)

        log_default_level_warning = False

        if logging_level is None:
            logging_level = logging.INFO
            log_default_level_warning = True

        # Setup main logger
        cls.logger.setLevel(logging.DEBUG)

        # Define logging format
        timeformat = '%(asctime)s:' if config.LOGGING_TIMESTAMP else ''
        formatter = logging.Formatter(
            timeformat + ' %(levelname)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
        )

        # Define default handlers
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging_level)
        stream_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(
            filename=os.path.expanduser(config.LOGGING_FILE)
        )
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(formatter)

        # Setup desired handlers
        if config.LOGGING_TARGET == 'both':
            cls.logger.addHandler(file_handler)
            cls.logger.addHandler(stream_handler)
        elif config.LOGGING_TARGET == 'file':
            cls.logger.addHandler(file_handler)
        else:
            cls.logger.addHandler(stream_handler)

        if log_default_level_warning:
            cls.logger.warning("Logging level %s not recognized, "
                                "using 'info' instead", level)
