from plugins import IReporter
from tasklib.task import TaskWarrior


class TaskDescriptionReporter(IReporter):

    export_as = 'tasks'
    optional_plugin_options = ['filter', 'warrior_options']

    def __init__(self, **options):
        super(TaskDescriptionReporter, self).__init__(**options)
        self.task_filter = self.options.get('filter', dict())

        warrior_options = self.options.get('warrior_options', dict())
        self.warrior = TaskWarrior(**warrior_options)

    def get_tasks(self):
        return self.warrior.tasks.filter(**self.task_filter)

    def report(self):
        return ';'.join([str(t['description']) for t in self.get_tasks()])
