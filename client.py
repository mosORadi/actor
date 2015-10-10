import argparse
from plugins import DBusMixin

class CLIClient(DBusMixin):

    bus_name = "org.freedesktop.Actor"
    object_path = "/Actor"

    commands = ('activity-start', 'activity-stop', 'flow-start', 'flow-stop')

    def command_activity_start(self, identifier):
        self.interface.SetActivity(identifier)
        print("Activity %s started." % identifier)

    def command_activity_stop(self):
        self.interface.UnsetActivity()
        print("Activity stopped.")

    def command_flow_start(self, identifier):
        self.interface.SetFlow(identifier)
        print("Flow %s started." % identifier)

    def command_flow_stop(self):
        self.interface.UnsetFlow()
        print("Flow %s stopped.")

    def process_args(self):
        parser = argparse.ArgumentParser("CLI interface to Actor daemon")
        parser.add_argument('command', type=str, choices=self.commands)
        parser.add_argument('options', nargs='*', type=str)

        args = parser.parse_args()
        return args

    def run_command(self, command, options):
        method_name = "command_" + command.replace('-', '_')
        method = getattr(self, method_name)
        method(*options)

    def main(self):
        args = self.process_args()
        self.run_command(args.command, args.options)

if __name__ == "__main__":
    client = CLIClient()
    client.main()
