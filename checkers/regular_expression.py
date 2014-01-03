from plugins import IChecker

import re

class RegularExpressionChecker(IChecker):
    """
    Evaluates whether the input contains at least one
    occurence of the pattern searched for.

    Expects reports:
      - string - Input string

    Options:
      - regexp : The string containing the regular expression
    """

    export_as = 'regular_expression'
    required_plugin_options = ['regexp']

    def __init__(self, **options):
        super(RegularExpressionChecker, self).__init__(**options)
        self.re = re.compile(self.options.get('regexp'))

    def check(self, **reports):
        return re.search(self.re, reports['string'])
