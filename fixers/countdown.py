from plugins import IFixer
import dbus
import dbus.service

import random

class CountdownTriggerSignal(dbus.service.Object):

    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/org/freedesktop/Actor/%s' % random.randint(1,100000))

    @dbus.service.signal(dbus_interface='org.freedesktop.AcTor', signature='s')
    def CountdownStartSignal(self, countdown_id):
        return countdown_id

    @dbus.service.signal(dbus_interface='org.freedesktop.AcTor', signature='s')
    def CountdownResetSignal(self, countdown_id):
        return countdown_id

class CountdownTriggerFixer(IFixer):
    """
    Emits a D-Bus signal to start countdown on CountdownChecker with
    the specified identifier.

    Required options:
        id - CountdownChecker identifier (as defined by export_as option 
                                          or the plugin default value)
    """

    export_as = 'countdown'
    required_plugin_options = ['id']
    optional_plugin_options = ['action']

    def __init__(self, **options):
        super(CountdownTriggerFixer, self).__init__(**options)
        self.signal = CountdownTriggerSignal()

    def fix(self, **reports):
        action = self.options.get('action', 'start')

        if action == 'start':
            self.signal.CountdownStartSignal(self.options.get('id', ''))
        elif action == 'reset':
            self.signal.CountdownResetSignal(self.options.get('id', ''))
