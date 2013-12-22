from yapsy.IPlugin import IPlugin


class IReporter(IPlugin):
    """Reports user activity to the AcTor"""

    export_as = None

    def setup(self, **options):
        if 'export_as' in options:
            assert type(options['export_as']) == str
            self.export_as = options['export_as']
            del options['export_as']

        assert self.export_as is not None
        self.options = options

    def report(self):
        """Returns user activity value"""
        pass


class IChecker(IPlugin):
    """Evaluates user activity depending on the input from the responders"""

    def setup(self, **options):
        if 'export_as' in options:
            assert type(options['export_as']) == str
            self.export_as = options['export_as']
            del options['export_as']

        assert self.export_as is not None

        self.options = options


    def check(self, *reports):
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

    def setup(self, **options):
        """
        The triggered_by option must be passed via the framework.
        """

        assert 'triggered_by' in options
        self.triggered_by = options['triggered_by']
        assert type(self.triggered_by) == list

        del options['triggered_by']

        assert self.export_as is not None

        self.options = options

    def fix(self, *data):
        """
        This function does execute the given action.
        """

        pass
