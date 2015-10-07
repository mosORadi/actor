#!/usr/bin/python

import sys
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
    """
    Provides an interface to the plugins of a particular type (identified by
    given PluginMount class).

    Never initializes the same class twice, once initialized, class instance
    stays in the cache.

    PluginCache tries to be smart and it will not try to evaluate the same
    plugin when called with the same arguments as it has been called before.
    This behaviour is leveraged by Actor to avoid redundat multiple
    re-evaluations of the same plugin. It can be altered, however, with the
    following two flags:

      * stateless: Plugin is marked as stateless, i.e. its run() method
                   does not keep any state inside the plugin object.
                   If plugin is stateless, its instance can be shared between
                   multiple Rules.
      * side_effects: Plugin has side effects, i.e. it makes sense to
                      re-evaluate it when called with the same arguments.
    """

    def __init__(self, mount, context):
        self.mount = mount
        self.context = context
        self.cache = {}
        self.instances = {}

    @property
    def plugins(self):
        return {
            plugin_class.identifier: plugin_class
            for plugin_class in self.mount.plugins
        }

    def get(self, identifier, args, kwargs, rule_name=None):
        """
        Obtain a result from the given plugin. If the plugin is stateless
        and has no side effects, it will be returned from the result cache.

        Otherwise, the plugin will be re-evaluated and the result will be
        returned.
        """

        plugin_class = self.get_plugin(identifier)

        # Instances can be shared, and be kept for the time the Actor runs,
        # however, in the case of stateful plugins, we need to make sure
        # we create a separate instance per rule.

        if plugin_class.stateless and not plugin_class.side_effects:
            # Can be cached (per loop).
            return self.result_from_cache(identifier, args, kwargs)
        elif plugin_class.stateless:
            # It has side-effects, hence we need to run it.
            return self.run_plugin_instance(identifier, args, kwargs)
        else:
            if rule_name is None:
                raise ValueError("Only stateless plugins can be accessed "
                                 "from workers.")
            # It is stateful, hence cannot be shared between modules.
            # Modify instance name to include the rule name.
            instance_id = '{0}_{1}'.format(identifier, rule_name)
            return self.run_plugin_instance(instance_id, args, kwargs,
                                            class_identifier=identifier)

    def get_plugin(self, identifier):
        """
        Returns a plugin class identified by the given identifier.
        """

        try:
            return self.plugins[identifier]
        except KeyError:
            pass
            # TODO: Raise an error, no such plugin available

    def get_plugin_instance(self, identifier, class_identifier=None):
        """
        Returns a plugin instance corresponding to the given class identifier.
        If case the class identifier is None, identifier will be used. This is
        useful for the stateful plugins, where an unique identifier is
        constructed for each Rule.

        Makes sure plugins are initialized only once.
        """

        instance = self.instances.get(identifier)

        if instance is None:
            plugin_class = self.get_plugin(class_identifier or identifier)
            self.instances[identifier] = instance = plugin_class(self.context)

        return instance

    def result_from_cache(self, identifier, args, kwargs):
        """
        Only for stateless plugins with no side-effects. Gets the result from
        evaluation of the plugin with the corresponding identifier.

        Makes sure plugins are evaluated only once per (args, kwargs) tuple.
        """
        # Note: Only for stateless and no side-effects

        key = (identifier, args, HashableDict(**kwargs))
        value = self.cache.get(key)

        if value is None:
            plugin_instance = self.get_plugin(identifier)(self.context)
            self.cache[key] = value = plugin_instance.evaluate(*args, **kwargs)

        return value

    def run_plugin_instance(self, identifier, args, kwargs, class_identifier=None):
        """
        Evaluates the plugin instance corresponding to the given identifier
        and returns the result.
        """

        instance = self.get_plugin_instance(identifier, class_identifier)
        return instance.run(*args, **kwargs)

    def clear(self):
        """
        Clears the result cache. Instance cache is preserved.
        """

        self.cache.clear()

    def __iter__(self):
        """
        Iterates over all the instances of the plugins available to the cache.
        """

        for plugin_class in self.plugins:
            yield self.get_plugin_instance(plugin_class.identifier, None)


class PluginFactory(object):

    def __init__(self, mount, context):
        self.mount = mount
        self.context = context

    @property
    def plugins(self):
        return {
            plugin_class.identifier: plugin_class
            for plugin_class in self.mount.plugins
        }

    def make(self, identifier, args, kwargs):
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
                except Exception as e:
                    logging.warning(
                        "The {0} {1} module could not be loaded: {2} "
                        .format(module, category.__name__[:-1]), str(e))
                    logging.info(traceback.format_exc())

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
            try:
                module_id = os.path.basename(path.rstrip('.py'))
                imp.load_source(module_id, path)
            except Exception as e:
                logging.warning(
                    "Rule file {0} cannot be loaded, following error was "
                    "encountered: {1}".format(path, str(e))
                    )
                logging.info(traceback.format_exc())

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
