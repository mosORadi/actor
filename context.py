from plugins import (Reporter, Checker, Fixer, NoSuchPlugin,
                     PluginCache, PluginFactory)
from activities import Activity, Flow
from timetracking import Timetracking


class Context(object):
    """
    Object to keep shared state. Provides:
    - Access to plugins via PluginCaches and PluginFactories
    - List of rule and tracker instances
    - Current activity and flow
    """

    def __init__(self):
        self.rules = []
        self.trackers = []

        self.activity = None
        self.flow = None

        self.reporters = PluginCache(Reporter, self)
        self.checkers = PluginCache(Checker, self)
        self.fixers = PluginCache(Fixer, self)

        self.reporter_factory = PluginFactory(Reporter, self)
        self.checker_factory = PluginFactory(Checker, self)
        self.fixer_factory = PluginFactory(Fixer, self)

        self.activities = PluginFactory(Activity, self)
        self.flows = PluginFactory(Flow, self)

        self.timetracking = Timetracking(self)

    def clear_cache(self):
        """
        Clears all the cached values in the PluginCaches. This method should
        be called after each evaluation round, since external data sources
        might provide new values.
        """

        self.reporters.cache.clear()
        self.checkers.cache.clear()
        self.fixers.cache.clear()
