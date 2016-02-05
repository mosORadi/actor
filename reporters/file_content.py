import os

from plugins import Reporter


class FileContentReporter(Reporter):
    """
    Returns the content of a given file.

    Returns None if the file does not exist.
    """

    identifier = 'file_content'

    def run(self, path):
        if os.path.isfile(path):
            with open(path, 'r') as fil:
                return fil.read()
