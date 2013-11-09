#import os
#import grp
#import signal
import daemon
import lockfile

from actor import Actor

daemon_context = daemon.DaemonContext(
    working_directory='/var/lib/actor',
    pidfile=lockfile.FileLock('/var/run/spam.pid'),
    )

actor = Actor()

with daemon_context:
    actor.do_main_program()
