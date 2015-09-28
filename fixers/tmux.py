from plugins import Fixer
from util import run


class TmuxDetachFixer(Fixer):
    """
    Detaches the active tmux session.
    """

    export_as = "tmux_detach"

    def fix(self, **reports):
        run(['tmux', 'detach-client'])
