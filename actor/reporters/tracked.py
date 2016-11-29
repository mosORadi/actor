import os

from actor.core.plugins import Reporter
from actor.core.config import config


class TrackReporter(Reporter):

    identifier = 'track'

    def run(self, ident, key):
        # pylint: disable=arguments-differ
        return self.context.backend.get(ident, key)
