from active_window_pid import ActiveWindowPidReporter

class ActiveWindowProcessNameReporter(ActiveWindowPidReporter):

    export_as = 'active_window_process_name'

    def report(self):
        pid = super(ActiveWindowProcessNameReporter, self).report()
        with open('/proc/%d/comm' % pid, 'r') as f:
            name = f.read()
        return name
