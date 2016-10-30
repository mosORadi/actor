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
    @classmethod
    def log(cls, log_func, message, *args):
        log_func("%s: %s" % (cls.__name__, message), *args)

    # Interface to be leveraged by the class
    @classmethod
    def debug(cls, message, *args):
        cls.log(cls.logger.debug, message, *args)

    @classmethod
    def info(cls, message, *args):
        cls.log(cls.logger.info, message, *args)

    @classmethod
    def warning(cls, message, *args):
        cls.log(cls.logger.warning, message, *args)

    @classmethod
    def error(cls, message, *args):
        cls.log(cls.logger.error, message, *args)

    @classmethod
    def critical(cls, message, *args):
        cls.log(cls.logger.critical, message, *args)

    @classmethod
    def log_exception(cls, exception_type=None, value=None, trace=None):
        if exception_type is None:
            exception_type, value, trace = sys.exc_info()

        cls.error("Exception: %s", exception_type)
        cls.error("Value: %s", value)
        cls.error("Traceback (on a new line):\n%s",
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
