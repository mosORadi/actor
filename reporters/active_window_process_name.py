from active_window_pid import ActiveWindowPidReporter

class ActiveWindowProcessNameReporter(ActiveWindowPidReporter):

    export_as = 'active_window_process_name'

    def report(self):
        pid = super(ActiveWindowProcessNameReporter, self).report()
        name = None

        if pid is None:
            return ''

        # First try to read the cmdline
        try:
            with open('/proc/%d/cmdline' % pid, 'r') as f:
                name = f.read().strip()
        except IOError:
            pass

        # Fallback to comm
        if name is None:
            try:
                with open('/proc/%d/comm' % pid, 'r') as f:
                    name = f.read().strip()
            except IOError:
                pass

        return name or ''
