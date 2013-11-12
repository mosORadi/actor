from yapsy.IPlugin import IPlugin


class IReporter(IPlugin):
    """Reports user activity to the AcTor"""
    def __init__(self, **options):
        self.options = options

    def report(self):
        """Returns user activity value"""
        pass


class IChecker(IPlugin):
    """Evaluates user activity depending on the input from the responders"""

    def __init__(self, **options):
        self.options = options

    def check(self, **reports):
        """
        Returns evaluation of the situation - true or false, accorgding
        to the input from the reporters, passed to the check function,
        and custom logic of Checker itself.

        This function should return a dictionary, with mandatory key result
        which holds the value of the check itself, and any optional keys that
        are then passed to the fixer.
        """
        pass


class IFixer(IPlugin):
    def __init__(self, **options):
        self.options = options

    def fix(self, **data):
        """
        This function does execute the given action.
        """

        pass
