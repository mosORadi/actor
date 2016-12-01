import dbus
import time
import threading
import util

import logger

# This file contains definitions of plugin classes, most of
# which intentionally do not implement their abstract method
# contracts.
# pylint: disable=abstract-method


class NoSuchPlugin(Exception):
    """
    Raised when a plugin could not be found.
    """
    pass


class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        super(PluginMount, cls).__init__(name, bases, attrs)

        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            # System generic plugin classes are marked with 'noplugin'
            # attribute. We do not want to mix those with user plugin
            # instances, so let's skip them
            if 'noplugin' not in cls.__dict__:
                cls.plugins.append(cls)

class PersistentStateMixin(object):
    """
    Provides store/restoration capabilities for plugins that want to keep state
    across restarts.
    """

    def store(self):
        """
        Encodes attributes marked as persistent by self.persistent_attrs
        attribute.
        """

        data_dict = {
            attribute: getattr(self, attribute)
            for attribute in self.persistent_attrs
        }

        return util.json_encode(data_dict)

    @staticmethod
    def restore(data, mount, context):
        """
        Given a stored class persistent dict, reinitializes the class and
        restores the stored attributes to it.
        """

        data_dict = util.json_decode(data)

        # Reinitialize the class
        identifier = data_dict.pop('identifier')
        cls = mount.get_plugin(identifier)
        instance = cls(context, setup=False)

        # Restore the attributes
        for attribute, value in data_dict.items():
            setattr(instance, attribute, value)

        return instance


class Plugin(logger.LoggerMixin):

    def __init__(self, context):
        self.context = context

    # Convenience function for accessing worker modules
    def report(self, identifier, *args, **kwargs):
        return self.context.reporters.get(identifier, args, kwargs)

    def check(self, identifier, *args, **kwargs):
        return self.context.checkers.get(identifier, args, kwargs)

    def fix(self, identifier, *args, **kwargs):
        return self.context.fixers.get(identifier, args, kwargs)

    def factory_report(self, identifier, *args, **kwargs):
        return self.context.reporter_factory.make(identifier, args, kwargs)

    def factory_check(self, identifier, *args, **kwargs):
        return self.context.checker_factory.make(identifier, args, kwargs)

    def factory_fix(self, identifier, *args, **kwargs):
        return self.context.fixer_factory.make(identifier, args, kwargs)

    # Make sure every plugin implements the run method
    def run(self):
        """
        Method that actually provides the custom runtime logic shipped
        with the plugin.

        Plugins are expected to override this methods to perform their
        actions.
        """

        raise NotImplementedError("The run method needs to be"
                                  "implemented by the plugin itself")


class Worker(Plugin):
    """
    A base class for Reporter, Checker and Fixer.
    """

    stateless = True
    side_effects = False

    def evaluate(self, *args, **kwargs):
        """
        Wraps the run method. Currently only adds the debug logging.
        """

        self.debug('Running with args={0}, kwargs={1}', args, kwargs)

        result = self.run(*args, **kwargs)
        self.debug('Result: {0}', result)

        return result


class Reporter(Worker):
    """
    Reports user activity to the AcTor.
    """

    __metaclass__ = PluginMount


class Checker(Worker):
    """
    Evaluates user activity depending on the input from the responders.
    """

    __metaclass__ = PluginMount

    def __bool__(self):
        return self.run()


class Fixer(Worker):
    """
    Performs a custom action on the machine.
    """

    __metaclass__ = PluginMount

    side_effects = True


class ContextProxyMixin(object):
    """
    Provides a simplified interface to the workers exposed by the context.
    """

    @property
    def identifier(self):
        return self.__class__.__name__

    @property
    def timetracking(self):
        return self.context.timetracking

    @property
    def backend(self):
        return self.context.backend

    def report(self, identifier, *args, **kwargs):
        return self.context.reporters.get(identifier, args, kwargs,
                                          rule_name=self.identifier)

    def check(self, identifier, *args, **kwargs):
        return self.context.checkers.get(identifier, args, kwargs,
                                         rule_name=self.identifier)

    def fix(self, identifier, *args, **kwargs):
        return self.context.fixers.get(identifier, args, kwargs,
                                       rule_name=self.identifier)


class Rule(ContextProxyMixin, Plugin):
    """
    Performs custom rule.
    """

    __metaclass__ = PluginMount


