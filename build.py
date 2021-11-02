#! /usr/local/bin/python3
#
# Package extension files into an .oxt file
# Copyright © 2017, 2020  Dave Hocker (email: qalydon17@gmail.com)
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
# References
# https://wiki.openoffice.org/wiki/Calc/Add-In/Python_How-To
# http://www.biochemfusion.com/doc/Calc_addin_howto.html
# https://github.com/madsailor/SMF-Extension
#
# How to run a build on macOS X:
#
# lo_sdk.sh
# python3 build.py [next]
#
# where:
#   next option causes the build number to be incremented. This updates the src/description.xml file.
#
# How to run a build on Windows:
#
# lo_sdk.bat
# python build.py [next]
#
# where:
#   next option causes the build number to be incremented. This updates the src/description.xml file.
#

import os
import sys
import subprocess
import shutil
from xcu_file import XCUFile
import xml.etree.ElementTree as etree

# Set up environment vars
if sys.platform == 'darwin':
    # macOS
    # Be sure to run lo_sdk.sh first
    os.environ["PATH"] = os.environ["PATH"] + ":/usr/lib/ure/bin/"
    os.environ["PATH"] = os.environ["PATH"] + ":/Users/dhocker/LibreOffice6.0_SDK/bin"
    os.environ["DYLD_LIBRARY_PATH"] = os.environ["OO_SDK_URE_LIB_DIR"]
elif sys.platform == 'win32':
    # Windows
    # Nothing special required. Be sure to run lo_sdk.bat first.
    pass
else:
    # TODO figure out how to build on other OSes
    print ("Platform {0} is not supported by this build script".format(sys.platform))
    exit(1)
#subprocess.call("env")
#print (os.environ["DYLD_LIBRARY_PATH"])

# Recognized command line args
incr_version = len(sys.argv) == 2 and sys.argv[1].lower() == "next"

# Extract version from description.xml
tree = etree.parse("src/description.xml")
root = tree.getroot()
# There should only be one version node
nodes = root.findall('{http://openoffice.org/extensions/description/2006}version')
build_version = nodes[0].attrib["value"]

# Update build number as required
if incr_version:
    parts = build_version.split(".")
    build_num = parts[len(parts) - 1]
    build_num = str(int(build_num) + 1)
    parts[len(parts) - 1] = build_num
    build_version = str.join(".", parts)
    nodes[0].attrib["value"] = build_version
    # Note that this will rewrite the entire file and the results will likely
    # look substantially different.
    tree.write("src/description.xml", xml_declaration=False, encoding="utf-8",)
    print("Build number incremented")

print ("=============================")
print ("Building Version:", build_version)
print ("=============================")

# Clean build folder
print ("Cleaning build folder...")
shutil.rmtree("build", ignore_errors=True)

# Create required build folders
if not os.path.exists("build"):
    print ("Creating new build folder")
    os.mkdir("build")
if not os.path.exists("build/META-INF"):
    print ("Creating build/META-INF folder")
    os.mkdir("build/META-INF")

# Compile idl
subprocess.run(["idlc", "-w", "idl/xqf.idl"], stdout=sys.stdout, stderr=sys.stderr)
subprocess.run(["regmerge", "-v", "build/xqf.rdb", "UCR", "idl/xqf.urd"])
os.remove("idl/xqf.urd")

