from datetime import datetime
from test.base import ReporterTestCase


class TimeReporterTest(ReporterTestCase):
    class_name = 'TimeReporter'
    module_name = 'time'

    def test_time_reporter(self):
        time = self.plugin.report()
        assert time == datetime.now().strftime("%H.%M")


class ActiveWindowNameReporterTest(ReporterTestCase):
    class_name = 'ActiveWindowNameReporter'
    module_name = 'active_window_name'

    def test_active_window_name_reporter(self):
        window = self.plugin.report()
        assert type(window) == str
        assert len(window) > 0


class ActiveWindowPidReporterTest(ReporterTestCase):
    class_name = 'ActiveWindowPidReporter'
    module_name = 'active_window_pid'

    def test_active_window_pid_reporter(self):
        pid = self.plugin.report()
        assert type(pid) == int


class ActiveWindowProcessNameReporterTest(ReporterTestCase):
    class_name = 'ActiveWindowProcessNameReporter'
    module_name = 'active_window_process_name'

    def test_active_window_pid_reporter(self):
        window_name = self.plugin.report()
        assert type(window_name) == str
