from plugins import Fixer
from util import run


class SpeakFixer(Fixer):
    """
    Simple fixer that suspends your workstation.
    """

    identifier = "speak"

    def run(self, text, language='en'):
        # pylint: disable=arguments-differ

        run(['espeak', '-v', language, text])
