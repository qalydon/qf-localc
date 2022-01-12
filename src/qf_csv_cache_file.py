# coding: utf-8
#
# csv_cache_file - Implements use of CSV file for history data caching
# Copyright © 2022  Dave Hocker (email: Qalydon17@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE.md file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE.md file).  If not, see <http://www.gnu.org/licenses/>.
#

import csv


class QFCSVCacheFile():
    """
    Implements a cache file (in CSV format) with a compound key and multiple values.
    The compound key is usually a ticker symbol and ISO format date (yyyy-mm-dd)
    in the following format: symbol:date.


    Each record in the CSV file has the following columns: ticker symbol, date, value-1,...,value-n.
    """
    def __init__(self, csv_file_path, symbol="", value_date="", value_keys=None):
        """
        Initialize a cache file instance
        :param csv_file_path:
        :param symbol: The key that contains the ticker symbol.
        :param value_date: The key that contains the CSV record date.
        :param value_keys: A list of keys for the values in a CSV record.
        """
        if value_keys is None:
            value_keys = []
        self._csv_file_path = csv_file_path

        self._symbol = symbol
        self._value_date = value_date
        self._value_keys = value_keys

        # This is the complete set of columns in a single CSV record.
        # The first two columns are always the ticker symbol and the date.
        self._csv_field_names = [self._symbol, self._value_date]
        self._csv_field_names.extend(self._value_keys)

        self._cache = None

    def get_cache_record(self, symbol, value_date):
        """
        Return the cache record for a given date
        :param symbol: Ticker symbol
        :param value_date: ISO format date yyyy-mm-dd
        :return: If there is no cache record for the symbol:value_date, returns None.
        Else, returns the cached record.
        """
        key = QFCSVCacheFile._make_key(symbol, value_date)
        if key not in self._cache.keys():
            return None
        return self._cache[key]

    def get_cache_value(self, symbol, value_date, value_key):
        """
        Return the value for a given cache record
        :param symbol: Ticker symbol
        :param value_date: ISO format date yyyy-mm-dd
        :param value_key: Column name
        :return: If there is no cache record for the symbol:value_date, returns None.
        Else, returns the cached value.
        """
        key = QFCSVCacheFile._make_key(symbol, value_date)
        cr = self.get_cache_record(symbol, value_date)
        if cr is None:
            return None
        if value_key not in cr.keys():
            return None
        return cr[value_key]

    def load_csv(self):
        """
        Load a history CSV file
        :return: Returns a dict containing all of the records from the CSV file.
        """
        self._cache = {}
        csv_file = open(self._csv_file_path, "r", newline='')
        reader = csv.DictReader(csv_file)
        for r in reader:
            # Dict key is symbol:date
            key = QFCSVCacheFile._make_key(r[self._symbol], r[self._value_date])
            self._cache[key] = r
        csv_file.close()

        return self._cache

    def create_csv(self):
        """
        Create a new, empty CSV file
        :return:
        """
        csv_file = open(self._csv_file_path, "w", newline='')
        writer = csv.DictWriter(csv_file, fieldnames=self._csv_field_names)
        writer.writeheader()
        csv_file.close()

        self._cache = {}

    def add_cache_record(self, symbol, value_date, values):
        """
        Add/append a new CSV record
        :param symbol:
        :param value_date:
        :param values: A dict of values keyed by value_key. The keys MUST
        match the value_keys used to create the CSVCacheFile instance.
        :return: None
        """
        # Build the record to be appended to the CSV file
        row = {self._symbol: symbol, self._value_date: value_date}
        for k in self._value_keys:
            row[k] = values[k]

        # Open CSV file for appending
        csv_file = open(self._csv_file_path, "a", newline='')

        # Append the new record to cache file
        writer = csv.DictWriter(csv_file, fieldnames=self._csv_field_names)
        writer.writerow(row)
        csv_file.close()

        # Add to in-memory cache
        key = QFCSVCacheFile._make_key(symbol, value_date)
        self._cache[key] = values

    @staticmethod
    def _make_key(symbol, value_date):
        """
        Returns a compound key
        :param symbol: Ticker symbol
        :param value_date: ISO format date yyyy-mm-dd
        :return:
        """
        return symbol + ":" + value_date

