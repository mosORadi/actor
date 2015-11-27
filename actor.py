#!/usr/bin/python

import os
import logging
import hashlib
import traceback
import importlib
import imp

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

from context import Context
from plugins import PythonRule

from config import CONFIG_DIR, HOME_DIR
from local_config import SLEEP_HASH

class ActorDBusProxy(dbus.service.Object):

    def __init__(self, actor):
        self.actor = actor

        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.freedesktop.Actor", bus=bus)

        super(ActorDBusProxy, self).__init__(bus_name, "/Actor")

    # Dbus interface
    @dbus.service.method("org.freedesktop.Actor", in_signature='s')
    def SetActivity(self, activity):
        self.actor.set_activity(activity)

    @dbus.service.method("org.freedesktop.Actor", in_signature='')
    def UnsetActivity(self):
        self.actor.unset_activity()

    @dbus.service.method("org.freedesktop.Actor", in_signature='s')
    def SetFlow(self, activity):
        self.actor.set_flow(activity)

    @dbus.service.method("org.freedesktop.Actor", in_signature='')
    def UnsetFlow(self):
        self.actor.unset_flow()


class Actor(object):

    def __init__(self):
        self.rules = []
        self.activity = None
        self.flow = None

        # Start dbus mainloop
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # Load the plugins
        self.import_plugins()
        self.context = Context()

        # Load the Actor configuration
        self.load_configuration()

    # Logging related methods

    @staticmethod
    def log_exception(exception_type, value, tb):
        logging.error("Exception: %s", exception_type)
        logging.error("Value: %s", value)
        logging.error("Traceback (on a new line):\n%s",
                      "\n".join(traceback.format_tb(tb)))

    @staticmethod
    def setup_logging(daemon_mode=False, level=logging.WARNING):
        # Setup Actor logging
        config = dict(format='%(asctime)s: %(levelname)s: %(message)s',
                      datefmt='%m/%d/%Y %I:%M:%S %p',
                      level=level)

        if daemon_mode:
            config.update(dict(filename=os.path.join(HOME_DIR, 'actor.log')))

        logging.basicConfig(**config)

    # Initialization related methods

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

    # Interface related methods

    def set_activity(self, identifier, force=False):
        """
        Sets the current activity as given by the identifier.
        """

        logging.info("Setting activity %s" % identifier)
        if self.flow is None or force:
            self.activity = self.context.activities.make(identifier)
        else:
            logging.info("Activity cannot be set, flow in progress.")

    def unset_activity(self, force=False):
        """
        Unsets the current activity.
        """

        logging.info("Unsetting activity.")
        if self.flow is None or force:
            self.activity = None
        else:
            logging.info("Activity cannot be unset, flow in progress.")


    def set_flow(self, identifier):
        """
        Sets the current flow as given by the identifier.
        """

        logging.info("Setting flow %s" % identifier)
        if self.flow is None:
            self.flow = self.context.flows.make(identifier, args=(self,))
        else:
            logging.info("Flow already in progress")

    def unset_flow(self):
        """
        Unsets the current flow.
        """

        logging.info("Unsetting flow.")
        self.flow = None
        self.unset_activity()

    # Runtime related methods

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

        # Make sure current activity is respected
        if self.activity is not None:
            self.activity.run()

        if self.flow is not None:
            self.flow.run()

        return True

    def main(self):
        # Start the main loop
        loop = gobject.MainLoop()
        gobject.timeout_add(2000, self.check_everything)
        logging.info("AcTor started.")
        loop.run()

if __name__ == "__main__":
    Actor.setup_logging(level=logging.DEBUG)
    actor = Actor()
    proxy = ActorDBusProxy(actor)
    actor.main()
