import datetime

from plugins import Fixer, DBusMixin
from util import run, convert_timestamp


class SpeakFixer(Fixer):
    """
    Simple fixer that suspends your workstation.
    """

    identifier = "speak"

    def run(self, text, language='en'):
        # pylint: disable=arguments-differ

        run(['espeak', '-v', language, text])
