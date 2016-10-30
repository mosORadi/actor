#!/usr/bin/python

import multiprocessing
import sys
sys.dont_write_bytecode = True

from main import Actor, ActorDBusProxy
from config import config


# Start the desktop service in a separate process
def start_desktop():
    import desktop
    desktop.main()


def main(logging_level=config.LOGGING_LEVEL):
    desktop = multiprocessing.Process(target=start_desktop)
    desktop.start()

    # Forward all exceptions to the log
    sys.excepthook = Actor.log_exception
    Actor.setup_logging(level=logging_level)

    # Initialize an Actor instance and setup proxy for it
    actor = Actor()
    ActorDBusProxy(actor)

    # Run the AcTor!
    actor.main()


def main_debug():
    main(logging_level=logging.DEBUG)

if __name__ == '__main__':
    main_debug()