class DBusMixin(object):
    """
    Sets the interface of the specified DBus object as self.interface. In case
    DBusException occurs during setup, self.interface is set to None.
    """

    bus_name = None        # i.e. 'org.freedesktop.PowerManagement'
    object_path = None     # i.e.'/org/freedesktop/PowerManagement'
    interface_name = None  # can be omitted, and bus_name will be used instead

    # This is the maximum timeout possible, see
    # http://dbus.freedesktop.org/doc/api/html/group__DBusPendingCall.html
    INFINITE_TIMEOUT = 0x7FFFFFFF / 1000.0

    def __init__(self, *args, **kwargs):
        super(DBusMixin, self).__init__(*args, **kwargs)
        self.bus = dbus.SessionBus()
        self.initialize_interface()

    def initialize_interface(self):
        try:
            dbus_object = self.bus.get_object(self.bus_name, self.object_path)
            self._interface = dbus.Interface(
                dbus_object,
                self.interface_name or self.bus_name
            )
        except dbus.exceptions.DBusException:
            self._interface = None

    @property
    def interface(self):
        if self._interface is not None:
            return self._interface
        else:
            self.initialize_interface()
            return self._interface



class AsyncEvalMixinBase(object):

    """
    Base class for the asynchronous evaluation of the plugins. It makes
    sure that the plugin is evaluated in a separate thread, and hence
    it does not block the main execution loop of the program.

    This class is not to be used directly, instead one of the two child
    classes is supposed to be used:
        AsyncEvalNonBlockingMixin - does not block the thread, useful for
                                    plugins that leverage polling to obtain
                                    the data
        AsyncEvalBlockingMixin - blocks the thread, useful for the plugins
                                 that have data pushed using callbacks
    """

    stateless = False

    def __init__(self, *args, **kwargs):
        super(AsyncEvalMixinBase, self).__init__(*args, **kwargs)

        self.running = False
        self.completed = False
        self.result = None

    def thread_handler(self, *args, **kwargs):
        raise NotImplementedError("This class is not meant to be run directly")

    def evaluate(self, *args, **kwargs):
        if not self.running and not self.completed:
            thread = threading.Thread(
                target=self.thread_handler,
                args=args,
                kwargs=kwargs
            )
            thread.start()
        elif self.completed:
            return self.result

    def reset(self):
        """
        Resets the cached result and state of the plugin.

        This method should be explicitly called after the value
        from the plugin has been pulled and processed, to allow the
        further re-use of this plugin instance.
        """

        self.running = False
        self.completed = False
        self.result = None


class AsyncEvalNonBlockingMixin(AsyncEvalMixinBase):
    """
    Async mixin for polling-based plugins. Does not block the thread.
    """

    def thread_handler(self, *args, **kwargs):
        self.running = True

        # Here we intentionally call the evaluate on the grandparent to avoid
        # getting into a deadlock
        # pylint: disable=bad-super-call
        self.result = super(AsyncEvalMixinBase, self).evaluate(*args, **kwargs)
        self.completed = True
        self.running = False


class AsyncEvalBlockingMixin(AsyncEvalMixinBase):
    """
    Async mixin for pushing-based plugins. Does block the thread, waiting
    for the result to be updated.
    """

    def thread_handler(self, *args, **kwargs):
        self.running = True
        super(AsyncEvalBlockingMixin, self).evaluate(*args, **kwargs)

        # Block until result is available
        while getattr(self, 'result', None) is None:
            time.sleep(1)

        self.completed = True
        self.running = False


class AsyncDBusEvalMixin(AsyncEvalNonBlockingMixin, DBusMixin):
    """
    Async mixin for pushing-based plugins leveraging async dbus
    calls.
    """

    def reply_handler(self, reply):
        self.result = reply

    def error_handler(self, error):
        # Raise the returned DBusException
        raise error


class HashableDict(dict):
    """
    Enhanced dictionary that can be hashed (hence used as a key).
    """

    def __hash__(self):
        return hash(frozenset(self.items()))


class PluginFactory(object):
    """
    Simple factory class for a plugin mount. Provides creation capabilities
    for plugins of given type.
    """

    def __init__(self, mount, context):
        self.mount = mount
        self.context = context

    @property
    def plugins(self):
        """
        Returns a dictionary of plugins contained in the
        given PluginMount upon which the factory is built.
        """

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
        """
        Returns a plugin class corresponding to the given identifier. Raises
        NoSuchPlugin exception if none found.
        """

        try:
            return self.plugins[identifier]
        except KeyError:
            raise NoSuchPlugin("Plugin with identifier {0} is not available'"
                               .format(identifier))


class PluginCache(PluginFactory):
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
        super(PluginCache, self).__init__(mount, context)

        self.cache = {}
        self.instances = {}

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
            identifier = class_identifier or identifier
            self.instances[identifier] = instance = self.make(identifier)

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

    def run_plugin_instance(self, identifier, args,
                            kwargs, class_identifier=None):
        """
        Evaluates the plugin instance corresponding to the given identifier
        and returns the result.
        """

        instance = self.get_plugin_instance(identifier, class_identifier)
        return instance.evaluate(*args, **kwargs)

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
