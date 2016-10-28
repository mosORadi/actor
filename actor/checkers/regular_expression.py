import re

from plugins import Checker


class RegularExpressionChecker(Checker):
    """
    Evaluates whether the input contains at least one occurence of the
    pattern searched for.

    Expects following keyword arguments:
      - regexp - Regular expression
      - string - Input string tested to match the regular expression
    """

    identifier = 'regular_expression'

    def run(self, regexp, string):
        # pylint: disable=arguments-differ

        return bool(re.search(regexp, string or ''))
