from plugins import IReporter
import dbus


class HamsterActivityDailyDurationReporter(IReporter):
    export_as = 'hamster_activity_daily_duration'

    def __init__(self, **options):
        super(IReporter, self).__init__(**options)
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
