from plugins import Checker

import re

class RegularExpressionChecker(Checker):
    """
    Evaluates whether the input contains at least one
    occurence of the pattern searched for.

    Expects reports:
      - string - Input string

    Options:
      - regexp : The string containing the regular expression
    """

    identifier = 'regular_expression'
    required_plugin_options = ['regexp']

    def __init__(self, **options):
        super(RegularExpressionChecker, self).__init__(**options)
        self.re = re.compile(self.options.get('regexp'))

    def check(self, **reports):
        return bool(re.search(self.re, reports['string'] or ''))
