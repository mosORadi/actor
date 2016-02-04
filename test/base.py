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

    def setUp(self):
        # Load the plugin
        module_name = '{0}s.{1}'.format(self.plugin_type, self.module_name)
        module = importlib.import_module(module_name)
        plugin_class = getattr(module, self.class_name)

        # Initialize a new MockContext
        self.context = MockContext()

        # Instantiate the plugin using the MockContext
        self.plugin = plugin_class(self.context)


class ReporterTestCase(PluginTestCase):
    plugin_type = 'reporter'


class CheckerTestCase(PluginTestCase):
    plugin_type = 'checker'


class FixerTestCase(PluginTestCase):
    plugin_type = 'fixer'
