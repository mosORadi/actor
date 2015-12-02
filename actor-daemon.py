#!/usr/bin/python

import os
import subprocess
import sys
sys.dont_write_bytecode = True

from actor import Actor, ActorDBusProxy
import config

# Forward all exceptions to the log
sys.excepthook = Actor.log_exception
Actor.setup_logging(level=config.LOGGING_LEVEL, daemon_mode=True)

# Initialize an Actor instance and setup proxy for it
actor = Actor()
proxy = ActorDBusProxy(actor)

# Run the AcTor!
actor.main()
