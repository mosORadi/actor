import datetime
import dbus
import logging
import itertools
import psutil

import local_config


logger = logging.getLogger('main')


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class Plugin(object):

    def __init__(self, context):
        self.context = context

    # Logging-related helpers
    def log(self, log_func, message):
        log_func("%s: %s" % (self.__class__.__name__, message))

    def debug(self, message):
        self.log(logger.debug, message)

    def info(self, message):
        self.log(logger.info, message)

    def warning(self, message):
        self.log(logger.warning, message)

    def error(self, message):
        self.log(logger.error, message)

    def critical(self, message):
        self.log(logger.critical, message)

    # Convenience function for accessing worker modules
    def report(self, identifier, *args, **kwargs):
        return self.context.reporters.get(identifier, args, kwargs)

    def check(self, identifier, *args, **kwargs):
        return self.context.checkers.get(identifier, args, kwargs)

    def fix(self, identifier, *args, **kwargs):
        return self.context.fixers.get(identifier, args, kwargs)

    def factory_report(self, identifier, *args, **kwargs):
        return self.context.reporter_factory.make(identifier, args, kwargs)

    def factory_check(self, identifier, *args, **kwargs):
        return self.context.checker_factory.make(identifier, args, kwargs)

    def factory_fix(self, identifier, *args, **kwargs):
        return self.context.fixer_factory.make(identifier, args, kwargs)

    # Make sure every plugin implements the run method
    def run(self):
        raise NotImplementedError("The run method needs to be"
            "implemented by the plugin itself")


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

    def __bool__(self):
        return self.run()


class Fixer(Worker):
    """
    Performs a custom action on the machine.
    """

    side_effects = True

    __metaclass__ = PluginMount


class ContextProxyMixin(object):
    """
    Provides a simplified interface to the workers exposed by the context.
    """

    @property
    def identifier(self):
        return self.__class__.__name__

    def report(self, identifier, *args, **kwargs):
        return self.context.reporters.get(identifier, args, kwargs,
                                          rule_name=self.identifier)

    def check(self, identifier, *args, **kwargs):
        return self.context.checkers.get(identifier, args, kwargs,
                                         rule_name=self.identifier)

    def fix(self, identifier, *args, **kwargs):
        return self.context.fixers.get(identifier, args, kwargs,
                                       rule_name=self.identifier)

class PythonRule(ContextProxyMixin, Plugin):
    """
    Performs custom rule.
    """

    __metaclass__ = PluginMount


class DBusMixin(object):
    """
    Sets the interface of the specified DBus object as self.interface. In case
    DBusException occurs during setup, self.interface is set to None.
    """

    bus_name = None        # i.e. 'org.freedesktop.PowerManagement'
    object_path = None     # i.e.'/org/freedesktop/PowerManagement'
    interface_name = None  # can be omitted, and bus_name will be used instead

    def __init__(self, *args, **kwargs):
        super(DBusMixin, self).__init__(*args, **kwargs)

        try:
            self.bus = dbus.SessionBus()
            dbus_object = self.bus.get_object(self.bus_name, self.object_path)
            self.interface = dbus.Interface(dbus_object,
                                            self.interface_name or self.bus_name)
        except dbus.exceptions.DBusException:
            self.interface = None


class Activity(ContextProxyMixin, Plugin):

    __metaclass__ = PluginMount

    blacklisted_commands = tuple()
    whitelisted_commands = tuple()
    whitelisted_titles = tuple()

    notification = None
    notification_timeout = 30000
    notification_headline = "Actor"

    hamster_activity = None

    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)

        # Run initial setup for the activity
        self.setup()

    def setup(self):
        """
        Performs the tasks related to the activity setup.
        - Displays the activity instructions.
        """

        # Issue a setup notification
        if self.notification:
            self.fix('notify', message=self.notification,
                     timeout=self.notification_timeout,
                     headline=self.notification_headline)

        # Setup the current activity in the Hamster Time Tracker
        if self.hamster_activity:
            self.info("Setting the activity: %s" % self.hamster_activity)
            self.fix('set_hamster_activity', activity=self.hamster_activity)

        # Get the list of all allowed commands / titles by joining
        # the allowed values from the class with the global values from the
        # settings
        self.whitelisted_commands = (self.whitelisted_commands +
                                     local_config.WHITELISTED_COMMANDS)

        self.whitelisted_titles = (self.whitelisted_titles +
                                   local_config.WHITELISTED_TITLES)

    def run(self):
        """
        Performs the periodic activity validation.
        - Enforces the allowed applications.
        """

        # Detect the current running process / window title
        current_title = self.report('active_window_name')
        current_command = self.report('active_window_process_name')

        if current_command is None or current_title is None:
            return

        # If no of the whitelisted entries partially matches the reported
        # window command / title, user will have to face the consenquences
        if not any([t in current_title for t in self.whitelisted_titles] +
                   [c in current_command for c in self.whitelisted_commands]):
            self.fix('notify', message="Application not allowed")
            self.fix('kill_process', pid=self.report('active_window_pid'))

        # If we're running terminal emulator, we need to get inside
        # the emulator to detect what is actually being run inside
        emulator_processes = []

        if any([e in current_command
                for e in local_config.TERMINAL_EMULATORS]):

            active_window_process = self.report('active_window_process')

            if active_window_process:
                emulator_processes = active_window_process.children(recursive=True)

                # If we're running tmux, the commands are being executed
                # under tmux server instead
                if any(['tmux' in ' '.join(e.cmdline())
                        for e in emulator_processes]):

                    emulator_processes = list(itertools.chain(*[
                        psutil.Process(pane_pid).children(recursive=True)
                        for pane_pid in self.report('tmux_active_panes_pids')
                    ]))

                # If the active window is a terminal emulator, perform
                # selective blacklisting of the spawned applications
                for process in emulator_processes:
                    command = ' '.join(process.cmdline())
                    if any([b in command for b in self.blacklisted_commands]):
                        process.kill()


class Flow(ContextProxyMixin, Plugin):
    """
    Defines a list of activities with their duration.
    """

    __metaclass__ = PluginMount

    activities = tuple()

    def __init__(self, context, actor):
        self.context = context
        self.actor = actor
        self.current_activity_index = None
        self.current_activity_start = None

    @property
    def next_activity(self):
        try:
            return self.activities[(self.current_activity_index or 0) + 1]
        except IndexError:
            return None

    @property
    def current_activity(self):
        return self.activities[self.current_activity_index]

    @property
    def current_activity_expired(self):
        duration = datetime.timedelta(minutes=self.current_activity[1])
        end_time = self.current_activity_start + duration

        return datetime.datetime.now() > end_time

    def start(self, activity):
        self.current_activity_start = datetime.datetime.now()
        self.actor.set_activity(activity[0], force=True)

    def end(self):
        self.actor.unset_activity(force=True)
        self.current_activity_start = None

    def run(self):
        if self.current_activity_index is None:
            self.current_activity_index = 0
            self.start(self.current_activity)
        elif self.current_activity_expired and self.next_activity is not None:
            self.end()
            self.current_activity_index =+ 1
            self.start(self.current_activity)
        elif self.current_activity_expired and self.next_activity is None:
            self.end()
            self.actor.unset_flow()
