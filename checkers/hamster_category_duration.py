from plugins import IChecker

class HamsterCategoryDailyDurationChecker(IChecker):
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
        super(HamsterActivityDailyDurationChecker, self).__init__(**options)
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
