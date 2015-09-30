from plugins import Checker


class TautologyChecker(Checker):
    """
    Simple checker that always returns true.

    Expects reports:
        None.

    Options:
        None.
    """

    identifier = 'tautology'

    def check(self, **reports):
        return True
