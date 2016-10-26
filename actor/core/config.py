import os


class Config(object):

    # User's home directory. There should be no need to override this.
    HOME_DIR = os.path.expanduser('~')

    # The location of the configuration directory
    CONFIG_DIR = os.path.join(HOME_DIR, '.actor')

    # Any process that shares the user session you are accessing. This is
    # here to provide a workaround so that actor can connect to your
    # dbus session bus, it reads the environment variable of DBUS
    # session bus from environment of the desktop process configured here.
    # For KDE users, good desktop process plasma-desktop.

    DESKTOP_PROCESS = "plasma-desktop"

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
