#import os
#import grp
#import signal
import daemon
import lockfile

from actor import Actor

daemon_context = daemon.DaemonContext(
    working_directory='/var/lib/actor',
    pidfile=lockfile.FileLock('/var/run/actor.pid'),
    )

actor = Actor()

with daemon_context:
    actor.main()
