import logging

class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class Plugin(object):

    required_framework_options = ['rule_name']
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
                                                    options['rule_name'],
                                                    list(missing_options)))

        # Make sure no ignored options are present
        all_options_set = required_options_set.union(set(self.optional_options))
        if not options_set.issubset(all_options_set):
            extra_options = options_set.difference(all_options_set)
            raise ValueError("The following options are extra "
                             "for %s in %s : %s" % (self.__class__.__name__,
                                                    options['rule_name'],
                                                    list(extra_options)))

    def log(self, log_func, message):
        log_func("%s : %s: %s" % (self.options['rule_name'],
                                  self.__class__.__name__,
                                  message))

    def debug(self, message):
        self.log(logging.debug, message)

    def info(self, message):
        self.log(logging.info, message)

    def warning(self, message):
        self.log(logging.warning, message)

    def error(self, message):
        self.log(logging.error, message)

    def critical(self, message):
        self.log(logging.critical, message)

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
                (self.__class__.__name__, options['rule_name']))

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


class Reporter(Plugin):
    """Reports user activity to the AcTor"""

    __metaclass__ = PluginMount
    optional_framework_options = ['export_as']
    export_as = None

    def __init__(self, **options):
        super(Reporter, self).__init__(**options)
        self.options = self.set_export_as(**options)

    def report(self):
        """Returns user activity value"""
        pass

    def report_safe(self):
        try:
            return self.report()
        except Exception as e:
            # TODO: Log the failure
            self.warning("Generation of the report failed: %s" % str(e))
            return None



class Checker(Plugin):
    """Evaluates user activity depending on the input from the responders"""

    __metaclass__ = PluginMount
    optional_framework_options = ['export_as', 'inputs']

    def __init__(self, **options):
        super(Checker, self).__init__(**options)
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
        redirected_reports = self.get_redirected_reports(**reports)
        return self.check(**redirected_reports)


class Fixer(Plugin):

    __metaclass__ = PluginMount
    required_framework_options = ['rule_name', 'triggered_by']
    optional_framework_options = ['inputs']

    def __init__(self, **options):
        """
        The triggered_by option must be passed via the framework.
        """

        super(Fixer, self).__init__(**options)

        self.triggered_by = options['triggered_by']

    def fix(self, **reports):
        """
        This function does execute the given action.
        """

        pass

    def fix_raw(self, **reports):
        reports = self.get_redirected_reports(**reports)
        return self.fix(**reports)
