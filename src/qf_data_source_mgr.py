# coding: utf-8
#
# qf_data_source_mgr - financial market data management
# Copyright © 2018  Dave Hocker (email: Qalydon17@gmail.com)
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

from qf_configuration import QConfiguration
from qf_wsj import WSJDataSource
# from qf_iex import IEXDataSource
from qf_cnbc import CNBCDataSource
from qf_stooq import StooqDataSource
from qf_tiingo import TiingoDataSource
from qf_yahoo import YahooDataSource
from qf_app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class DataSourceMgr:
    """
    Singleton
    """
    qf_data_source_obj = None
    _sources = {
        "wsj": WSJDataSource(),
        # "iex": IEXDataSource(),
        "cnbc": CNBCDataSource(),
        "stooq": StooqDataSource(),
        "tiingo": TiingoDataSource(),
        "yahoo": YahooDataSource()
    }

    @classmethod
    def get_data_source(cls, data_source_name):
        if data_source_name in cls._sources.keys():
            logger.debug("Data source returned: %s", data_source_name)
            return cls._sources[data_source_name]
        else:
            logger.error("Unrecognized data source name %s", data_source_name)
            raise ValueError("Unrecognized data source name {0}".format(data_source_name))
