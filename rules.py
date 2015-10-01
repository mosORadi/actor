from plugins import PluginMount, Plugin


class PythonRule(Plugin):
    """Performs custom python rule"""

    __metaclass__ = PluginMount

    def run(self):
        """Evaluates custom python rule"""
        pass
