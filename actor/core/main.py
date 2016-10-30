#!/usr/bin/python -B

import os
import sys
import importlib
import imp

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

from context import Context
from plugins import Rule
from trackers import Tracker
from util import Expiration

from config import config
from logger import LoggerMixin


class ActorDBusProxy(dbus.service.Object):
    # pylint: disable=interface-not-implemented

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
    # pylint: disable=invalid-name
    @dbus.service.method("org.freedesktop.Actor", in_signature='si')
    def SetActivity(self, activity, time_limit):
        self.actor.set_activity(activity, time_limit or None)

    @dbus.service.method("org.freedesktop.Actor", in_signature='')
    def UnsetActivity(self):
        self.actor.unset_activity()

    @dbus.service.method("org.freedesktop.Actor", in_signature='')
    def NextActivity(self):
        self.actor.next_activity()

    @dbus.service.method("org.freedesktop.Actor", in_signature='')
    def ActivityStatus(self):
        return self.actor.context.activity.identifier, self.actor.context.activity.expired.remaining

    @dbus.service.method("org.freedesktop.Actor", in_signature='i')
    def Pause(self, minutes):
        self.actor.pause(minutes)

    @dbus.service.method("org.freedesktop.Actor", in_signature='si')
    def SetFlow(self, activity, time_limit):
        self.actor.set_flow(activity, time_limit or None)

    @dbus.service.method("org.freedesktop.Actor", in_signature='')
    def UnsetFlow(self):
        self.actor.unset_flow()

    @dbus.service.method("org.freedesktop.Actor", in_signature='')
    def FlowStatus(self):
        flow = self.actor.context.flow.identifier
        activity = self.actor.context.activity.identifier
        remaining = self.actor.context.flow.identifier
        return self.actor.context.flow.identifier, self.actor.context.activity.identifier

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
        self.context = Context()
        self.import_plugins()
        self.load_plugins()

        self.pause_expired = Expiration()

    def handle_exception(self):
        exception_type, value, trace = sys.exc_info()

        if exception_type == KeyboardInterrupt:
            self.error("Actor was interrupted.")
            sys.exit(0)
        else:
            self.log_exception()

    # Initialization related methods

    def import_plugins(self):
        import actor.reporters
        import actor.checkers
        import actor.fixers
        categories = [actor.reporters, actor.checkers, actor.fixers]

        # pylint: disable=broad-except
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
                    self.log_exception()

    def load_plugins(self):
        # Create the config directory, if it does not exist
        if not os.path.exists(config.CONFIG_DIR):
            os.mkdir(config.CONFIG_DIR)

        # Load the rule files. They will be automatically
        # added to the Rule pluginmount.
        rules = [os.path.join(config.CONFIG_DIR, path)
                 for path in os.listdir(config.CONFIG_DIR)
                 if path.endswith('.py')
                 and not path.endswith('config.py')]

        # pylint: disable=broad-except
        for path in rules:
            try:
                module_id = os.path.basename(path.rstrip('.py'))
                imp.load_source(module_id, path)
            except Exception as exc:
                self.warning(
                    "Rule file {0} cannot be loaded, following error was "
                    "encountered: {1}".format(path, str(exc))
                )
                self.log_exception()

        # pylint: disable=no-member
        for rule_class in Rule.plugins:
            self.rules.append(rule_class(self.context))

        for tracker_class in Tracker.plugins:
            self.trackers.append(tracker_class(self.context))

        if not rules:
            self.warning("No rules available")

    # Interface related methods

    def set_activity(self, identifier, time_limit=None):
        """
        Sets the current activity as given by the identifier.
        """

        if self.context.flow is None:
            self.context.set_activity(identifier, time_limit)
        else:
            self.info("Activity %s cannot be set, flow in progress."
                      % identifier)

    def unset_activity(self):
        """
        Unsets the current activity.
        """

        if self.context.flow is None:
            self.context.unset_activity()
        else:
            self.info("Activity cannot be unset, flow in progress.")

    def next_activity(self):
        """
        Starts the next activity in the current flow.
        """

        self.info("Force forwarding to next activity.")
        if self.context.flow is not None:
            self.context.flow.start_next_activity()
        else:
            self.error("Next activity cannot be started, no flow in progress.")

    def set_flow(self, identifier, time_limit=None):
        """
        Sets the current flow as given by the identifier.
        """

        if self.context.flow is None:
            self.context.set_flow(identifier, time_limit)
        else:
            self.info("Cannot set flow %s. flow already in progress" % identifier)

    def unset_flow(self):
        """
        Unsets the current flow.
        """

        self.context.unset_flow()

    def pause(self, minutes):
        self.pause_expired = Expiration(minutes)
        self.info('Pausing Actor for {0} minutes.'.format(minutes))

    # Runtime related methods

    def check_everything(self):
        if not self.pause_expired:
            return True
        elif self.pause_expired.just_expired():
            self.info('Actor is resumed.')

        # Clear the cached values
        self.context.clear_cache()

        for rule in self.rules:
            try:
                rule.run()
            except Exception as e:
                self.handle_exception()

        for tracker in self.trackers:
            try:
                tracker.run()
            except Exception as e:
                self.handle_exception()

        # Make sure current activity is respected
        if self.context.activity is not None:
            try:
                self.context.activity.run()
            except Exception as e:
                self.handle_exception()

        if self.context.flow is not None:
            try:
                self.context.flow.run()
            except Exception as e:
                self.handle_exception()

        return True

    def main(self):
        # Start the main loop
        loop = gobject.MainLoop()
        gobject.timeout_add(2000, self.check_everything)
        self.info("AcTor started.")
        loop.run()
