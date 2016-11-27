from plugins import (Reporter, Checker, Fixer, NoSuchPlugin,
                     PluginCache, PluginFactory)
from logger import LoggerMixin
from activities import Activity, Flow
from timetracking import Timetracking


class Context(LoggerMixin):
    """
    Object to keep shared state. Provides:
    - Access to plugins via PluginCaches and PluginFactories
    - List of rule and tracker instances
    - Current activity and flow
    - Timetracking interface
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

    def set_activity(self, identifier, time_limit=None):
        """
        Sets the current activity as given by the identifier.
        """

        self.info("Setting activity {0} ({1})",
                  identifier, time_limit or 'unlimited')
        self.activity = self.activities.make(identifier,
                                             kwargs=dict(time_limit=time_limit))
        self.info("Activity is now {0}", self.activity)

    def unset_activity(self):
        """
        Unsets the current activity.
        """

        self.info("Unsetting activity.")
        self.activity = None

    def set_flow(self, identifier, time_limit=None):
        """
        Sets the current flow as given by the identifier.
        """

        self.info("Setting flow {0} ({1})", identifier, time_limit or 'unlimited')
        self.flow = self.flows.make(identifier,
                                    kwargs=dict(time_limit=time_limit))

    def unset_flow(self):
        """
        Unsets the current flow.
        """

        self.info("Unsetting flow.")
        self.flow = None
        self.unset_activity()
