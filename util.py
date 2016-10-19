import datetime
import dbus
import subprocess
import sys


class Periodic(object):
    """
    A helper class to abstract away handling of periodic time intervals.

    Returns True once after every 'seconds' seconds.
    """

    def __init__(self, seconds):
        self.period = datetime.timedelta(seconds=seconds)
        self.last_execution = datetime.datetime.fromtimestamp(0)

    def __nonzero__(self):
        now = datetime.datetime.now()
        if now - self.period >= self.last_execution:
            self.last_execution = now
            return True
        else:
            return False


def run(args):
    child = subprocess.Popen(
        [str(arg) for arg in args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = child.communicate()
    code = child.returncode

    return stdout, stderr, code


def run_async(args):
    child = subprocess.Popen([str(arg) for arg in args])
    return child


def convert_timestamp(timestamp):
    """
    Takes timestamp (either "%H.%M" string or datetime.time object)
    and converts it to datetime.datetime object valid for today.
    """

    if isinstance(timestamp, str):
        # If the date is not specified, beginning of epoch will be used
        parsed = datetime.datetime.strptime(timestamp, "%H.%M")

        # Hence we need to combine the time with today's date
        return datetime.datetime.combine(datetime.date.today(), parsed.time())
    else:
        return datetime.datetime.combine(datetime.date.today(), timestamp)


def extract_dbus_exception_error(exception):
    exception_type = exception.get_dbus_name().split('.')[-1]
    error_lines = [l for l in exception.message.splitlines()
                   if l.startswith(exception_type)]

    if error_lines:
        return error_lines[0][:-1]


def dbus_error_handler(function):
    """
    Makes sure that DBus errors are properly parsed out and handled.

    Also caches the argcount of the original (un-wrapped) function in the
    _co_argcount attribute.
    """
    def wrapped(*args):
        try:
            function(*args)
        except dbus.DBusException as exc:
            error = extract_dbus_exception_error(exc)
            error = error or "DBus exception occured."
            sys.exit(error)

    # pylint: disable=protected-access
    wrapped._co_argcount = function.func_code.co_argcount

    return wrapped
