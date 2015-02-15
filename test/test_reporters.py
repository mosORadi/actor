from datetime import datetime
from test.base import ReporterTestCase


class TimeReporterTest(ReporterTestCase):
    class_name = 'TimeReporter'
    module_name = 'time'

    def test_time_reporter(self):
        self.assertEqual(self.plugin.report(), datetime.now().strftime("%H.%M"))


class TimeActiveWindowNameReporter(ReporterTestCase):
    class_name = 'ActiveWindowNameReporter'
    module_name = 'active_window_name'

    def test_active_window_name_reporter(self):
        self.plugin.report()
