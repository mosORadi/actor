import collections
import logging
import re
import yaml

from plugins import PluginMount, Reporter, Checker, Fixer


class PythonRule(object):
    """Performs custom python rule"""

    __metaclass__ = PluginMount

    def __init__(self, context):
        self.context = context

    def report(self, identifier, *args, **kwargs):
        return self.context.reporters.get(identifier, *args, **kwargs)

    def check(self, identifier, *args, **kwargs):
        return self.context.checkers.get(identifier, *args, **kwargs)

    def fix(self, identifier, *args, **kwargs):
        return self.context.fixers.get(identifier, *args, **kwargs)

    def run(self):
        """Evaluates custom python rule"""
        pass
