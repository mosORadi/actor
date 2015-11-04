from plugins import Reporter
from util import run

from psutil import Process


class TmuxActiveSessionNameReporter(Reporter):
    """
    Returns a list of the names of the active sessions.
    """

    identifier = 'tmux_active_sessions'

    def run(self):
        output = run(['tmux',
                      'list-sessions',
                      '-F', '#{session_attached} #{session_name}'])[0]

        active_sessions = [line[2:] for line in output.splitlines()
                                    if line.startswith('1 ')]

        return active_sessions


class TmuxActiveWindowNameReporter(TmuxActiveSessionNameReporter):
    """
    Returns a list of the names of the active windows.
    """

    identifier = 'tmux_active_windows'

    def run(self):
        active_sessions = super(TmuxActiveWindowNameReporter, self).run()
        active_windows = []

        for session in active_sessions:
            output = run(
                ['tmux',
                 'list-windows',
                 '-t', session,
                 '-F', '#{window_active} #{window_name}'])[0]

            active_windows = active_windows + [line[2:]
                    for line in output.splitlines()
                    if line.startswith('1 ')]

        return active_windows


class TmuxActivePanePIDsReporter(TmuxActiveSessionNameReporter):
    """
    Returns a list of pids of the processes in the active panes.
    """

    identifier = 'tmux_active_panes_pids'

    def get_active_panes(self):
        active_sessions = super(TmuxActivePanePIDsReporter, self).run()
        active_panes = []

        for session in active_sessions:
            output = run(
                ['tmux',
                 'list-panes',
                 '-t', session,
                 '-F', '#{pane_active} #{pane_pid}'])[0]

            active_panes = active_panes + [int(line[2:])
                    for line in output.splitlines()
                    if line.startswith('1 ')]

        return active_panes

    def run(self):
        processes = []

        for pid in self.get_active_panes():
            process = Process(pid)
            processes.append(process)
            processes = processes + list(process.children())

        return [p.pid for p in processes]


class TmuxActivePaneProcessNames(Reporter):
    """
    Returns the list of names of the commands running in active panes.
    """

    identifier = 'tmux_active_panes_process_names'

    def run(self):
        return [' '.join(Process(pid).cmdline())
                for pid in self.report('tmux_active_panes_pids')]
