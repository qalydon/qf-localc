# coding: utf-8
#
# dump_db - Dumps the old sqlite database into CSV files
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

import os
import sqlite3
import csv
from qf_csv_cache_file import QFCSVCacheFile
from qf_configuration import QConfiguration


def convert(db_path):
    _dump_symboldate_table(db_path)
    _dump_ttmdividends_table(db_path)


def _dump_symboldate_table(db_path):
    # The columns in the old sqlite3 DB
    fieldnames = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Close']

    full_file_path = os.path.join(db_path, "symbol_date.csv")
    cache_file = QFCSVCacheFile(full_file_path,
                                symbol="Symbol", value_date="Date", value_keys=fieldnames)

    # Create empty CSV file with header
    cache_file.create_csv()

    # Open the old sqlite3 DB
    cnn = _open_db(os.path.join(db_path, "qf-cache-db.sqlite3"))

    # Select all price history records and dump them into a CSV file
    rset = cnn.execute("SELECT * from SymbolDate")
    rows = rset.fetchall()
    for r in rows:
        row = {}
        for c in fieldnames:
            row[c] = r[c]
        # print(row)
        try:
            cache_file.add_cache_record(r["Symbol"], r["Date"], row)
        except Exception as ex:
            print(str(ex))

    cnn.close()


def _dump_ttmdividends_table(db_path):
    fieldnames = ['Amount']

    # Create empty CSV file with header
    full_file_path = os.path.join(db_path, "ttmdividends.csv")
    cache_file = QFCSVCacheFile(full_file_path,
                                symbol="Symbol", value_date="CalcDate", value_keys=fieldnames)
    cache_file.create_csv()

    # Open the old sqlite DB
    cnn = _open_db(os.path.join(db_path, "qf-cache-db.sqlite3"))

    # Select all dividend history records and dump them into a CSV file
    rset = cnn.execute("SELECT * from TTMDividends")
    rows = rset.fetchall()
    for r in rows:
        # print(r["Symbol"], r["CalcDate"], r["Amount"])
        row = {"Amount": r["Amount"]}
        try:
            cache_file.add_cache_record(r["Symbol"], r["CalcDate"], row)
        except Exception as ex:
            print(str(ex))

    cnn.close()


def _load_csv(csv_file_path, symbol="", value_date="", value=""):
    """
    Load a history CSV file
    :param csv_file_path: The CSV file to be loaded
    :param symbol: The ticker symbol key
    :param value_date: The date key
    :param value: The value key
    :return: Returns a dict containing all of the records from the CSV file.
    """
    hist_price_cache = {}
    csv_file = open(csv_file_path, "r", newline='')
    reader = csv.DictReader(csv_file)
    for r in reader:
        # Dict key is symbol:date
        key = r[symbol] + ":" + r[value_date]
        hist_price_cache[key] = r[value]
        print(r[symbol], r[value_date], r[value])
    csv_file.close()

    return hist_price_cache


def _open_db(full_file_path):
    """
    Open a connection to the cache DB.
    :return: Database connection.
    """
    conn = sqlite3.connect(full_file_path)

    # We use the row factory to get named row columns. Makes handling row sets easier.
    conn.row_factory = sqlite3.Row
    # The default string type is unicode. This changes it to UTF-8.
    conn.text_factory = str

    # return connection to the cache DB
    return conn


def test_csv_files(db_path):
    """
    Test the converted CSV files using well-known symbols and dates.
    :param db_path: Path to directory where CSV files are kept.
    :return: None
    """
    price_cache = QFCSVCacheFile(os.path.join(db_path, "symbol_date.csv"),
                                 symbol="Symbol", value_date="Date",
                                 value_keys=['Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Close'])
    price_cache.load_csv()

    print("Look up price for key BSCK 2020-10-30")
    v = price_cache.get_cache_value("BSCK", "2020-10-30", "Close")
    print(float(v))

    print("New price history record")
    rec = {
        'Open': 0.0,
        'High': 0.0,
        'Low': 0.0,
        'Close': 99.99,
        'Volume': 0,
        'Adj_Close': 0.0
    }
    price_cache.add_cache_record("ZZZZ", "2022-01-06", rec)
    v = price_cache.get_cache_value("ZZZZ", "2022-01-06", 'Close')
    print(v)

    dividend_cache = QFCSVCacheFile(os.path.join(db_path, "ttmdividends.csv"),
                                    symbol="Symbol", value_date="CalcDate", value_keys=["Amount"])
    dividend_cache.load_csv()

    print("Look up dividend for VOO 2020-07-31")
    v = dividend_cache.get_cache_value("VOO", "2020-07-31", 'Amount')
    print(float(v))


if '__main__' == __name__:
    db_path = QConfiguration.qf_cache_db
    print("Converting DB to CSV in directory:", db_path)
    db_path = os.path.dirname(db_path)
    convert(db_path)
    print("Converted")
    # print("Testing...")
    # test_csv_files(db_path)
