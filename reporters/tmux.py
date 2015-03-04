from plugins import IReporter
from util import run

from psutil import Process


class TmuxActiveSessionNameReporter(IReporter):

    export_as = 'tmux_active_sessions'

    def get_active_sessions(self):
        output = run(['tmux',
                      'list-sessions',
                      '-F', '#{session_attached} #{session_name}'])[0]

        active_sessions = [line[2:] for line in output.splitlines()
                                    if line.startswith('1 ')]

        return active_sessions

    def report(self, **reports):
        return ';'.join(self.get_active_sessions())


class TmuxActiveWindowNameReporter(TmuxActiveSessionNameReporter):

    export_as = 'tmux_active_windows'

    def get_active_windows(self, **reports):
        active_sessions = self.get_active_sessions()
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

    def report(self, **reports):
        return ';'.join(self.get_active_windows())


class TmuxActivePanePIDsReporter(TmuxActiveSessionNameReporter):

    export_as = 'tmux_active_panes_pids'

    def get_all_processes_in_active_panes(self):
        processes = []

        for pid in self.get_active_panes():
            process = Process(pid)
            processes.append(process)
            processes = processes + list(process.children())

        return processes

    def get_active_panes(self, **reports):
        active_sessions = self.get_active_sessions()
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

    def report(self, **reports):
        return ';'.join([str(p.pid)
            for p in self.get_all_processes_in_active_panes()])


class TmuxActivePaneProcessNames(TmuxActivePanePIDsReporter):

    export_as = 'tmux_active_panes_process_names'

    def report(self, **reports):
        return ';'.join([' '.join(p.cmdline())
            for p in self.get_all_processes_in_active_panes()])
