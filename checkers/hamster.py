from plugins import Checker

class HamsterActivityDailyDurationChecker(Checker):
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


class HamsterCategoryDailyDurationChecker(Checker):
    """
    Checks whether a time limit for a particular activity has not been
    exceeded.

    Expects reports:
      - hamster_activity_daily_duration - Input dictionary of summary of
                                          activity duration

    Options:
      - limit : The activity duration limit, in minutes
      - category: The activity that should be measured, in the form of 'Category'
    """

    export_as = 'hamster_category_duration'
    required_plugin_options = ['limit', 'category']

    def __init__(self, **options):
        super(HamsterCategoryDailyDurationChecker, self).__init__(**options)
        self.category = self.options.get('category')
        self.limit = self.options.get('limit', 0) * 60

        if not self.category:
            raise ValueError("You must specify the activity option for HamsterCategoryDailyDurationChecker")
        if not self.limit:
            raise ValueError("You must specify the limit option for HamsterCategoryDailyDurationChecker")

    def check(self, **reports):
        category_duration = 0
        activities = reports['hamster_activity_daily_duration'].iteritems()

        for activity, duration in activities:
            if activity.endswith(self.category):
                category_duration =+ duration

        return category_duration > self.limit
