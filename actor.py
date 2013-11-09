#!/usr/bin/python

import sys
import logging
import time

import dbus
import gobject
import dbus.mainloop.glib


from yapsy.PluginManager import PluginManager

from plugins import IReporter


class Actor(object):

    def __init__(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["reporters"])
        self.plugin_manager.setCategoriesFilter({
           "Reporter": IReporter,
           })
        self.plugin_manager.collectPlugins()

    def get_plugins(self, category):
        plugin_infos = self.plugin_manager.getPluginsOfCategory(category)
        plugins = [plugin_info.plugin_object for plugin_info in plugin_infos]
        return plugins

    def check_reporters(self):
        for reporter in self.get_plugins("Reporter"):
            print reporter.report()

    def do_main_program(self):
        self.check_reporters()


if __name__ == '__main__':
    stdout_handler = logging.StreamHandler(sys.stdout)
    rootLogger = logging.getLogger('yapsy')
    rootLogger.addHandler(stdout_handler)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    actor = Actor()
    print actor.plugin_manager.getAllPlugins()

    while True:
        time.sleep(5)
        actor.check_reporters()
