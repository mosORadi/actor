from actor.core.plugins import Reporter
from actor.core.util import run


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


class TaskWarriorReporterDuration(Reporter):
    """
    Returns TaskWarrior tasks matching the given filter.
    """

    identifier = 'timew_activity_duration'

    def run(self):
        stdout, stderr, code = run(['timew'])
        parts = stdout.splitlines()[3].split("Total ")

        if len(parts) > 1:
            segments = parts[1].strip().split(':')
            if len(segments) > 1:
                minutes = int(segments[1].lstrip('0') or 0)
                hours = int(segments[0].lstrip('0') or 0)

                return (hours * 60) + minutes

        return None
