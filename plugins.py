import dbus
import time
import threading

import logger


class NoSuchPlugin(Exception):
    """
    Raised when a plugin could not be found.
    """
    pass


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            # System generic plugin classes are marked with 'noplugin'
            # attribute. We do not want to mix those with user plugin
            # instances, so let's skip them
            if not 'noplugin' in cls.__dict__:
                cls.plugins.append(cls)


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
        raise NotImplementedError("The run method needs to be"
            "implemented by the plugin itself")


class Worker(Plugin):
    """
    A base class for Reporter, Checker and Fixer.
    """

    stateless = True
    side_effects = False

    def evaluate(self, *args, **kwargs):
        self.debug('Running with args={0}, kwargs={1}'.format(args, kwargs))

        result = self.run(*args, **kwargs)
        self.debug('Result: {0}'.format(result))

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

    side_effects = True

    __metaclass__ = PluginMount


class ContextProxyMixin(object):
    """
    Provides a simplified interface to the workers exposed by the context.
    """

    @property
    def identifier(self):
        return self.__class__.__name__

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

        try:
            self.bus = dbus.SessionBus()
            dbus_object = self.bus.get_object(self.bus_name, self.object_path)
            self.interface = dbus.Interface(dbus_object,
                                            self.interface_name or self.bus_name)
        except dbus.exceptions.DBusException:
            self.interface = None


class AsyncEvalMixin(object):

    stateless = False

    def __init__(self, *args, **kwargs):
        super(AsyncEvalMixin, self).__init__(*args, **kwargs)
        self.reset()

    def thread_handler(self, *args, **kwargs):
        self.running = True
        self.result = super(AsyncEvalMixin, self).evaluate(*args, **kwargs)
        self.completed = True
        self.running = False

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


class AsyncDBusEvalMixin(AsyncEvalMixin, DBusMixin):

    def reply_handler(self, reply):
        self.result = reply

    def error_handler(self, error):
        # Raise the returned DBusException
        raise error

    def thread_handler(self, *args, **kwargs):
        self.running = True
        super(AsyncEvalMixin, self).evaluate(*args, **kwargs)

        # Block until result is available
        while getattr(self, 'result', None) is None:
            time.sleep(1)

        self.completed = True
        self.running = False
