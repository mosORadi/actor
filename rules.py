import collections
import logging
import re
import yaml

from plugins import PluginMount, Reporter, Checker, Fixer


class PythonRule(object):
    """Performs custom python rule"""

    __metaclass__ = PluginMount

    def run(self):
        """Evaluates custom python rule"""
        pass
