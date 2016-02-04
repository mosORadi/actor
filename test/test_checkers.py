from test.base import CheckerTestCase


class RegularExpressionCheckerTest(CheckerTestCase):
    class_name = 'RegularExpressionChecker'
    module_name = 'regular_expression'

    def setUp(self):
        self.options.update({'regexp': 'ratata'})
        super(RegularExpressionCheckerTest, self).setUp()

    def test_regular_expression_checker(self):
        assert self.plugin.check(string="potato") == False
        assert self.plugin.check(string="jiglypuff") == False
        assert self.plugin.check(string="nasty ratata defeated") == True


class TimeIntervalCheckerTest(CheckerTestCase):
    class_name = 'TimeIntervalChecker'
    module_name = 'time_interval'
    options = {'start': "18.00", 'end': "19.00"}

    def test_time_interval_checker(self):
        assert self.plugin.check(time='18.50') == True
        assert self.plugin.check(time='18.00') == True
        assert self.plugin.check(time='19.00') == False
        assert self.plugin.check(time='17.00') == False

    def test_time_interval_checker_overnight(self):
        self.initialize(start="18.00", end="05.00")
        assert self.plugin.check(time='17.00') == False
        assert self.plugin.check(time='18.00') == True
        assert self.plugin.check(time='18.50') == True
        assert self.plugin.check(time='19.00') == True
        assert self.plugin.check(time='00.00') == True
        assert self.plugin.check(time='04.59') == True
        assert self.plugin.check(time='05.00') == False
        assert self.plugin.check(time='09.00') == False
