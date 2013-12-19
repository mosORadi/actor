#!/usr/bin/python

import copy
import os
import sys
import logging
import time

import gobject
import dbus
import dbus.mainloop.glib
import yaml

from yapsy.PluginManager import PluginManager

from plugins import IReporter, IChecker, IFixer


class Actor(object):

    def __init__(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["reporters", "checkers", "fixers"])
        self.plugin_manager.setCategoriesFilter({
           "Reporter": IReporter,
           "Checker": IChecker,
           "Fixer": IFixer,
           })
        self.plugin_manager.collectPlugins()

        self.activities = []

    def get_plugins(self, category):
        plugin_infos = self.plugin_manager.getPluginsOfCategory(category)
        plugins = [plugin_info.plugin_object for plugin_info in plugin_infos]
        return plugins

    def check_reporters(self):
        for reporter in self.get_plugins("Reporter"):
            print reporter.report()

    def check_checkers(self):
        for checker in self.get_plugins("Checker"):
            print checker.check()

    def check_fixers(self):
        for fixer in self.get_plugins("Fixer"):
            print fixer.fix()

    def do_main_program(self):
        self.check_reporters()

    def load_configuration(self):
        yaml_config_paths = [os.path.join("config", path)
                             for path in os.listdir("config")
                             if path.endswith('.yaml')]

        for path in yaml_config_paths:
            with open(path, "r") as f:
                activity_definitions = yaml.load(f)

                for config in activity_definitions:
                    activity = Activity.from_yaml(config)
                    self.activities.append(activity)


class Activity(object):

    def __init__(self):
        self.reporters = []
        self.checkers = []
        self.fixers = []

    @classmethod
    def from_yaml(cls, config):
        definitions = [(name, details) for (name, details)
                                       in config.iteritems()]
        assert len(definitions) == 1

        name = definitions[0][0]
        details = definitions[0][1]

        reporters_info = details.get("reporter")
        checkers_info = details.get("checker")
        fixers_info = details.get("fixer")

        assert reporters_info is not None
        assert checkers_info is not None
        assert fixers_info is not None

        activity = cls()

        for reporter_info in reporters_info:
            for plugin_name, options in reporter_info.iteritems():
                options = options or {}

                reporter_plugin = actor.plugin_manager.getPluginByName(
                                    plugin_name,
                                    category="Reporter").plugin_object.__class__
                reporter = reporter_plugin()
                reporter.setup(**options)
                activity.reporters.append(reporter)

        for checker_info in checkers_info:
            for plugin_name, options in checker_info.iteritems():
                options = options or {}
                checker_plugin = actor.plugin_manager.getPluginByName(
                                    plugin_name,
                                    category="Checker").plugin_object.__class__
                checker = checker_plugin()
                checker.setup(**options)

                activity.checkers.append(checker)

        all_checker_names = [checker.export_as for checker in activity.checkers]

        for fixer_info in fixers_info:
            for plugin_name, options in fixer_info.iteritems():
                options = options or {}
                if 'triggered_by' not in options:
                    options['triggered_by'] = all_checker_names

                fixer_plugin = actor.plugin_manager.getPluginByName(
                                    plugin_name,
                                    category="Fixer").plugin_object.__class__
                fixer = fixer_plugin()
                fixer.setup(**options)

                activity.fixers.append(fixer)

        return activity

def check_everything():
    for activity in actor.activities:

        # Generate reports
        reports = {reporter.export_as:reporter.report()
                   for reporter in activity.reporters}

        # Determine which checkers approve the situation
        active_checkers = [checker.export_as
                           for checker in activity.checkers
                           if checker.check(**reports)]

        # Run all the fixers that were triggered
        # By default fixer needs all the checkers defined to be active
        for fixer in activity.fixers:
             if set(fixer.triggered_by).issubset(set(active_checkers)):
                 fixer.fix()

    return True
if __name__ == '__main__':
    stdout_handler = logging.StreamHandler(sys.stdout)
    rootLogger = logging.getLogger('yapsy')
    rootLogger.addHandler(stdout_handler)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    actor = Actor()

    actor.load_configuration()
    loop = gobject.MainLoop()
    gobject.timeout_add(2000, check_everything)
    loop.run()


