from plugins import Reporter
import dbus


class HamsterActivityReporter(Reporter):
    activity = None

    export_as = 'hamster'

    def __init__(self, **options):
        super(HamsterActivityReporter, self).__init__(**options)
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
                # 4 - name, 6 - category
                self.activity = "%s@%s" % (last_fact[4], last_fact[6])

    def report(self):
        return str(self.activity or '')


class HamsterActivityDailyDurationReporter(Reporter):
    export_as = 'hamster_activity_daily_duration'

    def __init__(self, **options):
        super(HamsterActivityDailyDurationReporter, self).__init__(**options)
        self.bus = dbus.SessionBus()
        proxy = dbus.SessionBus().get_object(
            "org.gnome.Hamster", "/org/gnome/Hamster")
        self.hamster = dbus.Interface(proxy, dbus_interface='org.gnome.Hamster')


    def get_activity_duration(self):
        totals = {}

        for fact in self.hamster.GetTodaysFacts():
            # 4 - name
            # 6 - category
            # 9 - duration
            key = "%s@%s" % (fact[4], fact[6])

            if key in totals:
                totals[key] =+ fact[9]
            else:
                totals[key] = fact[9]

        return totals

    def report(self):
        return self.get_activity_duration()
