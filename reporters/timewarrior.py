from plugins import Reporter
from util import run


class TaskWarriorReporter(Reporter):
    """
    Returns TaskWarrior tasks matching the given filter.
    """

    identifier = 'timew_activity'

    def run(self):
        stdout, stderr, code = run(['timew'])
        parts = stdout.splitlines()[0].split("Tracking ")

        if len(parts) > 1:
            return parts[1].strip()
        else:
            return None
