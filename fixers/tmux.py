from plugins import IFixer
from util import run


class TmuxDetachFixer(IFixer):
    """
    Detaches the active tmux session.
    """

    export_as = "tmux_detach"

    def fix(self, **reports):
        run(['tmux', 'detach-client'])
