from plugins import IChecker


class TautologyChecker(IChecker):
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
