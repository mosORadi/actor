import wnck
import gtk
import psi.process

from plugins import IReporter


class ActiveWindowReporter(IReporter):

    def report(self):
        screen = wnck.screen_get_default()
        screen.force_update()
        while gtk.events_pending():
            gtk.main_iteration()

        active_window = screen.get_active_window()
        process_table = psi.process.ProcessTable()

        name = active_window.get_name()
        process_name = process_table.get(active_window.get_pid()).name
        process_command = process_table.get(active_window.get_pid()).command

        return (name, process_name, process_command)
