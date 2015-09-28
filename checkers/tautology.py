from plugins import Checker


class TautologyChecker(Checker):
    """
    Simple checker that always returns true.

    Expects reports:
        None.

    Options:
        None.
    """

    export_as = 'tautology'

    def check(self, **reports):
        return True
