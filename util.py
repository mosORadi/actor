import subprocess

def run(args):
    child = subprocess.Popen(map(str, args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    rc = child.returncode

    return stdout, stderr, rc
