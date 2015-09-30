import os
import signal

from plugins import Fixer


class KillProcessFixer(Fixer):
    """
    Simple fixer that kills a given PID.
    """

    identifier = "kill_process"
    interface = None

    def kill(self, pid):
        os.kill(pid, signal.SIGKILL)

    def fix(self, **reports):
        if reports.get('pid'):
            pid = int(reports.get('pid'))
            self.kill(pid)
