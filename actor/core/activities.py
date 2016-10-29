import datetime
import itertools
import psutil
import subprocess

import util
from plugins import Plugin, PluginMount, ContextProxyMixin
from config import config

# Define own our commands so that we don't kill ourselves under
# any circumstances
ACTOR_COMMANDS = ('actor', 'actor-desktop')


class ActivityTimetrackingMixin(object):

    timetracking_id = None

    def active(self):
        return self.timetracking_id is not None

    def setup(self):
        # Setup the current activity in the Hamster Time Tracker
        if self.timetracking_id:
            self.info("Setting the activity: %s" % self.timetracking_id)
            self.timetracking.start(self.timetracking_id)


class ActivityNotificationMixin(object):

    notification = None
    notification_timeout = 30000
    notification_headline = "Actor"

    def active(self):
        return self.notification is not None

    def setup(self):
        # Issue a setup notification
        if self.notification:
            self.fix('notify', message=self.notification,
                     timeout=self.notification_timeout,
                     headline=self.notification_headline)


class ActivityApplicationEnforcementMixin(object):

    blacklisted_commands = tuple()
    whitelisted_commands = tuple()
    whitelisted_titles = tuple()

    def active(self):
        return any([self.blacklisted_commands,
                    self.whitelisted_commands,
                    self.whitelisted_titles])

    def setup(self):
        # Get the list of all allowed commands / titles by joining
        # the allowed values from the class with the global values from the
        # settings
        self.whitelisted_commands = (self.whitelisted_commands +
                                     ACTOR_COMMANDS +
                                     config.WHITELISTED_COMMANDS)

        self.whitelisted_titles = (self.whitelisted_titles +
                                   config.WHITELISTED_TITLES)

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

    def active(self):
        return self.startup_commands is not None

    def setup(self):

        # Execute the startup commands
        for command in self.startup_commands:
            util.run_async(command)


class ActivityOverlayMixin(object):
    """
    Implements a non-tracked activity that should occur away from
    keyboard. Desktop is blocked using a overlay window.
    """

    overlay_header = None
    overlay_message = None

    def active(self):
        return any([self.overlay_header, self.overlay_message])

    def setup(self):
        self.overlay = self.factory_fix('overlay')

    def run(self):
        value = self.overlay.evaluate(message=self.overlay_message,
                                      header=self.overlay_header)

        if value is None:
            return

        self.overlay.reset()

        # TODO: Handle activity teardown more gracefully
        self.context.activity = None


class ActivityTrackingOverlayMixin(object):
    """
    Implements a input-terminated activity that should occur away from
    keyboard. Desktop is blocked using a overlay window.
    """

    tracking_overlay_header = None
    tracking_overlay_message = None

    def active(self):
        return any([self.tracking_overlay_header,
                    self.tracking_overlay_message])

    def setup(self):
        self.overlay = self.factory_fix('overlay')

    def run(self):
        value = self.overlay.evaluate(message=self.tracking_overlay_message,
                                      header=self.tracking_overlay_header)

        if value is None:
            return

        key = datetime.datetime.now().strftime("%Y-%m-%d")

        self.fix(
            'track',
            ident=self.identifier,
            key=key,
            value=value
        )

        self.overlay.reset()

        # TODO: Handle activity teardown more gracefully
        self.context.activity = None


class ActivityProgressNotificationMixin(object):

    """
    Notifies user when activities are about to be changed.
    """

    progress_notifications = False
    progress_checkpoints = [0.5, 0.25, 0.1]

    def active(self):
        return self.progress_notifications is not False

    def setup(self):
        # Create a copy of progress checkpoints to use for this
        # activity only
        self.checkpoints_to_notify = list(self.progress_checkpoints)

    def run(self):
        # If there are no remaining checkpoints, we have nothing
        # to do
        if not self.checkpoints_to_notify:
            return

        relative_remaining = self.expired.remaining / self.expired.duration
        closest_checkpoint = self.checkpoints_to_notify[0]

        if relative_remaining < closest_checkpoint:
            # Pop the list of remaining checkpoints
            self.checkpoints_to_notify = self.checkpoints_to_notify[1:]

            # Notify
            message = ("Less than {0}% time for current activity remaining."
                       .format(closest_checkpoint * 100))

            self.fix('notify', message=message, timeout=10000,
                     headline="Actor")


