import wnck
import gtk

from plugins import IReporter


class ActiveWindowNameReporter(IReporter):

    export_as = 'active_window_name'

    def report(self):
        name = None

        while gtk.events_pending():
            gtk.main_iteration()

        screen = wnck.screen_get_default()
        screen.force_update()

        if screen:
            active_window = screen.get_active_window()

            if active_window:
                name = active_window.get_name()

        return name or ''
