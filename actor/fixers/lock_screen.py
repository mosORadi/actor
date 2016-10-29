from actor.core.plugins import Fixer, DBusMixin


class LockScreenFixer(DBusMixin, Fixer):
    """
    Simple fixer that locks your screen.
    """

    identifier = "lock_screen"

    bus_name = 'org.freedesktop.ScreenSaver'
    object_path = '/ScreenSaver'

    def run(self):
        if self.interface and not self.interface.GetActive():
            self.interface.Lock()
