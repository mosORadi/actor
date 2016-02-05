import datetime
import subprocess
import tempfile
import os
import dbus.mainloop.glib

from tests.base import ReporterTestCase
from util import run
from time import sleep
from tasklib import TaskWarrior, Task


class TimeReporterTest(ReporterTestCase):
    class_name = 'TimeReporter'
    module_name = 'time'

    def test_time_reporter(self):
        reported_time = self.plugin.run()
        actual_time = datetime.datetime.now()

        assert actual_time - reported_time < datetime.timedelta(seconds=1)


class WeekdayReporterTest(ReporterTestCase):
    class_name = 'WeekdayReporter'
    module_name = 'time'

    def test_weekday_reporter(self):
        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        output, _, _ = run(['date', '+%w'])
        system_day = weekdays[int(output.strip())]

        day = self.plugin.run()
        assert day == system_day


class ActiveWindowReporterTest(ReporterTestCase):

    def setUp(self):
        super(ActiveWindowReporterTest, self).setUp()
        self.close('gedit')
        self.close('Calculator')
        sleep(0.5)
        subprocess.Popen(['gedit'])
        subprocess.Popen(['gnome-calculator'])
        sleep(0.5)

    def tearDown(self):
        self.close('gedit')
        self.close('Calculator')
        sleep(0.5)

    def activate(self, title_part):
        output = run(['xdotool', 'search', '--name', title_part])[0]
        window_ids = output.strip().splitlines()
        for window_id in window_ids:
            errors = run(['xdotool', 'windowactivate', window_id])[1]
        sleep(0.5)

    def close(self, title_part):
        output = run(['xdotool', 'search', '--name', title_part])[0]
        window_ids = output.strip().splitlines()
        for window_id in window_ids:
            errors = run(['xdotool', 'windowkill', window_id])[1]
        sleep(0.5)

class ActiveWindowNameReporterTest(ActiveWindowReporterTest):
    class_name = 'ActiveWindowNameReporter'
    module_name = 'active_window'

    def test_active_window_name_reporter(self):
        self.activate('gedit')
        window = self.plugin.run()
        assert type(window) == str
        assert 'gedit' in window

    def test_active_window_name_reporter_changing(self):
        self.activate('gedit')
        window = self.plugin.run()
        assert type(window) == str
        assert 'gedit' in window

        self.activate('Calculator')
        window = self.plugin.run()
        assert type(window) == str
        # The title depends on the package version
        assert 'Calculator' in window or 'gnome-calculator' in window

        self.activate('gedit')
        window = self.plugin.run()
        assert type(window) == str
        assert 'gedit' in window

class ActiveWindowPidReporterTest(ActiveWindowReporterTest):
    class_name = 'ActiveWindowPidReporter'
    module_name = 'active_window'

    def get_window_pid(self, title_part):
        self.activate(title_part)
        output = run(['xdotool', 'getwindowfocus', 'getwindowpid'])[0]
        xdopid = int(output.strip())
        return xdopid

    def setUp(self):
        super(ActiveWindowPidReporterTest, self).setUp()
        self.gedit_pid = self.get_window_pid('gedit')
        self.calc_pid = self.get_window_pid('Calculator')

    def test_active_window_pid_reporter(self):
        self.activate('gedit')
        pid = self.plugin.run()
        assert type(pid) == int
        assert pid == self.gedit_pid

    def test_active_window_pid_reporter_changing(self):
        self.activate('gedit')
        pid = self.plugin.run()
        assert type(pid) == int
        assert pid == self.gedit_pid

        self.activate('Calculator')
        pid = self.plugin.run()
        assert type(pid) == int
        assert pid == self.calc_pid

        self.activate('gedit')
        pid = self.plugin.run()
        assert type(pid) == int
        assert pid == self.gedit_pid


class ActiveWindowProcessNameReporterTest(ActiveWindowReporterTest):
    class_name = 'ActiveWindowProcessNameReporter'
    module_name = 'active_window'

    def test_active_process_name_reporter(self):
        self.activate('gedit')
        process = self.plugin.run()
        assert type(process) == str
        assert 'gedit' in process

    def test_active_process_name_reporter_changing(self):
        self.activate('gedit')
        process = self.plugin.run()
        assert type(process) == str
        assert 'gedit' in process

        self.activate('Calculator')
        process = self.plugin.run()
        assert type(process) == str
        assert 'gnome-calculator' in process

        self.activate('gedit')
        process = self.plugin.run()
        assert type(process) == str
        assert 'gedit' in process

class FileContentReporterTest(ReporterTestCase):
    class_name = 'FileContentReporter'
    module_name = 'file_content'

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()

        self.tempfile.write("aaa\n")
        self.tempfile.write("bbb\n")
        self.tempfile.write("ccc\n")
        self.tempfile.flush()

        super(FileContentReporterTest, self).setUp()

    def test_file_content_reporter(self):
        file_content = self.plugin.run(path=self.tempfile.name)
        assert type(file_content) == str
        assert len(file_content) > 0
        assert "aaa" in file_content
        assert "bbb" in file_content
        assert "ccc" in file_content


class HamsterActivityReporterTest(ReporterTestCase):
    class_name = 'HamsterActivityReporter'
    module_name = 'hamster'

    def setUp(self):
        run(['killall', 'hamster-service'])
        self.hamster_db_file = os.path.expanduser("~/.local/share/hamster-applet/hamster.db")

        if os.path.isfile(self.hamster_db_file):
            os.rename(self.hamster_db_file, self.hamster_db_file + "-backup-actor-tests")

        run(['hamster', 'start', "something@Home"])
        sleep(1)
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        super(HamsterActivityReporterTest, self).setUp()

    def tearDown(self):
        run(['killall', 'hamster-service'])

        if os.path.isfile(self.hamster_db_file + "-backup-actor-tests"):
            os.rename(self.hamster_db_file + "-backup-actor-tests", self.hamster_db_file)

        run(['hamster', 'current'])

    def test_correct_activity(self):
        assert self.plugin.run() == "something@Home"

        run(['hamster', 'start', 'other@Home'])
        assert self.plugin.run() == "other@Home"


class TaskWarriorReporterTest(ReporterTestCase):
    class_name = 'TaskWarriorReporter'
    module_name = 'taskwarrior'

    def setUp(self):
        data_dir = tempfile.mkdtemp()
        self.warrior = TaskWarrior(data_location=data_dir)
        self.tw_options = {'data_location': data_dir}
        super(ReporterTestCase, self).setUp()

    def test_empty_tasklist(self):
        assert len(self.plugin.run(warrior_options=self.tw_options)) == 0

    def test_correct_description(self):
        Task(self.warrior, description="test").save()
        assert repr(self.plugin.run(warrior_options=self.tw_options)) == '[test]'

    def test_filtered_description(self):
        Task(self.warrior, project="work", description="work task1").save()
        Task(self.warrior, project="home", description="home task1").save()

        result = self.plugin.run(
            warrior_options=self.tw_options,
            taskfilter={'project': 'work'}
        )
        assert repr(result) == '[work task1]'
