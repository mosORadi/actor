from actor.core.plugins import Reporter, DBusMixin


class SessionIdleTimeReporter(DBusMixin, Reporter):
    """
    Returns time, in minutes, for which the current session has been idle
    (no mouse movement, no keyboard presses).
    """

    identifier = 'desktop_session_idle_time'

    bus_name = "org.freedesktop.ScreenSaver"
    object_path = "/org/freedesktop/ScreenSaver"

    def run(self):
        return self.interface.GetSessionIdleTime() / 60000.0


class SessionLockedReporter(DBusMixin, Reporter):
    """
    Returns True if current desktop session is locked, False otherwise.
    """

    identifier = 'desktop_session_locked'

    bus_name = "org.freedesktop.ScreenSaver"
    object_path = "/org/freedesktop/ScreenSaver"

    def run(self):
        return self.interface.GetActive() == 1


class SessionActiveReporter(DBusMixin, Reporter):
    """
    Returns time, in minutes, for which the screen is locked.
    """

    identifier = 'desktop_session_locked_time'

    bus_name = "org.freedesktop.ScreenSaver"
    object_path = "/org/freedesktop/ScreenSaver"

    def run(self):
        return self.interface.GetActiveTime() / 60000.0
