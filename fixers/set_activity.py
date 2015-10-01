import dbus

from plugins import Fixer


class SetHamsterActivityFixer(Fixer):
    """
    Simple fixer, that sets current activity in Hamster.

    Accepted options (defaults in parentheses):
      - activity: Activity string as put in the Hamster (activity@Sample)
    """

    identifier = "set_hamster_activity"

    bus_name = 'org.gnome.Hamster'
    object_path = '/org/gnome/Hamster'
    interface_name = bus_name

    def __init__(self, context):
        super(SetHamsterActivityFixer, self).__init__(context)

        self.bus = dbus.SessionBus()
        dbus_object = self.bus.get_object(self.bus_name, self.object_path)
        self.interface = dbus.Interface(dbus_object, self.interface_name)

    def run(self, activity):
        # First, let's detect the current activity to not
        # redefine the same activity over and over
        current_activity = self.report('hamster_activity') or ''

        # We use substring search here to support setting activity
        # of the form activity@Project, description
        # since we generate only activity@Project
        if current_activity not in activity:

            # Zero stands for now
            self.interface.StopTracking(0)
            self.interface.AddFact(activity, 0, 0, False)
