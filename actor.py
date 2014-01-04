#!/usr/bin/python

import copy
import collections
import os
import sys
import logging
import time

import gobject
import dbus
import dbus.mainloop.glib
import yaml

from plugins import IReporter, IChecker, IFixer
from reporters import *
from checkers import *
from fixers import *

class Actor(object):

    def __init__(self):
        self.activities = []

    def get_plugin(self, name, category):
        plugin_candidates = [plugin for plugin in category.plugins if plugin.__name__ == name]

        if plugin_candidates:
            return plugin_candidates[0]
        else:
            raise ValueError("Could not find %s plugin of name: %s" % (category.__name__, name))

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
                options['activity_name'] = name

                reporter_plugin = actor.get_plugin(plugin_name,
                                                   category=IReporter)
                reporter = reporter_plugin(**options)
                activity.reporters.append(reporter)

        for checker_info in checkers_info:
            for plugin_name, options in checker_info.iteritems():
                options = options or {}
                options['activity_name'] = name

                checker_plugin = actor.get_plugin(plugin_name,
                                                  category=IChecker)
                checker = checker_plugin(**options)
                activity.checkers.append(checker)

        all_checker_names = [checker.export_as for checker in activity.checkers]

        for fixer_info in fixers_info:
            for plugin_name, options in fixer_info.iteritems():
                options = options or {}
                options['activity_name'] = name

                if 'triggered_by' not in options:
                    options['triggered_by'] = all_checker_names

                fixer_plugin = actor.get_plugin(plugin_name,
                                                category=IFixer)
                fixer = fixer_plugin(**options)
                activity.fixers.append(fixer)

        # Check that all reporters and checkers have unique exports
        for plugins_by_type, type_name in [(activity.reporters, 'Reporters'),
                                           (activity.checkers, 'Checkers')]:
            plugin_names_list = [plugin.export_as
                                 for plugin in plugins_by_type]
            duplicates = [k for k, v in collections.Counter(plugin_names_list).items()
                          if v > 1]
            if duplicates:
                raise ValueError("Activity %s has name clash in %s for "
                                 "the following identifiers: %s. "
                                 "Use the export_as option to differentiate." %
                                 (name, type_name, duplicates))

        return activity

def check_everything():
    for activity in actor.activities:

        # Generate reports
        reports = {reporter.export_as:reporter.report()
                   for reporter in activity.reporters}

        # Determine which checkers approve the situation
        active_checkers = [checker.export_as
                           for checker in activity.checkers
                           if checker.check_raw(**reports)]

        # Run all the fixers that were triggered
        # By default fixer needs all the checkers defined to be active
        for fixer in activity.fixers:
             all_positive_triggers_active = set(fixer.triggered_by).issubset(set(active_checkers))
             any_negative_trigger_active = any([checker in active_checkers
                                                for checker in fixer.anti_triggered_by])
             if all_positive_triggers_active and not any_negative_trigger_active:
                 fixer.fix_raw(**reports)

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


