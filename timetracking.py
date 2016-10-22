"""
Provides a layer that exposes time-tracking abilities, regardless of the user
selected backend (Hamster, Timewarrior, etc.).
"""

import config

from plugins import PluginMount, PluginFactory, Plugin

class Timetracking(object):

    def __init__(self, context):
        factory = PluginFactory(Timetracker, context)
        self.timetracker = factory.make(config.TIMETRACKER)

    def start(self, activity, category=None, tags=None):
        self.timetracker.start(activity, category, tags)

    def stop(self):
        self.timetracker.stop()


class Timetracker(Plugin):

    __metaclass__ = PluginMount


class HamsterTimetracker(Timetracker):

    identifier = 'hamster'

    def start(self, activity, category, tags):
        self.fix('set_hamster_activity', activity=activity)

    def stop(self):
        self.fix('stop_hamster_activity')


class TimewarriorTimetracker(Timetracker):

    identifier = 'timewarrior'

    def start(self, activity, category, tags):
        self.fix('set_timew_activity', activity=activity)

    def stop(self):
        self.fix('stop_timew_activity')
