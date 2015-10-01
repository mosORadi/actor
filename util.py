import datetime
import subprocess

def run(args):
    child = subprocess.Popen(
            map(str, args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
    )
    stdout, stderr = child.communicate()
    rc = child.returncode

    return stdout, stderr, rc

def convert_timestamp(timestamp):
    """
    Takes timestamp (either "%H.%M" string or datetime.time object)
    and converts it to datetime.datetime object valid for today.
    """

    if type(timestamp) is str:
        # If the date is not specified, beginning of epoch will be used
        parsed = datetime.datetime.strptime(timestamp, "%H.%M")

        # Hence we need to combine the time with today's date
        return datetime.datetime.combine(datetime.date.today(), parsed.time())
    else:
        return datetime.datetime.combine(datetime.date.today(), timestamp)
