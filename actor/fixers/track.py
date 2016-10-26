import os

from plugins import Fixer
from config import CONFIG_DIR


class TrackFixer(Fixer):

    identifier = 'track'

    def run(self, ident, key, value):
        # pylint: disable=arguments-differ

        filepath = os.path.join(CONFIG_DIR, ident + ".act")
        with open(filepath, 'a') as fil:
            fil.write("{0}: {1}\n".format(key, value))
