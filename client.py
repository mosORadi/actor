#!/usr/bin/python -B
from __future__ import print_function

import argparse
import sys
from plugins import DBusMixin
from util import dbus_error_handler


class CLIClient(DBusMixin):

    bus_name = "org.freedesktop.Actor"
    object_path = "/Actor"

    commands = (
        'activity-start',
        'activity-stop',
        'activity-next',
        'flow-start',
        'flow-stop',
        'pause',
        'report')

    @dbus_error_handler
    def command_activity_start(self, identifier):
        self.interface.SetActivity(identifier)
        print(u"Activity %s started." % identifier)

    @dbus_error_handler
    def command_activity_stop(self):
        self.interface.UnsetActivity()
        print(u"Activity stopped.")

    @dbus_error_handler
    def command_activity_next(self):
        self.interface.NextActivity()
        print(u"Next activity started.")

    @dbus_error_handler
    def command_flow_start(self, identifier):
        self.interface.SetFlow(identifier)
        print(u"Flow %s started." % identifier)

    @dbus_error_handler
    def command_flow_stop(self):
        self.interface.UnsetFlow()
        print(u"Flow stopped.")

    @dbus_error_handler
    def command_report(self, identifier):
        result = self.interface.Report(identifier)
        print(u"{0}: {1}".format(identifier, result))

    @dbus_error_handler
    def command_pause(self, minutes):
        self.interface.Pause(int(minutes))
        print(u"Actor paused for {0} minutes.".format(minutes))

    def process_args(self):
        parser = argparse.ArgumentParser("CLI interface to Actor daemon")
        parser.add_argument('command', type=str, choices=self.commands)
        parser.add_argument('options', nargs='*', type=str)

        args = parser.parse_args()
        return args

    def run_command(self, command, options):
        method_name = "command_" + command.replace('-', '_')
        method = getattr(self, method_name, None)

        # pylint: disable=protected-access
        args_expected = method._co_argcount - 1

        if method is None:
            sys.exit("Command '{0}' not found.".format(command))
        else:
            if len(options) != args_expected:
                sys.exit("Invalid number of arguments, expected %d, got %d."
                         % (args_expected, len(options)))
            method(*options)

    def validate_actor(self):
        if self.interface is None:
            sys.exit("Actor is not running.")

    def main(self):
        self.validate_actor()
        args = self.process_args()
        self.run_command(args.command, args.options)


def main():
    client = CLIClient()
    client.main()


if __name__ == "__main__":
    main()
