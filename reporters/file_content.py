import os

from plugins import Reporter


class FileContentReporter(Reporter):

    identifier = 'file_content'
    required_plugin_options = ['path']

    def __init__(self, **options):
        super(FileContentReporter, self).__init__(**options)
        self.path = self.options.get('path', '')

    def report(self):
        if os.path.isfile(self.path):
            with open(self.path, 'r') as f:
                return f.read()
        else:
            return ''
