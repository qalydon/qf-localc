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
from qf_iex import IEXDataSource
from qf_stooq import StooqDataSource
from qf_app_logger import AppLogger


# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class DataSourceMgr:
    """
    Singleton
    """
    qf_data_source_obj = None

    @classmethod
    def create_data_source(cls):
        if QConfiguration.qf_data_source == "wsj":
            cls.qf_data_source_obj = WSJDataSource()
        elif QConfiguration.qf_data_source == "iex":
            cls.qf_data_source_obj = IEXDataSource()
        elif QConfiguration.qf_data_source == "stooq":
            cls.qf_data_source_obj = StooqDataSource()
        else:
            logger.error("Unrecognized data source %s", QConfiguration.qf_data_source)
            raise ValueError("Unrecognized data source {0}".format(QConfiguration.qf_data_source))
        logger.debug("Data source created: %s", QConfiguration.qf_data_source)

    @classmethod
    def data_source(cls):
        """
        Returns the currently configured data source
        :return:
        """
        return QConfiguration.qf_data_source