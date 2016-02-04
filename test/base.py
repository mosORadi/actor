import importlib
from unittest import TestCase

class MockContext(object):

    def __init__(self):
        self.fake_reports = {}
        self.fake_checks = {}
        self.fake_fixes = {}

    def report(self, identifier, *args, **kwargs):
        return self.fake_reports[identifier]

    def check(self, identifier, *args, **kwargs):
        return self.fake_checks[identifier]

    def fix(self, identifier, *args, **kwargs):
        return self.fake_fixes[identifier]


class PluginTestCase(TestCase):
    class_name = None
    module_name = None
    plugin_type = None

    def __init__(self, *args, **kwargs):
        self.options = {}
        super(PluginTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        # Update settings from the parent class instance
        parent_options = getattr(self.__class__, 'options', dict())
        self.options.update(parent_options)

        # Load the plugin
        module_name = '{0}s.{1}'.format(self.plugin_type, self.module_name)
        module = importlib.import_module(module_name)
        self.plugin_class = getattr(module, self.class_name)
        self.initialize(**self.options)

    def initialize(self, **options):
        self.plugin = self.plugin_class(None)


class ReporterTestCase(PluginTestCase):
    plugin_type = 'reporter'


class CheckerTestCase(PluginTestCase):
    plugin_type = 'checker'


class FixerTestCase(PluginTestCase):
    plugin_type = 'fixer'
