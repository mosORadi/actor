import os

from plugins import IReporter


class FileContentReporter(IReporter):

    export_as = 'file_content'

    def setup(self, **options):
        super(FileContentReporter, self).setup(**options)
        self.path = self.options.get('path', '')

    def report(self):
        if os.path.isfile(self.path):
            with open(self.path, 'r') as f:
                return f.read()
        else:
            return ''
