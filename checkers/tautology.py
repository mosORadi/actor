from plugins import IChecker


class TautologyChecker(IChecker):
    """
    Simple checker that always returns true.

    Expects reports:
    None.

    Options:
    None.
    """

    def check(self, **reports):
        return True
