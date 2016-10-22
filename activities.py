import datetime
import itertools
import psutil

import config
import util
from plugins import Plugin, PluginMount, ContextProxyMixin

# Define own our commands so that we don't kill ourselves under
# any circumstances
ACTOR_COMMANDS = ('actor', 'actor-desktop')

class ActivityTimetrackingMixin(object):

    timetracking_id = None

    def setup_timetracking(self):
        # Setup the current activity in the Hamster Time Tracker
        if self.timetracking_id:
            self.info("Setting the activity: %s" % self.timetracking_id)
            self.timetracking.start(self.timetracking_id)

class ActivityNotificationMixin(object):

    notification = None
    notification_timeout = 30000
    notification_headline = "Actor"

    def setup_notification(self):
        # Issue a setup notification
        if self.notification:
            self.fix('notify', message=self.notification,
                     timeout=self.notification_timeout,
                     headline=self.notification_headline)

class ActivityApplicationEnforcementMixin(object):

    blacklisted_commands = tuple()
    whitelisted_commands = tuple()
    whitelisted_titles = tuple()

    def setup_application_enforcement(self):
        # Get the list of all allowed commands / titles by joining
        # the allowed values from the class with the global values from the
        # settings
        self.whitelisted_commands = (self.whitelisted_commands +
                                     ACTOR_COMMANDS +
                                     config.WHITELISTED_COMMANDS)

        self.whitelisted_titles = (self.whitelisted_titles +
                                   config.WHITELISTED_TITLES)

    def run_application_efnrocement(self):
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
                for e in config.TERMINAL_EMULATORS]):

            active_window_process = self.report('active_window_process')

            if active_window_process:
                emulator_processes = active_window_process.children(
                    recursive=True)

                # If we're running tmux, the commands are being executed
                # under tmux server instead
                if any(['tmux' in ' '.join(e.cmdline())
                        for e in emulator_processes]):

                    emulator_processes = list(itertools.chain(*[
                        psutil.Process(pane_pid).children(recursive=True)
                        for pane_pid in self.report('tmux_active_panes_pids')
                        if psutil.pid_exists(pane_pid)
                    ]))

                # If the active window is a terminal emulator, perform
                # selective blacklisting of the spawned applications
                for process in emulator_processes:
                    try:
                        command = ' '.join(process.cmdline())
                        if any([forbidden in command
                                for forbidden in self.blacklisted_commands]):
                            process.kill()
                    except psutil.NoSuchProcess:
                        # If process ended in the mean time, ignore it
                        pass

class AcitivityStartupCommandsMixin(object):

    startup_commands = tuple()

    def setup_startup_commands(self):

        # Execute the startup commands
        for command in self.startup_commands:
            util.run_async(command)

class Activity(ActivityTimetrackingMixin,
               ActivityNotificationMixin,
               ActivityApplicationEnforcementMixin,
               ContextProxyMixin, Plugin):

    __metaclass__ = PluginMount

    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)

        self.setup_methods = []
        self.run_methods = []

        # Collect the setup and run methods in the order of the base classes
        for cls in Activity.__bases__:
            self.setup_methods += [getattr(self, method) for method in dir(cls)
                                   if method.startswith('setup_')]
            self.run_methods += [getattr(self, method) for method in dir(cls)
                                 if method.startswith('run_')]


        # Run initial setup for the activity
        self.setup()

    def setup(self):
        # Perform actual setup
        for setup_method in self.setup_methods:
            setup_method()

    def run(self):
        # Execute all the run methods
        for run_method in self.run_methods:
            run_method()


class AfkActivity(Activity):
    """
    Implements a non-tracked activity that should occur away from
    keyboard. Desktop is blocked using a overlay window.
    """

    noplugin = True
    header = None
    message = None

    def setup(self):
        # Setup the current activity in the Hamster Time Tracker
        if self.timetracking_id:
            self.info("Setting the activity: %s" % self.timetracking_id)
            self.timetracking.start(self.timetracking_id)

        self.overlay = self.factory_fix('overlay')

    def run(self):
        value = self.overlay.evaluate(message=self.message, header=self.header)

        if value is None:
            return

        self.overlay.reset()

        # TODO: Handle activity teardown more gracefully
        self.context.activity = None


class AfkTrackedActivity(Activity):
    """
    Implements a input-terminated activity that should occur away from
    keyboard. Desktop is blocked using a overlay window.
    """

    noplugin = True
    header = None
    message = None

    def setup(self):
        # Setup the current activity in the Hamster Time Tracker
        if self.timetracking_id:
            self.info("Setting the activity: %s" % self.timetracking_id)
            self.timetracking.start(self.timetracking_id)

        self.overlay = self.factory_fix('overlay')

    @property
    def key(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def run(self):
        value = self.overlay.evaluate(message=self.message, header=self.header)

        if value is None:
            return

        self.fix(
            'track',
            ident=self.identifier,
            key=self.key,
            value=value
        )

        self.overlay.reset()

        # TODO: Handle activity teardown more gracefully
        self.context.activity = None


class Flow(ContextProxyMixin, Plugin):
    """
    Defines a list of activities with their duration.
    """

    __metaclass__ = PluginMount

    activities = tuple()

    def __init__(self, context, actor):
        super(Flow, self).__init__(context)

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
        # If the activity is no longer set, consider it expired
        if self.context.activity is None:
            return True

        # Otherwise check if the time allocated ran out
        duration = datetime.timedelta(minutes=self.current_activity[1])
        end_time = self.current_activity_start + duration

        return datetime.datetime.now() > end_time

    def start(self, activity):
        self.current_activity_start = datetime.datetime.now()
        self.actor.set_activity(activity[0], force=True)

    def end(self):
        self.actor.unset_activity(force=True)
        self.current_activity_start = None

    def start_next_activity(self):
        self.end()

        if self.next_activity is not None:
            self.current_activity_index += 1
            self.start(self.current_activity)
        else:
            self.actor.unset_flow()

    def run(self):
        if self.current_activity_index is None:
            self.current_activity_index = 0
            self.start(self.current_activity)
        elif self.current_activity_expired:
            self.start_next_activity()
