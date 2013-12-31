import dbus

from plugins import IFixer


class SetHamsterActivityFixer(IFixer):
    """
    Simple fixer, that sets current activity in Hamster.

    Accepted options (defaults in parentheses):
      - activity: Activity string as put in the Hamster (activity@Sample)
    """

    export_as = "set_hamster_activity"

    bus_name = 'org.gnome.Hamster'
    object_path = '/org/gnome/Hamster'
    interface_name = bus_name

    def __init__(self, **options):
        super(SetHamsterActivityFixer, self).__init__(**options)
        self.bus = dbus.SessionBus()
        dbus_object = self.bus.get_object(self.bus_name, self.object_path)
        self.interface = dbus.Interface(dbus_object, self.interface_name)

    def is_already_set(self):
        facts = self.interface.GetTodaysFacts()
        last_fact = facts[-1] if facts else None

        last_fact_string = "%s@%s" % (last_fact[4], last_fact[6])

        # We use substring search here to support setting activity of the form
        # activity@Project, description
        # since we generate only activity@Project
        return last_fact_string in self.options.get('activity', '')

    def set_activity(self):
        activity = self.options.get('activity', 'activity@Sample')

        if not self.is_already_set():
            # Zero stands for now
            self.interface.StopTracking(0)
            self.interface.AddFact(activity, 0, 0, False)

    def fix(self, **reports):
        self.set_activity()
