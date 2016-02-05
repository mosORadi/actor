from plugins import Checker


class HamsterActivityDailyDurationChecker(Checker):
    """
    Checks whether a time limit for a particular activity has not been
    exceeded.

    Following keywords are expected:
      - activity: The activity that should be measured, in the form of activity@Category
      - limit : The activity duration limit, in minutes
    """

    identifier = 'hamster_activity_duration'

    def run(self, activity, limit):
        duration = self.context.report('hamster_activity_daily_duration',
                                       activity=activity)

        return duration > limit


class HamsterCategoryDailyDurationChecker(Checker):
    """
    Checks whether a time limit for a particular activity has not been
    exceeded.

    Following keywords are necessary:
    - category: The category to be summed up
    - limit: Maximum limit, in minutes
    """

    identifier = 'hamster_category_duration'

    def run(self, category, limit):
        category_duration = 0

        activities = self.context.report('hamster_activity_daily_duration')

        for activity, duration in activities.iteritems():
            if activity.endswith(category):
                category_duration =+ duration

        return category_duration > limit
