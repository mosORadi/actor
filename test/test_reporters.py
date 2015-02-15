from datetime import datetime
import tempfile
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

    def test_active_window_process_name_reporter(self):
        process_name = self.plugin.report()
        assert type(process_name) == str
        assert len(process_name) > 0


class FileContentReporterTest(ReporterTestCase):
    class_name = 'FileContentReporter'
    module_name = 'file_content'

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.options.update({'path': self.tempfile.name})

        self.tempfile.write("aaa\n")
        self.tempfile.write("bbb\n")
        self.tempfile.write("ccc\n")
        self.tempfile.flush()

        super(FileContentReporterTest, self).setUp()

    def test_file_content_reporter(self):
        file_content = self.plugin.report()
        assert type(file_content) == str
        assert len(file_content) > 0
        assert "aaa" in file_content
        assert "bbb" in file_content
        assert "ccc" in file_content
