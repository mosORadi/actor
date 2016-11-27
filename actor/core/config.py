import imp
import os


class CustomOverride(type):

    def __init__(cls, name, bases, attrs):
        super(CustomOverride, cls).__init__(name, bases, attrs)

        base_class = bases[0]

        if not hasattr(cls, '_custom'):
            cls._custom = None
        elif cls._custom is None:
            base_class._custom = cls
        else:
            raise RuntimeError("Config object was overriden multiple times")


class Config(object):

    __metaclass__ = CustomOverride

    def _load_customizations(self):
        # Create the config directory, if it does not exist
        if not os.path.exists(self.CONFIG_DIR):
            os.mkdir(self.CONFIG_DIR)

        path = os.path.join(self.CONFIG_DIR, 'config.py')
        if os.path.exists(path):
            module_id = os.path.basename(path.rstrip('.py'))
            imp.load_source(module_id, path)

        for name, value in self._custom.__dict__.items():
            if name.isupper():
                setattr(self, name, value)

    # User's home directory. There should be no need to override this.
    HOME_DIR = os.path.expanduser('~')

    # The location of the configuration directory
    CONFIG_DIR = os.path.join(HOME_DIR, '.actor')

    # The source directory
    SOURCE_DIR = os.path.dirname(os.path.dirname(__file__))

    # The static directory
    STATIC_DIR = os.path.join(SOURCE_DIR, 'static')

    # The preferred way of logging. For systemd-based systems, use 'stdout'
    # and the Actor logging output will be available using journalctl.
    # For file-based logging, use 'file'

    LOGGING_TARGET = 'stdout'

    # The minimal logging level that should be logged. Must be one of
    # 'debug', 'info', 'warn', 'error', 'critical'.

    LOGGING_LEVEL = 'info'

    # Whether the format of the log messagess should include timestamp

    LOGGING_TIMESTAMP = False

    # File to log to if LOGGING_TARGET is set to 'file'.

    LOGGING_FILE = os.path.join(CONFIG_DIR, 'actor.log')

    # Windows spawned by the following commands should be allowed
    # to have focus in any activity

    # WHITELISTED_COMMANDS = ('konsole', 'plasma', 'krunner', 'polkit')
    WHITELISTED_COMMANDS = tuple()

    # Windows containing these titles are allowed to be used during any activity

    WHITELISTED_TITLES = tuple()

    # The following commands are terminal emulators being used

    TERMINAL_EMULATORS = ('konsole', 'xterm', 'guake', 'gnome-terminal',
                          'xfce4-terminal')

    # The timetracking interface you wish to use
    TIMETRACKER = 'timewarrior'

config = Config()
config._load_customizations()
