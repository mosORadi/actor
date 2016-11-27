#!/usr/bin/python -B

import os
import sys
import time
import importlib
import imp

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

from context import Context
from plugins import Rule, DBusMixin
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


class Actor(DBusMixin, LoggerMixin):

    bus_name = 'org.freedesktop.ActorDesktop'
    object_path = '/Desktop'

    def __init__(self):
        # Start dbus mainloop, must happen before super call
        # as DBusMixin's __init__ needs this
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        super(Actor, self).__init__()

        self.rules = []
        self.trackers = []

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

    def wait_for_desktop(self):
        """
        Waits until desktop process is available (verified by dedicated
        DBus call). Times out after 60 seconds.
        """

        timeout = 60
        self.info('Waiting for desktop process.')

        while timeout > 0:
            desktop_setup_finished = (self.interface and
                                      self.interface.SetupFinished())

            if desktop_setup_finished:
                self.info('Desktop process setup finished.')
                break
            else:
                timeout = timeout - 1
                time.sleep(1)

        if timeout <= 0:
            self.info('Waiting for desktop process timed out.')

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
                        "The {0} {1} module could not be loaded: {2} ",
                        module, category.__name__[:-1], str(exc))
                    self.log_exception()

    def load_plugins(self):
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
                self.debug(module_id + " loaded successfully.")
            except Exception as exc:
                self.warning(
                    "Rule file {0} cannot be loaded, following error was "
                    "encountered: {1}", path, str(exc)
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
            self.info("Cannot set flow {0}. flow already in progress", identifier)

    def unset_flow(self):
        """
        Unsets the current flow.
        """

        self.context.unset_flow()

    def pause(self, minutes):
        self.pause_expired = Expiration(minutes)
        self.info('Pausing Actor for {0} minutes.', minutes)

    # Runtime related methods

    def check_everything(self):
        if not self.pause_expired:
            return True
        elif self.pause_expired.just_expired():
            self.info('Actor is resumed.')

        with self.stage('Checking round'):
            # Clear the cached values
            self.context.clear_cache()

            for rule in self.rules:
                with self.stage('Evaluating rule: {0}', rule):
                    try:
                        rule.run()
                    except Exception as e:
                        self.handle_exception()

            for tracker in self.trackers:
                with self.stage('Evaluating tracker: {0}', tracker):
                    try:
                        tracker.run()
                    except Exception as e:
                        self.handle_exception()

            # Make sure current activity is respected
            if self.context.activity is not None:
                with self.stage('Evaluating activity: {0}', self.context.activity):
                    try:
                        self.context.activity.run()
                    except Exception as e:
                        self.handle_exception()

            if self.context.flow is not None:
                with self.stage('Evaluating flow: {0}', self.context.flow):
                    try:
                        self.context.flow.run()
                    except Exception as e:
                        self.handle_exception()

        return True

    def main(self):
        # Start the main loop
        loop = gobject.MainLoop()
        gobject.timeout_add(2000, self.check_everything)

        # Wait for the desktop process
        self.wait_for_desktop()

        self.info("AcTor started.")
        loop.run()
