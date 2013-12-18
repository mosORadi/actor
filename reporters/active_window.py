import wnck
import gtk
import psi.process

from plugins import IReporter


class ActiveWindowReporter(IReporter):

    export_as = 'active_window'

    def report(self):
        name = None
        process_name = None
        process_command = None

        screen = wnck.screen_get_default()
        screen.force_update()
        while gtk.events_pending():
            gtk.main_iteration()

        if screen:
            active_window = screen.get_active_window()

            if active_window:
                name = active_window.get_name()
                pid = active_window.get_pid()

                process_table = psi.process.ProcessTable()
                process_name = process_table.get(pid).name
                process_command = process_table.get(pid).command

        return (name, process_name, process_command)
