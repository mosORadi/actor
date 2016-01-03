#!/usr/bin/python -B

import sys
import dbus
import dbus.service
import dbus.mainloop.qt

import PyQt4.Qt
import PyQt4.QtGui
import PyQt4.QtCore


class AsyncPromptThreadBase(PyQt4.QtCore.QThread):

    def __init__(self, desktop, reply_handler, message, identifier):
        super(AsyncPromptThreadBase, self).__init__(desktop)
        self.reply_handler = reply_handler
        self.message = message
        self.identifier = identifier

        self.communicator = self.Communicator()
        self.communicator.received.connect(self.return_result)

    def run(self):
        self.communicator.prompted.emit(self.message, self.identifier)


class AsyncPromptInputThread(AsyncPromptThreadBase):

    def __init__(self, desktop, *args, **kwargs):
        super(AsyncPromptInputThread, self).__init__(desktop, *args, **kwargs)
        self.communicator.prompted.connect(desktop.prompt_input)

    # pyqtSignals need to be class attributes of class inheriting from QObject
    class Communicator(PyQt4.QtCore.QObject):
        prompted = PyQt4.QtCore.pyqtSignal(str, str)
        received = PyQt4.QtCore.pyqtSignal(str)

    @PyQt4.QtCore.pyqtSlot(str)
    def return_result(self, value):
        self.reply_handler(str(value))


class ActorDesktopDBusProxy(dbus.service.Object):

    def __init__(self, desktop):
        self.desktop = desktop
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.freedesktop.ActorDesktop", bus=bus)

        super(ActorDesktopDBusProxy, self).__init__(bus_name, "/Desktop")

    @dbus.service.method("org.freedesktop.ActorDesktop", in_signature='ss', out_signature='s',
                         async_callbacks=('reply_handler', 'error_handler'))
    def Prompt(self, message, identifier, reply_handler, error_handler):
        thread = AsyncPromptInputThread(
            self.desktop,
            reply_handler,
            message,
            identifier
        )
        thread.start()


class ActorDesktop(PyQt4.QtGui.QWidget):

    @PyQt4.QtCore.pyqtSlot(str, str)
    def prompt(self, message, identifier):
        text, ok = PyQt4.QtGui.QInputDialog.getText(
            self,
            'Actor: %s' % identifier,
            message,
        )
        self.sender().received.emit(text)

def main():
    # Start dbus mainloop, must happen before definition of the main app
    dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)

    app = PyQt4.Qt.QApplication([])

    # Prevent input dialog from causing termination of the whole app
    app.setQuitOnLastWindowClosed(False)

    desktop = ActorDesktop()
    proxy = ActorDesktopDBusProxy(desktop)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
