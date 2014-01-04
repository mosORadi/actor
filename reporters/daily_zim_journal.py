import datetime

from file_content import FileContentReporter

class DailyZimJournalReporter(FileContentReporter):

    export_as = "daily_zim_journal"

    required_plugin_options = ["journal_root_path", "path"]
    optional_plugin_options = []

    def __init__(self, **options):
        super(DailyZimJournalReporter, self).__init__(path=self.get_path(options['journal_root_path']), **options)

    def get_path(self, journal_root_path):
        today = datetime.date.today()
        path = "%s/%s/%s/%s.txt" % (
                   journal_root_path,
                   today.year,
                   today.strftime('%m'),
                   today.strftime('%d')
               )
        return path

    def report(self):
        self.options['path'] = self.get_path(self.options['journal_root_path'])
        return super(DailyZimJournalReporter, self).report()
