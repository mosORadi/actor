from yapsy.IPlugin import IPlugin


class IReporter(IPlugin):
    """Reports user activity to the AcTor"""

    def report(self):
        """Returns user activity key"""
        pass

