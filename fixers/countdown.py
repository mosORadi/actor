from plugins import IFixer
import dbus
import dbus.service

import random

class CountdownTriggerFixer(IFixer, dbus.service.Object):
    export_as = 'countdown'

    def __init__(self):
        super(CountdownTriggerFixer, self).__init__()
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/org/freedesktop/Actor/%s' % random.randint(1,100000))
    
    @dbus.service.signal(dbus_interface='org.freedesktop.AcTor', signature='s')
    def CountdownStartSignal(self, countdown_id):
        return countdown_id

    def fix(self):
        self.CountdownStartSignal(self.options.get('id', ''))
