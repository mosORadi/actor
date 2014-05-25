#!/usr/bin/python

import config
import os
import sys

from daemon import runner

class ActorDaemon(object):

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = os.path.join(config.HOME_DIR, 'actor.pid')
        self.pidfile_timeout = 5

    def run(self):
        # Since Actor can connect from plugins to sockets,
        # we need to do the import inside the DaemonContext
        from actor import Actor
        actor = Actor()
        actor.main()


app = ActorDaemon()

if not sys.stdout.isatty():
    app.stdout_path = '/dev/null'
    app.stderr_path = '/dev/null'

daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
