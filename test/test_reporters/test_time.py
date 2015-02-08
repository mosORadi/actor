from unittest import TestCase
from datetime import datetime
from reporters.time import TimeReporter

class TimeReporterTest(TestCase):
    def test_time_reporter(self):
        time = TimeReporter(activity_name="test")
        self.assertEqual(time.report(), datetime.now().strftime("%H.%M"))
