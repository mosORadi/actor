from test.base import CheckerTestCase

from util import convert_timestamp


class RegularExpressionCheckerTest(CheckerTestCase):
    class_name = 'RegularExpressionChecker'
    module_name = 'regular_expression'

    def test_regular_expression_checker(self):
        assert self.plugin.run(regexp='ratata', string="potato") == False
        assert self.plugin.run(regexp='ratata', string="jiglypuff") == False
        assert self.plugin.run(regexp='ratata', string="nasty ratata") == True


class TimeIntervalCheckerTest(CheckerTestCase):
    class_name = 'TimeIntervalChecker'
    module_name = 'time_interval'

    def test_time_interval_checker(self):
        self.context.reporters['time'] = convert_timestamp('18.00')
        assert self.plugin.run(start='18.00', end='19.00') == True

        self.context.reporters['time'] = convert_timestamp('18.50')
        assert self.plugin.run(start='18.00', end='19.00') == True

        self.context.reporters['time'] = convert_timestamp('19.00')
        assert self.plugin.run(start='18.00', end='19.00') == False

        self.context.reporters['time'] = convert_timestamp('17.30')
        assert self.plugin.run(start='18.00', end='19.00') == False

    def test_time_interval_checker_overnight(self):
        self.context.reporters['time'] = convert_timestamp('17.00')
        assert self.plugin.run(start='18.00', end='05.00') == False

        self.context.reporters['time'] = convert_timestamp('18.00')
        assert self.plugin.run(start='18.00', end='05.00') == True

        self.context.reporters['time'] = convert_timestamp('18.50')
        assert self.plugin.run(start='18.00', end='05.00') == True

        self.context.reporters['time'] = convert_timestamp('19.00')
        assert self.plugin.run(start='18.00', end='05.00') == True

        self.context.reporters['time'] = convert_timestamp('00.00')
        assert self.plugin.run(start='18.00', end='05.00') == True

        self.context.reporters['time'] = convert_timestamp('04.59')
        assert self.plugin.run(start='18.00', end='05.00') == True

        self.context.reporters['time'] = convert_timestamp('05.00')
        assert self.plugin.run(start='18.00', end='05.00') == False

        self.context.reporters['time'] = convert_timestamp('09.00')
        assert self.plugin.run(start='18.00', end='05.00') == False
