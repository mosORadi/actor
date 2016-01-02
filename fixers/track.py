import os

from plugins import Fixer
from config import CONFIG_DIR


class TrackFixer(Fixer):

    identifier = 'track'

    def run(self, ident, key, value):
        filepath = os.path.join(CONFIG_DIR, ident + ".act")
        with open(filepath, 'a') as f:
            f.write("{0}: {1}\n".format(key, value))
