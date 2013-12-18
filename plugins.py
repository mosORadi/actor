from yapsy.IPlugin import IPlugin


class IReporter(IPlugin):
    """Reports user activity to the AcTor"""

    export_as = None

    def __init__(self, **options):
        if 'export_as' in options:
            assert type(options['export_as']) == str
            self.run_fixers = options['export_as']
            del options['export_as']

        assert self.export_as is not None
        self.options = options

    def report(self):
        """Returns user activity value"""
        pass


class IChecker(IPlugin):
    """Evaluates user activity depending on the input from the responders"""

    run_fixers = None

    def __init__(self, **options):
        if 'run_fixers' in options:
            assert type(options['run_fixers']) == list
            self.run_fixers = options['run_fixers']
            del options['run_fixers']

        self.options = options


    def does_run(self, fixer):
        """
        Evaluates whether this checker should cause running of the fixer
        plugin passed as argument.

        If no run_fixers list attribute is specified, every fixers should be 
        run.
        If it is, only fixers speciefied in the run_fixers list should be run.
        """

        return run_fixers is None or fixer.export_as in self.run_fixers

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
    def __init__(self, **options):
        if 'export_as' in options:
            assert type(options['export_as']) == str
            self.run_fixers = options['export_as']
            del options['export_as']

        assert self.export_as is not None

        self.options = options

    def fix(self, *data):
        """
        This function does execute the given action.
        """

        pass
