"""
Provides long term storage backend implementations.
"""

import datetime
from pony import orm

from config import config

db = orm.Database('sqlite', config.DB_FILE, create_db=True)

class Record(db.Entity):
    name = orm.Required(str)
    key = orm.Required(str)
    value = orm.Required(orm.Json)
    orm.composite_key(name, key)

db.generate_mapping(create_tables=True)


class Backend(object):
    """
    Backend implementation using local sqlite database.
    """

    @staticmethod
    def convert_key(key):
        """
        Generates key out of given object.
        """

        if isinstance(key, datetime.datetime):
            return key.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(key, datetime.date):
            return key.strftime("%Y-%m-%d")

        return key

    @orm.db_session
    def put(self, name, key, value, meta=False):
        key = self.convert_key(key)
        record = self.get(name, key, value_only=False)

        if not record:
            record = Record(name=name, key=key, value=value)
        else:
            record.value = value

    @orm.db_session
    def get(self, name, key, value_only=True):
        key = self.convert_key(key)
        matching = Record.select(lambda r: r.name == name and r.key == key)

        if value_only:
            # Return only value
            return list(matching)[0].value if matching else None
        else:
            # Return the whole record object
            return list(matching)[0] if matching else None
