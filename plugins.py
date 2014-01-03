class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class IPlugin(object):
    __metaclass__ = PluginMount

    required_framework_options = ['activity_name']
    optional_framework_options = []

    required_plugin_options = []
    optional_plugin_options = []

    def __init__(self, **options):
        self.options = options

        self.required_options = self.required_framework_options + self.required_plugin_options
        self.optional_options = self.optional_framework_options + self.optional_plugin_options

        # Make sure all the required framework options
        options_set = set(self.options.keys())
        required_options_set = set(self.required_options)

        if not required_options_set.issubset(options_set):
            missing_options = required_options_set.difference(options_set)
            raise ValueError("The following options are missing "
                             "for %s in %s : %s" % (self.__class__.__name__,
                                                    options['activity_name'],
                                                    list(missing_options)))

        # Make sure no ignored options are present
        all_options_set = required_options_set.union(set(self.optional_options))
        if not options_set.issubset(all_options_set):
            extra_options = options_set.difference(all_options_set)
            raise ValueError("The following options are extra "
                             "for %s in %s : %s" % (self.__class__.__name__,
                                                    options['activity_name'],
                                                    list(extra_options)))

    def set_export_as(self, **options):
        """
        Sets the export_as attribute if specified in options and removes it
        from the options dictionary.
        Makes sure that there is at least some identifier available.

        Returs the updated options dictionary.
        """

        if 'export_as' in options:
            assert type(options['export_as']) == str
            self.export_as = options['export_as']
            del options['export_as']

        if self.export_as is None:
            raise ValueError(
                "The identifier for the %s in %s is not set."
                "Use the export_as option to specify unique identifier." %
                (self.__class__.__name__, options['activity_name']))

        return options

    def get_redirected_reports(self, **reports):
        """
        Redirects the reports for this plugin in the following manner:
            For any key specified in the inputs dictionary,
        """

        reports_redirected = dict()

        if 'inputs' in self.options:
            for key, value in self.options.get('inputs').iteritems():
                 reports_redirected[key]=reports[value]

        reports.update(reports_redirected)

        return reports


class IReporter(IPlugin):
    """Reports user activity to the AcTor"""

    __metaclass__ = PluginMount
    optional_framework_options = ['export_as']
    export_as = None

    def __init__(self, **options):
        super(IReporter, self).__init__(**options)
        self.options = self.set_export_as(**options)

    def report(self):
        """Returns user activity value"""
        pass


class IChecker(IPlugin):
    """Evaluates user activity depending on the input from the responders"""

    __metaclass__ = PluginMount
    optional_framework_options = ['export_as', 'inputs']

    def __init__(self, **options):
        super(IChecker, self).__init__(**options)
        self.options = self.set_export_as(**options)

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


    def check_raw(self, **reports):
        reports = self.get_redirected_reports(**reports)

        if 'negate' in self.options:
            return not self.check(**reports)
        else:
            return self.check(**reports)

class IFixer(IPlugin):

    __metaclass__ = PluginMount
    optional_framework_options = ['triggered_by', 'inputs']

    def __init__(self, **options):
        """
        The triggered_by option must be passed via the framework.
        """

        super(IFixer, self).__init__(**options)

        assert 'triggered_by' in options
        self.triggered_by = options['triggered_by']
        assert type(self.triggered_by) == list

        del options['triggered_by']

        self.options = options

    def fix(self, **reports):
        """
        This function does execute the given action.
        """

        pass

    def fix_raw(self, **reports):
        reports = self.get_redirected_reports(**reports)
        return self.fix(**reports)
