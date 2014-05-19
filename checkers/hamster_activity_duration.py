from plugins import IChecker

class HamsterActivityDailyDurationChecker(IChecker):
    """
    Checks whether a time limit for a particular activity has not been
    exceeded.

    Expects reports:
      - hamster_activity_daily_duration - Input dictionary of summary of
                                          activity duration

    Options:
      - limit : The activity duration limit, in minutes
      - activity: The activity that should be measured, in the form of activity@Category
    """

    export_as = 'hamster_activity_duration'
    required_plugin_options = ['limit', 'activity']

    def __init__(self, **options):
        super(HamsterActivityDailyDurationChecker, self).__init__(**options)
        self.activity = self.options.get('activity')
        self.limit = self.options.get('limit', 0) * 60

        if not self.activity:
            raise ValueError("You must specify the activity option for HamsterActivityDailyDurationChecker")
        if not self.limit:
            raise ValueError("You must specify the limit option for HamsterActivityDailyDurationChecker")

    def check(self, **reports):
        duration = reports['hamster_activity_daily_duration'].get(self.activity, 0)
        
        return duration > self.limit
