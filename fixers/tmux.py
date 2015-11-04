from plugins import Fixer
from util import run


class TmuxDetachFixer(Fixer):
    """
    Detaches the active tmux session.
    """

    identifier = "tmux_detach"

    def run(self):
        run(['tmux', 'detach-client'])


class TmuxKillActivePaneFixer(Fixer):
    """
    Returns a list of pids of the processes in the active panes.
    """

    identifier = 'tmux_kill_active_pane'

    def get_active_panes(self):
        active_sessions = self.report('tmux_active_sessions')
        active_pane_ids = []

        for session in active_sessions:
            output = run(
                ['tmux',
                 'list-panes',
                 '-t', session,
                 '-F', '#{pane_active} #{pane_id}'])[0]

            active_pane_ids = active_pane_ids + [line[2:]
                    for line in output.splitlines()
                    if line.startswith('1 ')]

        return active_pane_ids

    def run(self):
        for pane_id in self.get_active_panes():
            run(['tmux', 'kill-pane', '-t', pane_id])