class ActivityBackgroundMusicMixin(object):
    """
    Plays activity specific music in the background.
    Restricts playback to headphones only if required.
    """

    background_music_path = None
    background_music_headphones_required = True

    def active(self):
        return self.background_music_path is not None

    def setup(self):
        args = ['mplayer', self.background_music_path]
        self.music_process = subprocess.Popen(args)

    def run(self):
        if self.background_music_headphones_required:
            if not self.report('headphones_plugged'):
                self.music_process.kill()


class Activity(ActivityTimetrackingMixin,
               ActivityNotificationMixin,
               ActivityApplicationEnforcementMixin,
               ActivityOverlayMixin,
               ActivityTrackingOverlayMixin,
               ActivityProgressNotificationMixin,
               ActivityBackgroundMusicMixin,
               ContextProxyMixin, Plugin):

    __metaclass__ = PluginMount

    def __init__(self, context, time_limit=None):
        super(Activity, self).__init__(context)

        self.expired = util.Expiration(time_limit) if time_limit else None

        self.setup_methods = []
        self.run_methods = []

        # Determine which mixins are active according to attributes
        # set on this class by the user
        active_mixins = [cls for cls in Activity.__bases__
                         if 'active' in dir(cls) and cls.active(self)]

        # Collect the setup and run methods of the active mixins
        self.setup_methods = [cls.setup for cls in active_mixins
                              if getattr(cls, 'setup', None) is not None]
        self.run_methods = [cls.run for cls in active_mixins
                            if getattr(cls, 'run', None) is not None]

        # Run initial setup for the activity
        self.setup()

    def setup(self):
        # Perform actual setup
        for setup_method in self.setup_methods:
            setup_method(self)

    def run(self):
        # Check if the activity should still live
        if self.expired:
            self.context.unset_activity()

        # Execute all the run methods
        for run_method in self.run_methods:
            run_method(self)


class ActivitySpec(object):

    def __init__(self, identifier, duration, max_shrinking, priority=1):

        self.identifier = identifier
        self.duration = duration
        self.max_shrinking = max_shrinking
        self.priority = priority
        self.shrinking = 1.0
        self.skipped = False

    @property
    def planned_duration(self):
        return self.duration * self.shrinking

    def __repr__(self):
        return "{0}, duration {1}, shrinking {2} (max {3}), skipped: {4}".format(
                self.identifier, self.duration, self.shrinking, self.max_shrinking, self.skipped)


class Flow(ContextProxyMixin, Plugin):
    """
    Defines a list of activities with their duration.
    """

    __metaclass__ = PluginMount

    activities = tuple()

    def __init__(self, context, time_limit=None):
        super(Flow, self).__init__(context)

        self.current_activity_index = None
        self.time_limit = time_limit
        self.plan = self.generate_plan()

        self.info("====== generated plan =======")
        self.info('\n'.join(map(repr, self.plan)))

    def generate_plan(self):
        if not self.time_limit:
            return self.activities

        planned_activities = [ActivitySpec(*a) for a in self.activities]
        time_deficit = None

        while True:
            planned_activities = [a for a in planned_activities if not a.skipped]
            time_required = sum([a.duration * a.shrinking for a in planned_activities])

            if time_required == 0:
                raise Exception("Not enough time to initialize the flow.")

            # Note: time_deficit may be negative, corresponding to
            # prolonging intervals after a activity has been skipped
            time_deficit = time_required - self.time_limit

            # Allow deviations from desired time of magnitude 0.3s
            if abs(time_deficit) <= 0.005:
                break

            # First try to shrink durations to erase the time deficit
            something_shrinked = False
            shrink_factor = 1 - (float(time_deficit) / time_required)

            for activity in planned_activities:
                proposed_shrinking = activity.shrinking * shrink_factor

                if proposed_shrinking >= activity.max_shrinking:
                    activity.shrinking = proposed_shrinking
                    something_shrinked = True

            # If we're not able to shrink any duration, we need to start skipping
            if not something_shrinked:
                # Skip activity with lowest priority
                # (in case of tie, lower max shrinking activity is skipped)

                activity = min(planned_activities,
                               key=lambda a: (a.priority, a.max_shrinking))
                activity.skipped = True

        return planned_activities

    @property
    def current_activity(self):
        return self.plan[self.current_activity_index]

    def start(self, activity):
        self.context.set_activity(activity.identifier,
                                  activity.planned_duration)

    def start_next_activity(self):
        if self.current_activity_index is None:
            self.current_activity_index = 0
            self.start(self.current_activity)
        elif self.current_activity_index + 1 < len(self.activities):
            self.current_activity_index += 1
            self.start(self.current_activity)
        else:
            self.context.unset_flow()

    def run(self):
        if self.context.activity is None:
            self.start_next_activity()
