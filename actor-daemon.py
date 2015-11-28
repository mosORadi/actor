#!/usr/bin/python

import os
import subprocess
import sys
sys.dont_write_bytecode = True

import config
from daemon import runner


class ActorDaemon(object):

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = os.path.join(config.CONFIG_DIR, 'actor.pid')
        self.pidfile_timeout = 5

    def set_environ(self):
        desktop_pid = subprocess.check_output('/usr/sbin/pidof %s' %
                                              config.DESKTOP_PROCESS,
                                              shell=True).strip()
        with open('/proc/%s/environ' % desktop_pid) as f:
            desktop_environ = dict(map(lambda x: x.split('=', 1),
                                   [var for var in f.read().split('\0')
                                    if '=' in var]))
            os.putenv('DBUS_SESSION_BUS_ADDRESS',
                       desktop_environ['DBUS_SESSION_BUS_ADDRESS'])

    def run(self):
        # Since Actor can connect from plugins to sockets,
        # we need to do the import inside the DaemonContext
        from actor import Actor, ActorDBusProxy

        # Forward all exceptions to the log
        sys.excepthook = Actor.log_exception
        Actor.setup_logging(level=config.LOGGING_LEVEL, daemon_mode=True)

        # Initialize an Actor instance and setup proxy for it
        actor = Actor()
        proxy = ActorDBusProxy(actor)

        # Run the AcTor!
        actor.main()


app = ActorDaemon()

# Use dummy files for daemons
if not sys.stdout.isatty():
    app.stdout_path = '/dev/null'
    app.stderr_path = '/dev/null'

if os.environ.get('DBUS_SESSION_BUS_ADDRESS', None):
    app.set_environ()

daemon_runner = runner.DaemonRunner(app)

if config.LOGGING_TARGET == 'stdout':
    daemon_runner.daemon_context.stdout = sys.stdout
    daemon_runner.daemon_context.stderr = sys.stderr

daemon_runner.do_action()
