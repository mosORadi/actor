import importlib
from unittest import TestCase

class PluginTestCase(TestCase):
    plugin_type = None
    module_name = None
    class_name = None

    def setUp(self):
        module_name = '{0}s.{1}'.format(self.plugin_type, self.module_name)
        module = importlib.import_module(module_name)
        plugin_class = getattr(module, self.class_name)
        self.plugin = plugin_class(activity_name="test")

class ReporterTestCase(PluginTestCase):
    plugin_type = 'reporter'

class CheckerTestCase(PluginTestCase):
    plugin_type = 'checker'

class FixerTestCase(PluginTestCase):
    plugin_type = 'fixer'
