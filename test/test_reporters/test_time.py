from datetime import datetime
from test.base import ReporterTestCase

class TimeReporterTest(ReporterTestCase):
    class_name = 'TimeReporter'
    module_name = 'time'

    def test_time_reporter(self):
        self.assertEqual(self.plugin.report(), datetime.now().strftime("%H.%M"))
