from plugins import Fixer
import dbus
import dbus.service

import random

class HealthDecreaseSignal(dbus.service.Object):

    def __init__(self):
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/org/freedesktop/Actor/%s' % random.randint(1,100000))

    @dbus.service.signal(dbus_interface='org.freedesktop.AcTor', signature='s')
    def HealthDecreaseSignal(self, countdown_id):
        return countdown_id

class HealthDecreaseFixer(Fixer):
    """
    Emits a D-Bus signal to decrease health on HealthChecker with
    the specified identifier.

    Required options:
        id - HealthChecker identifier
    """

    identifier = 'health_decrease'
    required_plugin_options = ['id']

    def __init__(self, **options):
        super(HealthDecreaseFixer, self).__init__(**options)
        self.signal = HealthDecreaseSignal()

    def fix(self, **reports):
        self.signal.HealthDecreaseSignal(self.options.get('id', ''))
