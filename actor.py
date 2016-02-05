#!/usr/bin/python -B

import os
import sys
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
from plugins import Rule
from trackers import Tracker

from config import CONFIG_DIR, HOME_DIR
from config import (SLEEP_HASH, LOGGING_TARGET,
                    LOGGING_FILE, LOGGING_TIMESTAMP)
from logger import LoggerMixin


class ActorDBusProxy(dbus.service.Object):

    def __init__(self, actor):
        self.actor = actor

        bus = dbus.SessionBus()

        # Prevent duplicate Actor instances
        if 'org.freedesktop.Actor' in bus.list_names():
            actor.info("Actord already running, exiting.")
            sys.exit(0)

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

    @dbus.service.method("org.freedesktop.Actor", in_signature='s')
    def Report(self, identifier):
        return self.actor.context.reporters.get(identifier)


class Actor(LoggerMixin):

    def __init__(self):
        self.rules = []
        self.trackers = []

        # Start dbus mainloop
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # Load the plugins
        self.import_plugins()
        self.context = Context()

        # Load the Actor configuration
        self.load_configuration()

    # Logging related methods

    @staticmethod
    def log_exception(exception_type, value, trace):
        root_logger = logging.getLogger('main')

        if exception_type == KeyboardInterrupt:
            root_logger.error("Actor was interrupted.")
            sys.exit(0)

        root_logger.error("Exception: %s", exception_type)
        root_logger.error("Value: %s", value)
        root_logger.error("Traceback (on a new line):\n%s",
                          "\n".join(traceback.format_tb(trace)))

    @staticmethod
    def setup_logging(daemon_mode=False, level='info'):
        # Setup Actor logging
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }

        logging_level = level_map.get(level)

        log_default_level_warning = False

        if logging_level is None:
            logging_level = logging.INFO
            log_default_level_warning = True

        # Setup main logger
        root_logger = logging.getLogger('main')
        root_logger.setLevel(logging.DEBUG)

        # Define logging format
        timeformat = '%(asctime)s:' if LOGGING_TIMESTAMP else ''
        formatter = logging.Formatter(
            timeformat + ' %(levelname)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
        )

        # Define default handlers
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging_level)
        stream_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(
            filename=os.path.expanduser(LOGGING_FILE)
        )
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(formatter)

        # Setup desired handlers
        if LOGGING_TARGET == 'both':
            root_logger.addHandler(file_handler)
            root_logger.addHandler(stream_handler)
        elif LOGGING_TARGET == 'file':
            root_logger.addHandler(file_handler)
        else:
            root_logger.addHandler(stream_handler)

        if log_default_level_warning:
            root_logger.warning("Logging level '{0}' not recognized, "
                                "using 'info' instead".format(level))

    # Initialization related methods

    def import_plugins(self):
        import reporters
        import checkers
        import fixers
        categories = [reporters, checkers, fixers]

        for category in categories:
            for module in category.__all__:
                try:
                    module_id = "{0}.{1}".format(category.__name__, module)
                    importlib.import_module(module_id)
                    self.debug(module_id + " loaded successfully.")
                except Exception as exc:
                    self.warning(
                        "The {0} {1} module could not be loaded: {2} "
                        .format(module, category.__name__[:-1], str(exc)))
                    self.info(traceback.format_exc())

    def load_configuration(self):
        # Create the config directory, if it does not exist
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)

        # Load the rule files. They will be automatically
        # added to the Rule pluginmount.
        rules = [os.path.join(CONFIG_DIR, path)
                 for path in os.listdir(CONFIG_DIR)
                 if path.endswith('.py')]

        for path in rules:
            try:
                module_id = os.path.basename(path.rstrip('.py'))
                imp.load_source(module_id, path)
            except Exception as exc:
                self.warning(
                    "Rule file {0} cannot be loaded, following error was "
                    "encountered: {1}".format(path, str(exc))
                )
                self.info(traceback.format_exc())

        for rule_class in Rule.plugins:
            self.rules.append(rule_class(self.context))

        for tracker_class in Tracker.plugins:
            self.trackers.append(tracker_class(self.context))

        if not rules:
            self.warning("No rules available")

    # Interface related methods

    def set_activity(self, identifier, force=False):
        """
        Sets the current activity as given by the identifier.
        """

        self.info("Setting activity %s", identifier)
        if self.context.flow is None or force:
            self.context.activity = self.context.activities.make(identifier)
        else:
            self.info("Activity cannot be set, flow in progress.")

    def unset_activity(self, force=False):
        """
        Unsets the current activity.
        """

        self.info("Unsetting activity.")
        if self.context.flow is None or force:
            self.context.activity = None
        else:
            self.info("Activity cannot be unset, flow in progress.")

    def set_flow(self, identifier):
        """
        Sets the current flow as given by the identifier.
        """

        self.info("Setting flow %s" % identifier)
        if self.context.flow is None:
            self.context.flow = self.context.flows.make(
                identifier,
                args=(self,)
            )
        else:
            self.info("Flow already in progress")

    def unset_flow(self):
        """
        Unsets the current flow.
        """

        self.info("Unsetting flow.")
        self.context.flow = None
        self.unset_activity()

    # Runtime related methods

    def check_sleep_file(self):
        """
        You can create one sleep file in your home directory.
        It immediately suspends AcTor.
        """

        sleep_file_path = os.path.join(HOME_DIR, 'actor-sleep')
        if os.path.exists(sleep_file_path):
            with open(sleep_file_path, 'r') as input_file:
                content = input_file.readlines()[0].strip()
                content_hash = hashlib.sha1(content).hexdigest()

            return content_hash == SLEEP_HASH

    def check_everything(self):
        if self.check_sleep_file():
            self.warning('Sleep file exists, skipping.')
            return True

        # Clear the cached values
        self.context.clear_cache()

        for rule in self.rules:
            rule.run()

        for tracker in self.trackers:
            tracker.run()

        # Make sure current activity is respected
        if self.context.activity is not None:
            self.context.activity.run()

        if self.context.flow is not None:
            self.context.flow.run()

        return True

    def main(self):
        # Start the main loop
        loop = gobject.MainLoop()
        gobject.timeout_add(2000, self.check_everything)
        self.info("AcTor started.")
        loop.run()

if __name__ == "__main__":
    Actor.setup_logging(level='debug')
    actor = Actor()
    proxy = ActorDBusProxy(actor)
    actor.main()
