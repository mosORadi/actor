import wnck
import gtk

from plugins import IReporter


class ActiveWindowPidReporter(IReporter):

    export_as = 'active_window_pid'

    def report(self):
        pid = None

        screen = wnck.screen_get_default()
        screen.force_update()
        while gtk.events_pending():
            gtk.main_iteration()

        if screen:
            active_window = screen.get_active_window()

            if active_window:
                pid = active_window.get_pid()

        return pid
