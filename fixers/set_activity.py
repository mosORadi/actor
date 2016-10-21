import shlex
import subprocess

from plugins import Fixer, DBusMixin


class SetHamsterActivityFixer(DBusMixin, Fixer):
    """
    Simple fixer that sets current activity in Hamster.

    Accepted options (defaults in parentheses):
      - activity: Activity string as put in the Hamster (activity@Sample)
    """

    identifier = "set_hamster_activity"

    bus_name = 'org.gnome.Hamster'
    object_path = '/org/gnome/Hamster'

    def run(self, activity):
        # pylint: disable=arguments-differ
        if not self.interface:
            return

        # First, let's detect the current activity to not
        # redefine the same activity over and over
        current_activity = self.report('hamster_activity')

        # We use substring search here to support setting activity
        # of the form activity@Project, description
        # since we generate only activity@Project
        if current_activity is None or current_activity not in activity:

            # Zero stands for now
            self.interface.StopTracking(0)
            self.interface.AddFact(activity, 0, 0, False)


class StopHamsterActivityFixer(DBusMixin, Fixer):
    """
    Simple fixer that stops current activity in Hamster.
    """

    identifier = "stop_hamster_activity"

    bus_name = 'org.gnome.Hamster'
    object_path = '/org/gnome/Hamster'

    def run(self, activity):
        # pylint: disable=arguments-differ
        if not self.interface:
            return

        # Zero stands for now
        self.interface.StopTracking(0)


class SetTimewActivityFixer(Fixer):
    """
    Simple fixer, that sets current activity in Timewarrior.

    Accepted options (defaults in parentheses):
      - activity: Activity string as put to timewarrior
    """

    identifier = "timew_set"

    def run(self, activity):
        # pylint: disable=arguments-differ

        # First, let's detect the current activity to not
        # redefine the same activity over and over
        current_activity = self.report('timew_activity')

        # We use substring search here to support setting activity
        # of the form activity@Project, description
        # since we generate only activity@Project
        if current_activity is not activity:
            subprocess.call(['timew', 'start'] + shlex.split(activity))


class StopTimewActivityFixer(Fixer):
    """
    Simple fixer, that stops current activity in Timewarrior.
    """

    identifier = "timew_stop"

    def run(self):
        # pylint: disable=arguments-differ
        subprocess.call(['timew', 'stop'])
