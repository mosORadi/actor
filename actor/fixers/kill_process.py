import os
import signal

from plugins import Fixer


class KillProcessFixer(Fixer):
    """
    Simple fixer that kills a given PID.
    """

    identifier = "kill_process"

    def kill(self, pid):
        os.kill(pid, signal.SIGKILL)

    def run(self, pid):
        # pylint: disable=arguments-differ

        if pid is not None:
            pid = int(pid)
            self.kill(pid)