# Copy all required files to build folder
print ("Copying files to build folder")
shutil.copy("src/manifest.xml", "build/META-INF/")
shutil.copy("src/description-en-US.txt", "build/")
shutil.copy("src/description.xml", "build/")
shutil.copy("src/qf_impl.py", "build/")
shutil.copy("src/qf_hist_quote.py", "build/")
shutil.copy("src/qf_dividends.py", "build/")
shutil.copy("src/qf_stooq.py", "build/")
shutil.copy("src/qf_wsj.py", "build/")
# shutil.copy("src/qf_iex.py", "build/")
shutil.copy("src/qf_cnbc.py", "build/")
shutil.copy("src/qf_tiingo.py", "build/")
shutil.copy("src/qf_tiingo_support.py", "build/")
shutil.copy("src/qf_yahoo.py", "build/")
shutil.copy("src/qf_data_source_base.py", "build/")
shutil.copy("src/qf_data_source_mgr.py", "build/")
shutil.copy("src/qf_app_logger.py", "build/")
shutil.copy("src/qf_configuration.py", "build/")
shutil.copy("src/qf_extn_helper.py", "build/")
shutil.copy("src/qf_url_helpers.py", "build/")
shutil.copy("src/qf_cache_db.py", "build/")
shutil.copy("src/qf_dialog_box.py", "build/")
shutil.copy("src/qf_home.py", "build/")
shutil.copytree("src/sqlite3", "build/sqlite3", dirs_exist_ok=True)
shutil.copy("certifi/cacert.pem", "build/")

# Generate the XCU file
print ("Generating qf.xcu")
xcu = XCUFile("com.qf.api.localc.python.QFImpl", "XQFinance")
#
# Note: DO NOT use underscores in parameter names. LO does not accept them.
# Note: Be careful using any special characters in descriptions and comments.
# This stuff ends up in an XML file and hence has all of the same restrictions.
# The xcu_file class escapes all descriptions in an attemp to avoid problems.
#
xcu.add_function("QFVersion", "Get extension version",
                 [
                 ])
xcu.add_function("QFDataSource", "Get current data source",
                 [
                     ('category', 'stock, etf, mutf, or index')
                 ])
xcu.add_function("QFClosingPrice", "Get the closing price for a date",
                 [
                     ('symbol', 'The stock ticker symbol for the price'),
                     ('category', 'stock, etf, mutf, or index'),
                     ('fordate', 'The date YYYY-MM-DD')
                 ])
xcu.add_function("QFOpeningPrice", "Get the opening price for a date",
                 [
                     ('symbol', 'The stock ticker symbol for the price'),
                     ('category', 'stock, etf, mutf, or index'),
                     ('fordate', 'The date YYYY-MM-DD')
                 ])
xcu.add_function("QFHighPrice", "Get the high price for a date",
                 [
                     ('symbol', 'The stock ticker symbol for the price'),
                     ('category', 'stock, etf, mutf, or index'),
                     ('fordate', 'The date YYYY-MM-DD')
                 ])
xcu.add_function("QFLowPrice", "Get the low price for a date",
                 [
                     ('symbol', 'The stock ticker symbol for the price'),
                     ('category', 'stock, etf, mutf, or index'),
                     ('fordate', 'The date YYYY-MM-DD')
                 ])
xcu.add_function("QFDayVolume", "Get the trading volume for a date",
                 [
                     ('symbol', 'The stock ticker symbol for the volume'),
                     ('category', 'stock, etf, mutf, or index'),
                     ('fordate', 'The date YYYY-MM-DD')
                 ])
xcu.add_function("QFTTMDividend", "Get the trailing 12 months dividend",
                 [
                     ('symbol', 'The stock ticker symbol for the dividend'),
                     ('fordate', 'The ending date of the 12 month period YYYY-MM-DD')
                 ])
# xcu.add_function("IexHistoricalQuote", "Get a closing quote for a date",
#                  [
#                      ('symbol', 'The stock ticker symbol for the quote'),
#                      ('fordate', 'The date YYYY-MM-DD')
#                  ])

xcu.generate("build/qf.xcu")
xcu.dump_functions()

# Zip contents of build folder and rename it to .oxt
print ("Zipping build files into qf.oxt file")
os.chdir("build/")
for f in os.listdir("./"):
    if os.path.isfile(f) or os.path.isdir(f):
        subprocess.run(["zip", "-r", "qf.zip", f])
os.chdir("..")
shutil.move("build/qf.zip", "qf.oxt")
print ("Extension file qf.oxt created")

print ("============================================")
print ("Build complete for Version:", build_version)
print ("============================================")
