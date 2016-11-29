import os

from actor.core.plugins import Fixer
from actor.core.config import config


class TrackFixer(Fixer):

    identifier = 'track'

    def run(self, ident, key, value):
        # pylint: disable=arguments-differ
        return self.context.backend.put(ident, key, value)
