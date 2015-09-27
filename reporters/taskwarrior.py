from plugins import IReporter
from tasklib import TaskWarrior


class TaskWarriorReporter(IReporter):

    export_as = 'tasks'
    optional_plugin_options = ['filter', 'rawfilter', 'warrior_options']

    def __init__(self, **options):
        super(TaskWarriorReporter, self).__init__(**options)
        self.task_filter = self.options.get('filter', dict())
        self.raw_filter = self.options.get('rawfilter', [])
        warrior_options = self.options.get('warrior_options', dict())
        self.warrior = TaskWarrior(**warrior_options)

    def get_tasks(self):
        return self.warrior.tasks.filter(*self.raw_filter, **self.task_filter)

    def report(self):
        return ';'.join([str(t['description']) for t in self.get_tasks()])


class TasksCompletedReporter(TaskWarriorReporter):

    export_as = 'tasks_completed'

    def get_tasks(self):
        return self.warrior.tasks.completed().filter(
                *self.raw_filter,
                **self.task_filter
        )


class TaskCountReporter(TaskWarriorReporter):

    export_as = 'task_count'

    def report(self):
        return len(self.get_tasks())
