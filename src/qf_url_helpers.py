# coding: utf-8
#
# url_helpers.py - Reusable functions for accessing URLs from Python3
# Copyright (C) 2018  Dave Hocker (email: galydon17@gmail.com)
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
# along with this program (the LICENSE.md file). If not, see <http://www.gnu.org/licenses/>.
#
# For terms and conditions of IEX use see https://iextrading.com/api-exhibit-a
#

import urllib.request
import urllib.parse
import urllib.error

import ssl
import json
from qf_app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


def setup_cacerts(cacerts):
    """
    Set up SSL for the given URL.
    :param url_string:
    :return: None
    """
    ssl_ctx = ssl.create_default_context(cafile=cacerts)
    httpshandler = urllib.request.HTTPSHandler(context=ssl_ctx)
    opener = urllib.request.build_opener(httpshandler)
    urllib.request.install_opener(opener)


def exec_request(url_string, parms):
    """
     Submit https request to IEX
    :param url_string:
    :param parms:
    :param cacerts:
    :return: A dict containing results of https GET.
    the results key contains what was returned by the GET request.
    The status_code key is added to return the HTTPS status code.
    """

    status_code = 666

    try:
        if parms:
            url_enc = url_string + "?" + urllib.parse.urlencode(parms, quote_via=urllib.parse.quote_plus)
        else:
            url_enc = url_string
        logger.debug("HTTPS GET: %s", url_enc)
        response = urllib.request.urlopen(url_enc)
        status_code = response.getcode()
        logger.debug("Status code: %d", status_code)
        res = response.read()
        res = str(res, "utf-8")
    except urllib.error.HTTPError as ex:
        logger.error(ex.msg)
        logger.error(str(ex))
        return {"status_code":ex.code, "error_message":ex.msg}

    # Not every URL returns something
    if res:
        # Guard against invalid result returned by URL
        try:
            # In Python3 JSON produces string output which is Unicode
            j = {"result": json.loads(res)}
            logger.debug("JSON: %s", j)
        except:
            logger.error("HTTPS GET: %s", url_string)
            logger.error("Status code: %d", status_code)
            logger.error("Returned invalid/unexpected JSON response: %s", res)
            j = {"bad_payload": res}
        j["status_code"] = status_code
    else:
        j = {"status_code" : status_code}
    return j
