from plugins import Reporter
from tasklib import TaskWarrior


class TaskWarriorReporter(Reporter):
    """
    Returns TaskWarrior tasks matching the given filter.
    """

    identifier = 'tasks'

    def run(self, warrior_options=None, rawfilter=None, taskfilter=None):
        # pylint: disable=arguments-differ

        warrior_options = warrior_options or dict()
        taskfilter = taskfilter or dict()
        rawfilter = rawfilter or tuple()

        warrior = TaskWarrior(**warrior_options)
        tasks = warrior.tasks.filter(*rawfilter, **taskfilter)

        return tasks
