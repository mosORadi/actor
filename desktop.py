#!/usr/bin/python -B

import sys
import dbus
import dbus.service
import dbus.mainloop.pyqt5

import PyQt5.QtWidgets
import PyQt5.QtGui
import PyQt5.QtCore


class OverlayWindow(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, app, *args, **kwargs):

        super(OverlayWindow, self).__init__(*args, **kwargs)

        self.app = app

        self.setObjectName("OverlayWindow")
        self.resize(1920, 1080)

        self.create_central_widget()
        self.create_central_frame()
        self.create_main_label()
        self.create_input()
        self.create_button()

        self.set_window_flags()

    def create_central_widget(self):
        self.centralwidget = PyQt5.QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

    def create_central_frame(self):
        self.frame = PyQt5.QtWidgets.QFrame(self.centralwidget)
        self.frame.setObjectName("frame")
        self.frame.setGeometry(PyQt5.QtCore.QRect(0, 0, 400, 400))
        self.frame.setFrameShape(PyQt5.QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(PyQt5.QtWidgets.QFrame.Raised)
        self.frame.setStyleSheet("QFrame {"
            "background-color: rgba(255, 255, 255, 15); "
            "}"
        )

        # Center the frame
        qr = self.frame.frameGeometry()
        cp = PyQt5.QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.frame.move(qr.topLeft())

        self.layout().addWidget(self.frame)

    def create_input(self):
        self.lineEdit = PyQt5.QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(PyQt5.QtCore.QRect(150, 150, 100, 30))

    def create_button(self):
        self.pushButton = PyQt5.QtWidgets.QPushButton(self.frame)
        self.pushButton.setText("Finished")
        self.pushButton.setShortcut("Q")
        self.pushButton.setGeometry(PyQt5.QtCore.QRect(150, 200, 100, 30))
        self.pushButton.clicked.connect(self.handle_clicked)

    def handle_clicked(self):
        self.reply_signal.emit(self.lineEdit.text())
        self.close()

    def set_reply_signal(self, signal):
        self.reply_signal = signal

    def create_main_label(self):
        # Create the button
        self.title = PyQt5.QtWidgets.QLabel("", self.frame)
        self.title.setGeometry(PyQt5.QtCore.QRect(0, 0, 400, 70))
        self.title.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        # This is a necessary override, since otherwise it seems
        # the background color opaqueness coefficient is summed up
        # with the underlying QFrame
        self.title.setStyleSheet("QLabel {"
            "background-color: rgba(255, 255, 255, 0); "
            "color: gray; "
            "font-size: 20pt; "
            "font-weight: bold; "
            "}"
        )

        self.description = PyQt5.QtWidgets.QLabel("", self.frame)
        self.description.setGeometry(PyQt5.QtCore.QRect(0, 70, 400, 70))
        self.description.setAlignment(PyQt5.QtCore.Qt.AlignHCenter | PyQt5.QtCore.Qt.AlignTop)

        self.description.setStyleSheet("QLabel {"
            "background-color: rgba(255, 255, 255, 0); "
            "color: gray; "
            "font-size: 12pt; "
            "font-weight: bold; "
            "}"
        )

    def paintEvent(self, event=None):
        painter = PyQt5.QtGui.QPainter(self)

        painter.setOpacity(0.85)
        painter.setBrush(PyQt5.QtCore.Qt.black)
        painter.setPen(PyQt5.QtGui.QPen(PyQt5.QtCore.Qt.black))
        painter.drawRect(self.rect())

    def set_window_flags(self):
        self.setWindowFlags(PyQt5.QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(PyQt5.QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(PyQt5.QtCore.Qt.WA_TranslucentBackground, True)

    def event(self, event):
        """
        Incoming event processor: catches and ignores attempted close events,
        otherwise passes everything on.
        """

        if event.type() == PyQt5.QtCore.QEvent.Close and event.spontaneous():
            event.ignore()
            return True  # Signalize that event was processed
        else:
            return super(OverlayWindow, self).event(event)


class AsyncPromptThreadBase(PyQt5.QtCore.QThread):

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
    class Communicator(PyQt5.QtCore.QObject):
        prompted = PyQt5.QtCore.pyqtSignal(str, str)
        received = PyQt5.QtCore.pyqtSignal(str)

    @PyQt5.QtCore.pyqtSlot(str)
    def return_result(self, value):
        self.reply_handler(str(value))


class AsyncPromptYesNoThread(AsyncPromptThreadBase):

    def __init__(self, desktop, *args, **kwargs):
        super(AsyncPromptYesNoThread, self).__init__(desktop, *args, **kwargs)
        self.communicator.prompted.connect(desktop.prompt_yesno)

    # pyqtSignals need to be class attributes of class inheriting from QObject
    class Communicator(PyQt5.QtCore.QObject):
        prompted = PyQt5.QtCore.pyqtSignal(str, str)
        received = PyQt5.QtCore.pyqtSignal(bool)

    @PyQt5.QtCore.pyqtSlot(bool)
    def return_result(self, value):
        self.reply_handler(bool(value))


class AsyncOverlayThread(AsyncPromptThreadBase):

    def __init__(self, desktop, *args, **kwargs):
        super(AsyncOverlayThread, self).__init__(desktop, *args, **kwargs)
        self.communicator.prompted.connect(desktop.overlay)

    # pyqtSignals need to be class attributes of class inheriting from QObject
    class Communicator(PyQt5.QtCore.QObject):
        prompted = PyQt5.QtCore.pyqtSignal(str, str)
        received = PyQt5.QtCore.pyqtSignal(str)

    @PyQt5.QtCore.pyqtSlot(str)
    def return_result(self, value):
        self.reply_handler(str(value))


class ActorDesktopDBusProxy(dbus.service.Object):

    def __init__(self, desktop):
        self.desktop = desktop
        bus = dbus.SessionBus()

        # Prevent duplicate Actor instances
        if 'org.freedesktop.ActorDesktop' in bus.list_names():
            print("Actor-desktop already running, exiting.")
            sys.exit(0)

        bus_name = dbus.service.BusName("org.freedesktop.ActorDesktop", bus=bus)

        super(ActorDesktopDBusProxy, self).__init__(bus_name, "/Desktop")

    def prompt_generic(self, cls, message, identifier, reply_handler):
        thread = cls(
            self.desktop,
            reply_handler,
            message,
            identifier
        )
        thread.start()

    @dbus.service.method("org.freedesktop.ActorDesktop", in_signature='ss', out_signature='s',
                         async_callbacks=('reply_handler', 'error_handler'))
    def Prompt(self, message, identifier, reply_handler, error_handler):
        self.prompt_generic(AsyncPromptInputThread, message, identifier, reply_handler)

    @dbus.service.method("org.freedesktop.ActorDesktop", in_signature='ss', out_signature='b',
                         async_callbacks=('reply_handler', 'error_handler'))
    def PromptYesNo(self, message, identifier, reply_handler, error_handler):
        self.prompt_generic(AsyncPromptYesNoThread, message, identifier, reply_handler)

    @dbus.service.method("org.freedesktop.ActorDesktop", in_signature='ss', out_signature='s',
                         async_callbacks=('reply_handler', 'error_handler'))
    def Overlay(self, title, description, reply_handler, error_handler):
        self.prompt_generic(AsyncOverlayThread, title, description, reply_handler)


class ActorDesktop(PyQt5.QtWidgets.QWidget):

    def __init__(self, app):
        super(ActorDesktop, self).__init__()

        self.app = app

    @PyQt5.QtCore.pyqtSlot(str, str)
    def prompt_input(self, message, identifier):
        text, ok = PyQt5.QtWidgets.QInputDialog.getText(
            self,
            'Actor: %s' % identifier,
            message,
        )
        self.sender().received.emit(text)

    @PyQt5.QtCore.pyqtSlot(str, str)
    def prompt_yesno(self, message, identifier):
        reply = PyQt5.QtWidgets.QMessageBox.question(
            self,
            'Actor: %s' % identifier,
            message,
            PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No
        )

        if reply == PyQt5.QtWidgets.QMessageBox.Yes:
            self.sender().received.emit(True)
        else:
            self.sender().received.emit(False)

    @PyQt5.QtCore.pyqtSlot(str, str)
    def overlay(self, title, description):
        self.window = OverlayWindow(self.app)
        self.window.showFullScreen()
        self.window.set_reply_signal(self.sender().received)
        self.window.title.setText(title)
        self.window.description.setText(description)


def main():
    # Start dbus mainloop, must happen before definition of the main app
    dbus.mainloop.pyqt5.DBusQtMainLoop(set_as_default=True)

    app = PyQt5.QtWidgets.QApplication([])

    # Prevent input dialog from causing termination of the whole app
    app.setQuitOnLastWindowClosed(False)

    desktop = ActorDesktop(app)
    proxy = ActorDesktopDBusProxy(desktop)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
