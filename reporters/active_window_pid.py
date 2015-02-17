import wnck
import gtk
import psutil
from util import run

from plugins import IReporter


class ActiveWindowPidReporter(IReporter):

    export_as = 'active_window_pid'

    def get_using_wnck(self):
        pid = None

        while gtk.events_pending():
            gtk.main_iteration(False)

        screen = wnck.screen_get_default()
        screen.force_update()


        if screen:
            active_window = screen.get_active_window()
            if active_window:
                pid = active_window.get_pid()

        return int(pid)

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
        except:
            return False

    def report(self):
        pid = self.get_using_wnck()

        if not self.verify_pid(pid):
            pid = self.get_using_xprop()

        return pid
