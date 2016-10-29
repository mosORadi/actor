import os

from actor.core.plugins import Reporter
from actor.core.config import config


class TrackReporter(Reporter):

    identifier = 'track'

    def run(self, ident, key):
        # pylint: disable=arguments-differ

        filepath = os.path.join(config.CONFIG_DIR, ident + ".act")
        try:
            with open(filepath, 'r') as fil:
                data = fil.readlines()

                for line in data:
                    if line.startswith(key):
                        return line.split(':')[1].strip()
        except IOError as exc:
            self.debug("Encountered an IOError, %s" % str(exc))
