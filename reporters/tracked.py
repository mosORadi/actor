import os

from plugins import Reporter
from config import CONFIG_DIR


class TrackReporter(Reporter):

    identifier = 'track'

    def run(self, ident, key):
        filepath = os.path.join(CONFIG_DIR, ident + ".act")
        try:
            with open(filepath, 'r') as fil:
                data = fil.readlines()

                for line in data:
                    if line.startswith(key):
                        return line.split(':')[1].strip()
        except IOError as exc:
            self.debug("Encountered an IOError, %s" % str(exc))
