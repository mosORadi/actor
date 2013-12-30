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

class CountdownTriggerFixer(IFixer):
    export_as = 'countdown'

    def __init__(self):
        super(CountdownTriggerFixer, self).__init__()
        self.signal = CountdownTriggerSignal()

    def fix(self):
        self.signal.CountdownStartSignal(self.options.get('id', ''))