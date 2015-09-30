import datetime

from file_content import FileContentReporter

class DailyZimJournalReporter(FileContentReporter):

    identifier = "daily_zim_journal"

    required_plugin_options = ["journal_root_path", "path"]
    optional_plugin_options = ["day_shift"]

    def __init__(self, **options):
        self.options = options
        super(DailyZimJournalReporter, self).__init__(path=self.get_path(options['journal_root_path']), **options)

    def get_path(self, journal_root_path):

        day_shift = self.options.get("day_shift", "0")
        delta = datetime.timedelta(days=int(day_shift))

        day = datetime.date.today() + delta
        path = "%s/%s/%s/%s.txt" % (
                   journal_root_path,
                   day.year,
                   day.strftime('%m'),
                   day.strftime('%d')
               )
        return path

    def report(self):
        self.options['path'] = self.get_path(self.options['journal_root_path'])
        return super(DailyZimJournalReporter, self).report()
