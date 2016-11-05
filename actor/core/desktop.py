#!/usr/bin/python -B
from __future__ import print_function

import os
import sys
import time
import dbus
import dbus.service
import dbus.mainloop.pyqt5

import PyQt5.QtWidgets
import PyQt5.QtGui
import PyQt5.QtCore

from config import config

# This file uses PyQt5, which brings over some pep8
# incompliant method names
# pylint: disable=invalid-name


class OverlayWindow(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, app, *args, **kwargs):

        super(OverlayWindow, self).__init__(*args, **kwargs)

        self.app = app

        # Used to emit the reply from the input from the correct signal
        self.reply_signal = None

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
        self.frame.setStyleSheet(
            "QFrame {"
            "background-color: rgba(255, 255, 255, 15); "
            "}"
        )

        # Center the frame
        coordinates = self.frame.frameGeometry()

        desktop = PyQt5.QtWidgets.QDesktopWidget()
        desktop_center = desktop.availableGeometry().center()

        coordinates.moveCenter(desktop_center)
        self.frame.move(coordinates.topLeft())

        self.layout().addWidget(self.frame)

    def create_input(self):
        self.line_edit = PyQt5.QtWidgets.QLineEdit(self.frame)
        self.line_edit.setObjectName("line_edit")
        self.line_edit.setGeometry(PyQt5.QtCore.QRect(150, 150, 100, 30))

    def create_button(self):
        self.push_button = PyQt5.QtWidgets.QPushButton(self.frame)
        self.push_button.setText("Finished")
        self.push_button.setShortcut("Q")
        self.push_button.setGeometry(PyQt5.QtCore.QRect(150, 200, 100, 30))
        self.push_button.clicked.connect(self.handle_clicked)

    def handle_clicked(self):
        self.reply_signal.emit(self.line_edit.text())
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
        self.title.setStyleSheet(
            "QLabel {"
            "background-color: rgba(255, 255, 255, 0); "
            "color: gray; "
            "font-size: 20pt; "
            "font-weight: bold; "
            "}"
        )

        self.description = PyQt5.QtWidgets.QLabel("", self.frame)
        self.description.setGeometry(PyQt5.QtCore.QRect(0, 70, 400, 70))
        self.description.setAlignment(
            PyQt5.QtCore.Qt.AlignHCenter | PyQt5.QtCore.Qt.AlignTop)

        self.description.setStyleSheet(
            "QLabel {"
            "background-color: rgba(255, 255, 255, 0); "
            "color: gray; "
            "font-size: 12pt; "
            "font-weight: bold; "
            "}"
        )

    def paintEvent(self, event=None):
        # pylint: disable=unused-argument

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
        elif event.type() == PyQt5.QtCore.QEvent.Leave:
            # If despite our best efforts with flags the window has been
            # deactivated, raise on the top again
            time.sleep(0.05)
            self.raise_()
            event.ignore()
            return True
        return super(OverlayWindow, self).event(event)


class AsyncPromptThreadBase(PyQt5.QtCore.QThread):

    def __init__(self, desktop, reply_handler, title, message):
        super(AsyncPromptThreadBase, self).__init__(desktop)
        self.reply_handler = reply_handler
        self.title = title
        self.message = message

        self.communicator = self.Communicator()
        self.communicator.received.connect(self.return_result)

    def run(self):
        self.communicator.prompted.emit(self.title, self.message)


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
    # pylint: disable=interface-not-implemented

    def __init__(self, desktop):
        self.desktop = desktop
        bus = dbus.SessionBus()

        # Prevent duplicate Actor instances
        if 'org.freedesktop.ActorDesktop' in bus.list_names():
            print("Actor-desktop already running, exiting.")
            sys.exit(0)

        bus_name = dbus.service.BusName(
            "org.freedesktop.ActorDesktop", bus=bus)

        super(ActorDesktopDBusProxy, self).__init__(bus_name, "/Desktop")

    def prompt_generic(self, cls, title, message, reply_handler):
        thread = cls(
            self.desktop,
            reply_handler,
            title,
            message
        )
        thread.start()

    @dbus.service.method("org.freedesktop.ActorDesktop",
                         in_signature='ss', out_signature='s',
                         async_callbacks=('reply_handler', 'error_handler'))
    def Prompt(self, title, message, reply_handler, error_handler):
        self.prompt_generic(
            AsyncPromptInputThread,
            title,
            message,
            reply_handler)

    @dbus.service.method("org.freedesktop.ActorDesktop",
                         in_signature='ss', out_signature='b',
                         async_callbacks=('reply_handler', 'error_handler'))
    def PromptYesNo(self, title, message, reply_handler, error_handler):
        self.prompt_generic(
            AsyncPromptYesNoThread,
            title,
            message,
            reply_handler)

    @dbus.service.method("org.freedesktop.ActorDesktop",
                         in_signature='ss', out_signature='s',
                         async_callbacks=('reply_handler', 'error_handler'))
    def Overlay(self, title, description, reply_handler, error_handler):
        self.prompt_generic(
            AsyncOverlayThread,
            title,
            description,
            reply_handler)

    @dbus.service.method("org.freedesktop.ActorDesktop",
                         in_signature='ssi', out_signature='')
    def ShowMessage(self, title, message, duration):
        self.desktop.show_message(title, message, duration)


    @dbus.service.method("org.freedesktop.ActorDesktop", out_signature='b')
    def SetupFinished(self):
        return self.desktop.setup_finished


class ActorDesktop(PyQt5.QtWidgets.QWidget):

    def __init__(self, app):
        super(ActorDesktop, self).__init__()

        self.setup_finished = False
        self.app = app
        self.startup_wait()
        self.setup_tray()

    def startup_wait(self):
        """
        Prolongs the startup sequence until we're sure all system components
        (such as systray) are ready.
        """

        timeout = 60

        while timeout > 0:
            if PyQt5.QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
                break

            time.sleep(1)
            timeout = timeout - 1

    def setup_tray(self):
        icon_path = os.path.join(config.STATIC_DIR, 'actor-logo.png')
        icon = PyQt5.QtGui.QIcon(icon_path)

        self.tray_icon = PyQt5.QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.show()

        self.setWindowIcon(icon)

        actions = [
            PyQt5.QtWidgets.QAction("Mi&nimize", self, triggered=self.hide),
            PyQt5.QtWidgets.QAction("Ma&ximize", self, triggered=self.showMaximized),
            PyQt5.QtWidgets.QAction("&Restore", self, triggered=self.showNormal)
        ]

        icon_menu = PyQt5.QtWidgets.QMenu(self)
        for action in actions:
            icon_menu.addAction(action)

        self.tray_icon.setContextMenu(icon_menu)

    def show_message(self, title, message, duration):
        icon = PyQt5.QtWidgets.QSystemTrayIcon.Information
        self.tray_icon.showMessage(title, message, icon, duration * 1000)

    @PyQt5.QtCore.pyqtSlot(str, str)
    def prompt_input(self, title, message):
        text = PyQt5.QtWidgets.QInputDialog.getText(
            self,
            title,
            message,
        )[0]

        self.sender().received.emit(text)

    @PyQt5.QtCore.pyqtSlot(str, str)
    def prompt_yesno(self, title, message):
        reply = PyQt5.QtWidgets.QMessageBox.question(
            self,
            title,
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
    ActorDesktopDBusProxy(desktop)
    desktop.setup_finished = True

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
