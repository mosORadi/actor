from plugins import Reporter, Checker, Fixer, Activity, Flow

class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class PluginCache(object):
    """
    Provides an interface to the plugins of a particular type (identified by
    given PluginMount class).

    Never initializes the same class twice, once initialized, class instance
    stays in the cache.

    PluginCache tries to be smart and it will not try to evaluate the same
    plugin when called with the same arguments as it has been called before.
    This behaviour is leveraged by Actor to avoid redundat multiple
    re-evaluations of the same plugin. It can be altered, however, with the
    following two flags:

      * stateless: Plugin is marked as stateless, i.e. its run() method
                   does not keep any state inside the plugin object.
                   If plugin is stateless, its instance can be shared between
                   multiple Rules.
      * side_effects: Plugin has side effects, i.e. it makes sense to
                      re-evaluate it when called with the same arguments.
    """

    def __init__(self, mount, context):
        self.mount = mount
        self.context = context
        self.cache = {}
        self.instances = {}

    @property
    def plugins(self):
        return {
            plugin_class.identifier: plugin_class
            for plugin_class in self.mount.plugins
        }

    def get(self, identifier, args=None, kwargs=None, rule_name=None):
        """
        Obtain a result from the given plugin. If the plugin is stateless
        and has no side effects, it will be returned from the result cache.

        Otherwise, the plugin will be re-evaluated and the result will be
        returned.
        """

        args = args or tuple()
        kwargs = kwargs or dict()

        plugin_class = self.get_plugin(identifier)

        # Instances can be shared, and be kept for the time the Actor runs,
        # however, in the case of stateful plugins, we need to make sure
        # we create a separate instance per rule.

        if plugin_class.stateless and not plugin_class.side_effects:
            # Can be cached (per loop).
            return self.result_from_cache(identifier, args, kwargs)
        elif plugin_class.stateless:
            # It has side-effects, hence we need to run it.
            return self.run_plugin_instance(identifier, args, kwargs)
        else:
            if rule_name is None:
                raise ValueError("Only stateless plugins can be accessed "
                                 "from workers.")
            # It is stateful, hence cannot be shared between modules.
            # Modify instance name to include the rule name.
            instance_id = '{0}_{1}'.format(identifier, rule_name)
            return self.run_plugin_instance(instance_id, args, kwargs,
                                            class_identifier=identifier)

    def get_plugin(self, identifier):
        """
        Returns a plugin class identified by the given identifier.
        """

        try:
            return self.plugins[identifier]
        except KeyError:
            pass
            # TODO: Raise an error, no such plugin available

    def get_plugin_instance(self, identifier, class_identifier=None):
        """
        Returns a plugin instance corresponding to the given class identifier.
        If case the class identifier is None, identifier will be used. This is
        useful for the stateful plugins, where an unique identifier is
        constructed for each Rule.

        Makes sure plugins are initialized only once.
        """

        instance = self.instances.get(identifier)

        if instance is None:
            plugin_class = self.get_plugin(class_identifier or identifier)
            self.instances[identifier] = instance = plugin_class(self.context)

        return instance

    def result_from_cache(self, identifier, args, kwargs):
        """
        Only for stateless plugins with no side-effects. Gets the result from
        evaluation of the plugin with the corresponding identifier.

        Makes sure plugins are evaluated only once per (args, kwargs) tuple.
        """
        # Note: Only for stateless and no side-effects

        key = (identifier, args, HashableDict(**kwargs))
        value = self.cache.get(key)

        if value is None:
            plugin_instance = self.get_plugin(identifier)(self.context)
            self.cache[key] = value = plugin_instance.evaluate(*args, **kwargs)

        return value

    def run_plugin_instance(self, identifier, args, kwargs, class_identifier=None):
        """
        Evaluates the plugin instance corresponding to the given identifier
        and returns the result.
        """

        instance = self.get_plugin_instance(identifier, class_identifier)
        return instance.run(*args, **kwargs)

    def clear(self):
        """
        Clears the result cache. Instance cache is preserved.
        """

        self.cache.clear()

    def __iter__(self):
        """
        Iterates over all the instances of the plugins available to the cache.
        """

        for plugin_class in self.plugins:
            yield self.get_plugin_instance(plugin_class.identifier, None)


class PluginFactory(object):

    def __init__(self, mount, context):
        self.mount = mount
        self.context = context

    @property
    def plugins(self):
        return {
            plugin_class.identifier: plugin_class
            for plugin_class in self.mount.plugins
        }

    def make(self, identifier, args=None, kwargs=None):
        """
        Returns an instance of a particular plugin given by identifier.
        """

        args = args or tuple()
        kwargs = kwargs or dict()

        # Create an instance of the plugin class and return it
        plugin_class = self.get_plugin(identifier)
        return plugin_class(self.context, *args, **kwargs)

    def get_plugin(self, identifier):
        try:
            return self.plugins[identifier]
        except KeyError:
            pass
            # TODO: Raise an error, no such plugin available


class Context(object):

    def __init__(self):
        self.rules = []
        self.activity = None
        self.flow = None

        self.reporters = PluginCache(Reporter, self)
        self.checkers = PluginCache(Checker, self)
        self.fixers = PluginCache(Fixer, self)

        self.reporter_factory = PluginFactory(Reporter, self)
        self.checker_factory = PluginFactory(Checker, self)
        self.fixer_factory = PluginFactory(Fixer, self)

        self.activities = PluginFactory(Activity, self)
        self.flows = PluginFactory(Flow, self)
