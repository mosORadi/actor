from plugins import IReporter
import dbus


class HamsterActivityReporter(IReporter):
    activity = None

    def __init__(self):
        super(IReporter, self).__init__()
        self.bus = dbus.SessionBus()
        self.bus.add_signal_receiver(
            self.get_current_activity,
            dbus_interface="org.gnome.Hamster",
            signal_name="FactsChanged")

        proxy = dbus.SessionBus().get_object(
            "org.gnome.Hamster", "/org/gnome/Hamster")
        self.hamster = dbus.Interface(proxy, dbus_interface='org.gnome.Hamster')

        # Initialize the activity value
        self.get_current_activity()

    def get_current_activity(self):
        today_facts = self.hamster.GetTodaysFacts()

        # See to_dbus_fact method in src/hamster-service
        if today_facts:
            last_fact = today_facts[-1]
            if last_fact[2] == 0:    # 2 - end_time, set to 0 for ongoing facts
                self.activity = last_fact[4]    # 4 - name

    def report(self):
        return self.activity
