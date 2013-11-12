#!/usr/bin/python

import sys
import logging
import time

import dbus
import dbus.mainloop.glib


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


if __name__ == '__main__':
    stdout_handler = logging.StreamHandler(sys.stdout)
    rootLogger = logging.getLogger('yapsy')
    rootLogger.addHandler(stdout_handler)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    actor = Actor()
    print actor.get_plugins("Reporter")
    print actor.get_plugins("Checker")
    print actor.get_plugins("Fixer")

    while True:
        time.sleep(5)
        actor.check_reporters()
        actor.check_checkers()
        actor.check_fixers()
