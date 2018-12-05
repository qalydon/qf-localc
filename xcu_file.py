#
# Create a component .xcu file describing its functions
# Copyright (C) 2017  Dave Hocker (email: qalydon17@gmail.com)
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

from xml.sax.saxutils import escape

class XCUFile:
    """
    Used to create a .xcu file describing extension functions.
    """
    def __init__(self, instance_id, auto_add_in):
        self.instance_id = instance_id
        self.auto_add_in = auto_add_in # XIex (the interface name)
        self.function_list = []
    
    def add_function(self, name, desc, parms):
        """
        Add a function to the manifest function list
        :param name: 
        :param desc: 
        :param parms: 
        :return: 
        """
        d = {}
        d["name"] = name
        d["desc"] = desc
        d["parms"] = parms
        self.function_list.append(d)

    def _generate_function(self, xcufile, name, desc, parms):
        xcufile.write('  <node oor:name="' + name + '" oor:op="replace">\n')
        xcufile.write('    <prop oor:name="DisplayName"><value xml:lang="en">' + escape(name) + '</value></prop>\n')
        xcufile.write('    <prop oor:name="Description"><value xml:lang="en">' + escape(desc) + '</value></prop>\n')
        xcufile.write('    <prop oor:name="Category"><value>Add-In</value></prop>\n')
        xcufile.write(
            '    <prop oor:name="CompatibilityName"><value xml:lang="en">AutoAddIn.' + self.auto_add_in + '.' + name + '</value></prop>\n')
        xcufile.write('    <node oor:name="Parameters">\n')

        for p, desc in parms:
            # Optional parameters will have a displayname enclosed in square brackets.
            p_name = p.strip("[]")
            xcufile.write('      <node oor:name="' + p_name + '" oor:op="replace">\n')
            xcufile.write('        <prop oor:name="DisplayName"><value xml:lang="en">' + escape(p_name) + '</value></prop>\n')
            xcufile.write('        <prop oor:name="Description"><value xml:lang="en">' + escape(desc) + '</value></prop>\n')
            xcufile.write('      </node>\n')

        xcufile.write('    </node>\n')
        xcufile.write('  </node>\n')

    def generate(self, file_name):
        """
        Generate the .xcu file from the function list
        :param file_name: full path to .xcu file
        :return: 
        """
    
        xcufile = open(file_name, 'w')
    
        xcufile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        xcufile.write(
            '<oor:component-data xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" oor:name="CalcAddIns" oor:package="org.openoffice.Office">\n')
        xcufile.write('<node oor:name="AddInInfo">\n')
        xcufile.write('<node oor:name="' + self.instance_id + '" oor:op="replace">\n')
        xcufile.write('<node oor:name="AddInFunctions">\n')

        for f in self.function_list:
            self._generate_function(xcufile, f["name"], f["desc"], f["parms"])

        xcufile.write('</node>\n')
        xcufile.write('</node>\n')
        xcufile.write('</node>\n')
        xcufile.write('</oor:component-data>\n')
    
        xcufile.close()

    def dump_functions(self):
        """
        Print a list of all of the defined functions
        :return:
        """
        print ("XCU Function List")
        for f in self.function_list:
            print (" ", f["name"], ":", f["desc"])
            for p_name, p_desc in f["parms"]:
                print ("   ", p_name.strip("[]"), ":", p_desc)

