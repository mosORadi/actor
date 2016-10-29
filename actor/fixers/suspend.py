import datetime

from actor.core.plugins import Fixer, DBusMixin
from actor.core.util import run, convert_timestamp


class SuspendFixer(DBusMixin, Fixer):
    """
    Simple fixer that suspends your workstation.
    """

    identifier = "suspend"

    bus_name = 'org.freedesktop.PowerManagement'
    object_path = '/org/freedesktop/PowerManagement'

    def run(self, enforced=False):
        # pylint: disable=arguments-differ

        if enforced:
            run(['sudo', 'pm-suspend'])
        else:
            self.interface.Suspend()


class SuspendUntilFixer(Fixer):
    """
    Simple fixer that suspends your workstation, until specified time, given
    in %H.%M format or as a datetime.time object.

    Uses rtcwake command.
    """

    identifier = "suspend_until"

    def run(self, until):
        # pylint: disable=arguments-differ

        until = convert_timestamp(until)

        if datetime.datetime.now() > until:
            until = until + datetime.timedelta(1)

        seconds_until = int((until - datetime.datetime.now()).total_seconds())
        run(['sudo', 'rtcwake', '-u', '-m', 'mem', '-s', seconds_until])
