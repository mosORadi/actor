#!/usr/bin/python

import os
import logging
import hashlib
import traceback
import re
import importlib
import imp

import gobject
import dbus
import dbus.mainloop.glib

from plugins import Reporter, Checker, Fixer, PythonRule

from config import CONFIG_DIR, HOME_DIR
from local_config import SLEEP_HASH


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self))


class PluginCache(object):

    def __init__(self, mount, context):
        self.mount = mount
        self.context = context
        self.cache = {}
        self.plugins = {
            plugin_class.identifier: plugin_class
            for plugin_class in self.mount.plugins
        }

    def get(self, identifier, *args, **kwargs):
        plugin_class = self.get_plugin(identifier)

        # If it is stateless and has no side-effects, it can be cached
        if plugin_class.stateless and not plugin_class.side_effects:
            return self.get_from_cache(identifier, *args, **kwargs)
        else:
            pass
            # TODO: Raise an error, such things ought to be accessed
            #       via a factory

    def get_plugin(self, identifier):
        try:
            return self.plugins[identifier]
        except KeyError:
            pass
            # TODO: Raise an error, no such plugin available

    def get_from_cache(self, identifier, *args, **kwargs):
        # Note: Only for stateless and no side-effects

        key = (identifier, args, HashableDict(**kwargs))
        value = self.cache.get(key)

        if value is None:
            plugin_instance = self.get_plugin(identifier)(self.context)
            self.cache[key] = value = plugin_instance.evaluate(*args, **kwargs)

        return value

    def clear(self):
        self.cache.clear()


class PluginFactory(object):

    def __init__(self, mount, context):
        self.mount = mount
        self.context = context
        self.plugins = {
            plugin_class.identifier: plugin_class
            for plugin_class in self.mount.plugins
        }

    def get(self, identifier, *args, **kwargs):
        plugin_class = self.get_plugin(identifier)

        # If it is stateless and has no side-effects, it can be cached
        if not plugin_class.stateless or plugin_class.side_effects:
            return self.get_plugin(identifier)(self.context, *args, **kwargs)
        else:
            pass
            # TODO: Raise an error, such things ought to be accessed
            #       via a factory

    def get_plugin(self, identifier):
        try:
            return self.plugins[identifier]
        except KeyError:
            pass
            # TODO: Raise an error, no such plugin available


class Context(object):

    def __init__(self):
        self.rules = []
        self.activity = None
        self.flow = None

        self.reporters = PluginCache(Reporter, self)
        self.checkers = PluginCache(Checker, self)
        self.fixers = PluginCache(Fixer, self)

        self.reporter_factory = PluginFactory(Reporter, self)
        self.checker_factory = PluginFactory(Checker, self)
        self.fixer_factory = PluginFactory(Fixer, self)


class Actor(object):

    def __init__(self):
        self.rules = []

    def main(self):
        # Start dbus mainloop
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # Load the plugins
        self.import_plugins()
        self.context = Context()

        # Load the Actor configuration
        self.load_configuration()

        # Start the main loop
        loop = gobject.MainLoop()
        gobject.timeout_add(2000, self.check_everything)
        logging.info("AcTor started.")
        loop.run()

    def setup_logging(self, daemon_mode=False, level=logging.WARNING):
        # Setup Actor logging
        config = dict(format='%(asctime)s: %(levelname)s: %(message)s',
                      datefmt='%m/%d/%Y %I:%M:%S %p',
                      level=level)

        if daemon_mode:
            config.update(dict(filename=os.path.join(HOME_DIR, 'actor.log')))

        logging.basicConfig(**config)

    def log_exception(self, exception_type, value, tb):
        logging.error("Exception: %s", exception_type)
        logging.error("Value: %s", value)
        logging.error("Traceback: %s", traceback.format_exc())

    def import_plugins(self):
        import reporters, checkers, fixers
        categories = [reporters, checkers, fixers]

        for category in categories:
            for module in category.__all__:
                try:
                    module_id = "{0}.{1}".format(category.__name__, module)
                    importlib.import_module(module_id)
                    logging.debug(module_id + " loaded successfully.")
                except Exception, e:
                    logging.warning("The {0} {1} module could not be loaded. "
                                    "Increase verbosity level to see more "
                                    "information."
                                    .format(module, category.__name__[:-1]))
                    logging.info(str(e))

    def get_plugin(self, name, category):
        plugin_candidates = [plugin for plugin in category.plugins
                             if plugin.__name__ == name]

        if plugin_candidates:
            return plugin_candidates[0]
        else:
            raise ValueError("Could not find %s plugin of name: %s"
                              % (category.__name__, name))

    def load_configuration(self):
        # Create the config directory, if it does not exist
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)

        # Load the python rules files. They will be automatically
        # added to the PythonRule pluginmount.
        python_rules = [os.path.join(CONFIG_DIR, path)
                        for path in os.listdir(CONFIG_DIR)
                        if path.endswith('.py')]

        for path in python_rules:
            module_id = os.path.basename(path.rstrip('.py'))
            imp.load_source(module_id, path)

        for rule_class in PythonRule.plugins:
            self.rules.append(rule_class(self.context))

        if not python_rules:
            logging.warning("No Python rules available")

    def check_sleep_file(self):
        """
        You can create one sleep file in your home directory.
        It immediately suspends AcTor.
        """

        sleep_file_path = os.path.join(HOME_DIR, 'actor-sleep')
        if os.path.exists(sleep_file_path):
            with open(sleep_file_path, 'r') as f:
                content = f.readlines()[0].strip()
                content_hash = hashlib.sha1(content).hexdigest()

            return content_hash == SLEEP_HASH

    def check_everything(self):
        if self.check_sleep_file():
            logging.warning('Sleep file exists, skipping.')
            return True

        # Clear the cached report values
        self.context.reporters.clear()

        for rule in self.rules:
            rule.run()

        return True

if __name__ == "__main__":
    actor = Actor()
    actor.setup_logging(level=logging.DEBUG)
    actor.main()
