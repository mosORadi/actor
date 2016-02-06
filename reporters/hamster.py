from plugins import Reporter, DBusMixin


class HamsterActivityReporter(DBusMixin, Reporter):
    """
    Reports the current activity, as set in Hamster Time Tracker.

    Returns the current activity name in the format 'activity@category',
    or None if no activity was detected.
    """

    identifier = 'hamster_activity'

    bus_name = "org.gnome.Hamster"
    object_path = "/org/gnome/Hamster"

    def run(self):
        activity = None

        today_facts = self.interface.GetTodaysFacts()

        # See to_dbus_fact method in src/hamster-service
        if today_facts:
            last_fact = today_facts[-1]
            if last_fact[2] == 0:    # 2 - end_time, set to 0 for ongoing facts
                # 4 - name, 6 - category
                activity = "%s@%s" % (last_fact[4], last_fact[6])

        return activity


class HamsterActivityDailyDurationReporter(Reporter):
    """
    Reports the cummulative time spent in a particular given activity,
    as tracked by Hamster Time Tracker.

    Returns the total time in minutes as float.
    """

    identifier = 'hamster_activity_daily_duration'

    bus_name = "org.gnome.Hamster",
    object_path = "/org/gnome/Hamster"

    def run(self, activity=None):
        # pylint: disable=arguments-differ

        totals = dict()

        for fact in self.interface.GetTodaysFacts():
            # 4 - name
            # 6 - category
            # 9 - duration
            key = "%s@%s" % (fact[4], fact[6])

            if key in totals:
                totals[key] = + fact[9] / 60.0
            else:
                totals[key] = fact[9] / 60.0

        if activity is not None:
            return totals.get(activity, 0.0)
        else:
            return totals
