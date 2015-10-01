import datetime
import dbus

from plugins import Fixer
from util import run, convert_timestamp


class SuspendFixer(Fixer):
    """
    Simple fixer that suspends your workstation.
    """

    identifier = "suspend"

    def __init__(self, context):
        super(SuspendFixer, self).__init__(context)

        bus_name = 'org.freedesktop.PowerManagement'
        object_path = '/org/freedesktop/PowerManagement'
        interface_name = bus_name

        session_bus = dbus.SessionBus()
        dbus_object = session_bus.get_object(bus_name, object_path)
        self.interface = dbus.Interface(dbus_object, interface_name)

    def run(self, enforced=False):
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
        until = convert_timestamp(until)

        if datetime.datetime.now() > until:
            until = until + datetime.timedelta(1)

        seconds_until = int((until - datetime.datetime.now()).total_seconds())
        run(['sudo', 'rtcwake', '-u', '-m', 'mem', '-s', seconds_until])
