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


def main():
    desktop = multiprocessing.Process(target=start_desktop)
    desktop.start()

    # Forward all exceptions to the log
    sys.excepthook = Actor.log_exception
    Actor.setup_logging(level=config.LOGGING_LEVEL)

    # Initialize an Actor instance and setup proxy for it
    actor = Actor()
    ActorDBusProxy(actor)

    # Run the AcTor!
    actor.main()


if __name__ == '__main__':
    main()
