import wnck
import gtk
import psutil
from util import run

from plugins import Reporter


class ActiveWindowNameReporter(Reporter):

    export_as = 'active_window_name'

    def get_active_window(self):

        while gtk.events_pending():
            gtk.main_iteration()

        screen = wnck.screen_get_default()
        screen.force_update()

        if screen:
            return screen.get_active_window()

    def report(self):
        window = self.get_active_window()

        if window:
            return window.get_name()


class ActiveWindowPidReporter(ActiveWindowNameReporter):

    export_as = 'active_window_pid'

    def get_using_wnck(self):
        window = self.get_active_window()

        if window:
            return window.get_pid()

    def get_using_xprop(self):
        output = run(['xprop', '-root'])[0]

        if output is None:
            return None

        candidate_lines = [line for line in output.splitlines()
                          if line.startswith('_NET_ACTIVE_WINDOW')]

        if len(candidate_lines) == 1:
            window_id = candidate_lines[0].split()[-1]

            if not window_id.startswith('0x'):
                return None

            output = run(['xprop', '-id', window_id])[0]
            candidate_lines = [line for line in output.splitlines()
                               if line.startswith('_NET_WM_PID')]

            if len(candidate_lines) == 1:
                return int(candidate_lines[0].split()[-1])

    def verify_pid(self, pid):
        try:
            psutil.Process(pid)
            return True
        except Exception:
            return False

    def report(self):
        pid = self.get_using_wnck()

        if not self.verify_pid(pid):
            pid = self.get_using_xprop()

        return pid


class ActiveWindowProcessNameReporter(ActiveWindowPidReporter):

    export_as = 'active_window_process_name'

    def report(self):
        pid = super(ActiveWindowProcessNameReporter, self).report()

        if pid is None:
            return None

        # First try to read the cmdline
        try:
            with open('/proc/%d/cmdline' % pid, 'r') as f:
                return f.read().strip()
        except IOError:
            pass

        # Fallback to comm
        try:
            with open('/proc/%d/comm' % pid, 'r') as f:
                return f.read().strip()
        except IOError:
            pass
