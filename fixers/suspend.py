import dbus

from plugins import Fixer
from util import run


class SuspendFixer(Fixer):
    """
    Simple fixer that suspends your workstation.
    """

    identifier = "suspend"
    interface = None
    optional_plugin_options = ["enforced"]

    def suspend(self):

        if not self.interface:
            bus_name = 'org.freedesktop.PowerManagement'
            object_path = '/org/freedesktop/PowerManagement'
            interface_name = bus_name

            session_bus = dbus.SessionBus()
            dbus_object = session_bus.get_object(bus_name, object_path)
            self.interface = dbus.Interface(dbus_object, interface_name)

        self.interface.Suspend()

    def suspend_forced(self):
        run(['sudo', 'pm-suspend'])

    def fix(self, **reports):
        if self.options.get('enforced'):
            self.suspend_forced()
        else:
            self.suspend()


import datetime


class SuspendUntilFixer(Fixer):
    """
    Simple fixer that suspends your workstation,
    until specified time, in %H.%M format.
    """

    identifier = "suspend_until"
    required_plugin_options = ["until"]

    def fix(self, **reports):
        until_old = datetime.datetime.strptime(str(self.options['until']), "%H.%M")
        until = datetime.datetime.combine(datetime.date.today(), until_old.time())

        if datetime.datetime.now() > until:
            until = until + datetime.timedelta(1)

        seconds_until = int((until - datetime.datetime.now()).total_seconds())
        print seconds_until
        run(['sudo', 'rtcwake', '-u', '-m', 'mem', '-s', seconds_until])
