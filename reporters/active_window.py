import wnck
import gtk
import psutil
from util import run

from plugins import Reporter


class ActiveWindowNameReporter(Reporter):
    """
    Returns a string containing the title of the active window.

    If no active window could be detected, returns None.
    """

    identifier = 'active_window_name'

    def get_active_window(self):
        """
        Returns the active window object.
        """

        while gtk.events_pending():
            gtk.main_iteration()

        screen = wnck.screen_get_default()
        screen.force_update()

        if screen:
            return screen.get_active_window()

    def run(self):
        window = self.get_active_window()

        if window:
            return window.get_name()


class ActiveWindowPidReporter(ActiveWindowNameReporter):
    """
    Returns the PID of the process the active window belongs to.

    If no active window could be detected, returns None.
    """

    identifier = 'active_window_pid'

    def get_pid_using_wnck(self):
        """
        Obtains the PID of the active window using wnck bindings.

        Returns None if active window could not be detected.
        """

        window = self.get_active_window()

        if window:
            return window.get_pid()

    def get_pid_using_xprop(self):
        """
        Obtains the PID of the active window using xprop utility, if available.

        Returns None if active window could not be detected.
        """

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
        """
        Verifies if a PID belongs to any active process.
        """

        try:
            psutil.Process(pid)
            return True
        except Exception:
            return False

    def run(self):
        """
        Obtains the active window PID using wnck, with fallback to xprop.
        """

        pid = self.get_pid_using_wnck()

        if not self.verify_pid(pid):
            pid = self.get_pid_using_xprop()

        return pid


class ActiveWindowProcessReporter(ActiveWindowPidReporter):
    """
    Returns the process belonging to the active window using the
    psutil.Process abstraction.
    """

    identifier = 'active_window_process'

    def run(self):
        pid = super(ActiveWindowProcessReporter, self).run()

        if pid is None:
            return None

        try:
            return psutil.Process(pid)
        except Exception:
            return None


class ActiveWindowProcessNameReporter(ActiveWindowPidReporter):
    """
    Returns the command name of the process the active window belongs to.

    Uses information from the /proc/<pid>/cmdline, with fallback to
    /proc/<pid>/comm.

    If no active window could be detected, returns None.
    """

    identifier = 'active_window_process_name'

    def run(self):
        pid = super(ActiveWindowProcessNameReporter, self).run()

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
