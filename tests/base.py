import importlib
from unittest import TestCase

class FakePluginCache(object):

    def __init__(self):
        self.store = {}

    def get(self, identifier, args, kwargs):
        """
        Returns a stored value for the given identifier, ignoring the
        args/kwargs.
        """
        return self.store.get(identifier)

    def __setitem__(self, identifier, value):
        """
        Supports faking the cache values via item assigment.
        """

        self.store[identifier] = value

class MockContext(object):

    def __init__(self):
        self.reporters = FakePluginCache()
        self.checkers = FakePluginCache()
        self.fixers = FakePluginCache()


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
