import datetime
import dbus
import json
import pickle
import subprocess
import sys


def json_encode(data):
    """
    A simple wrapper around json.dumps that uses JsonPicklerEncoder.
    """
    return json.dumps(data, cls=JsonPicklerEncoder)


def json_decode(data):
    """
    A simple wrapper around json.loads that uses JsonPicklerDecoder.
    """
    return json.loads(data, object_hook=JsonPicklerDecoder.unpickle)


class JsonPicklerEncoder(json.JSONEncoder):
    """
    Extends regular JSONEncoder with ability to serialize arbitrary objects
    using pickle.dumps.
    """

    def default(self, obj):
        """
        Keep a mark before the pickled object so we can tell it's been
        pickled.
        """
        data = "pickled|" + pickle.dumps(obj)
        return data


class JsonPicklerDecoder(json.JSONDecoder):
    """
    Provides a unpickle method that deserializes JSON strings that might
    contain some attributes marked as pickled objects.
    """

    @classmethod
    def unpickle(cls, obj):
        """
        Recursively unpickle already deserialized JSON structure.
        """

        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = cls.unpickle(value)
            return obj

        elif isinstance(obj, list):
            obj = list([cls.unpickle(v) for v in obj])
            return obj

        elif isinstance(obj, str) or isinstance(obj, unicode):
            if obj.startswith('pickled|'):
                return pickle.loads(obj[8:])

        return obj


class Periodic(object):
    """
    A helper class to abstract away handling of periodic time intervals.

    Returns True once after every 'minutes' minutes.

    If automatic_intervals is set to True, new interval starts immediately
    after the object has been evaluated to True. Otherwise the new interval
    starts manually by calling start_new_interval() method.
    """

    def __init__(self, minutes, automatic_intervals=True):
        self.period = datetime.timedelta(minutes=minutes)
        self.last_execution = datetime.datetime.fromtimestamp(0)
        self.automatic = automatic_intervals

    def __nonzero__(self):
        now = datetime.datetime.now()
        if now - self.period >= self.last_execution:
            # Mark the start of a new interval if automatic intervals are
            # desired
            if self.automatic:
                self.last_execution = now
            return True
        else:
            return False

    def start_new_interval(self):
        self.last_execution = datetime.datetime.now()


class Expiration(object):
    """
    A helper class to abstract away handling of expiring time intervals.

    Returns False until 'minutes' have passed since its initialization.
    """

    def __init__(self, minutes=0):
        self.interval = datetime.timedelta(minutes=minutes)
        self.expiration_point = datetime.datetime.now() + self.interval
        self.expiration_notified = False

    def __nonzero__(self):
        now = datetime.datetime.now()
        return now >= self.expiration_point

    def just_expired(self):
        """
        Returns True if called the first time after the object has expired.
        """

        # Do not consider empty intervals as worthy of expiration notification
        if not self.interval:
            return False

        if self and not self.expiration_notified:
            self.expiration_notified = True
            return True
        else:
            return False

    @property
    def passed(self):
        delta = datetime.datetime.now() + self.interval - self.expiration_point
        return delta.total_seconds()

    @property
    def remaining(self):
        delta =  self.expiration_point - datetime.datetime.now()
        return delta.total_seconds()

    @property
    def duration(self):
        return self.interval.total_seconds()


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
