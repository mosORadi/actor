import os
import signal

from plugins import IFixer


class KillProcessFixer(IFixer):
    """
    Simple fixer that kills a given PID.
    """

    export_as = "kill_process"
    interface = None

    def kill(self, pid):
        os.kill(pid, signal.SIGKILL)

    def fix(self, **reports):
        if reports.get('pid'):
            pid = int(reports.get('pid'))
            self.kill(pid)
