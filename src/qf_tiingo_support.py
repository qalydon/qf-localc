# coding: utf-8
#
# qf_tiingo_support - Support functions for Tiingo, including API key entry.
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
# This code was adapted from https://github.com/qalydon/intrinio-localc/blob/master/src/intrinio_access.py
# Trying to do a dialog box under LibreOffice (or OpenOffice) is extremely complicated.
#

from qf_app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()

try:
    import uno
    logger.debug("Attempt to import uno succeeded")
    # logger.debug("sys.path = %s", sys.path)
except Exception as ex:
    logger.error("Attempt to import uno failed %s", str(ex))
try:
    # https://www.openoffice.org/api/docs/common/ref/com/sun/star/awt/PosSize.html
    from com.sun.star.awt.PosSize import POSSIZE # flags the x- and y-coordinate, width and height
    logger.debug("Attempt to import com.sun.star.awt.PosSize succeeded")
except Exception as ex:
    logger.error("Attempt to import com.sun.star.awt.PosSize failed %s", str(ex))


def _add_awt_model(dlg_model, srv, ctl_name, prop_list):
    """
    Helper function for building dialog
    Insert UnoControl<srv>Model into given DialogControlModel
    :param dlg_model: dialog model where control is to be added
    :param srv: control model type to be added
    :param ctl_name: name to be assigned to the control model
    :param prop_list: properties to be assigned to new control model
    :return: None
    """
    ctl_model = dlg_model.createInstance("com.sun.star.awt.UnoControl" + srv + "Model")
    while prop_list:
        prp = prop_list.popitem()
        uno.invoke(ctl_model,"setPropertyValue",(prp[0],prp[1]))
        # works with awt.UnoControlDialogElement only:
        ctl_model.Name = ctl_name
    dlg_model.insertByName(ctl_name, ctl_model)


def api_key():
    """
    Ask user for Tiingo API key
    :return: If successful, returns API key as a tuple (something truthy)
    If canceled, returns False.
    """
    # Reference: https://www.openoffice.org/api/docs/common/ref/com/sun/star/awt/module-ix.html
    global logger

    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    dlg_model = smgr.createInstance("com.sun.star.awt.UnoControlDialogModel")
    dlg_model.Title = 'Enter Tiingo API Key'

    _add_awt_model(dlg_model, 'FixedText', 'lblApiKey', {
        'Label': 'API Key',
        }
    )
    _add_awt_model(dlg_model, 'Edit', 'txtApiKey', {
        'EchoChar': 42,
        }
    )

    _add_awt_model(dlg_model, 'Button', 'btnOK', {
        'Label': 'Save',
        'DefaultButton': True,
        'PushButtonType': 1,
        }
    )
    _add_awt_model(dlg_model, 'Button', 'btnCancel', {
        'Label': 'Cancel',
        'PushButtonType': 2,
        }
    )

    lmargin = 10  # left margin
    rmargin = 10  # right margin
    tmargin = 10  # top margin
    bmargin = 10  # bottom margin
    cheight = 25  # control height
    pad = 5  # top/bottom padding where needed
    theight = cheight + pad  # total height of a control

    # Poor man's grid
    # layout "control-name", [x, y, w, h]
    layout = {
        "lblApiKey": [lmargin, tmargin + (theight * 1), 100, cheight],
        "txtApiKey": [lmargin + 100, tmargin + (theight * 1), 250, cheight],
        "btnOK": [lmargin + 100, tmargin + (theight * 3), 100, cheight],
        "btnCancel": [lmargin + 200, tmargin + (theight * 3), 100, cheight]
    }

    dialog = smgr.createInstance("com.sun.star.awt.UnoControlDialog")
    dialog.setModel(dlg_model)
    api_key_ctl = dialog.getControl('txtApiKey')

    # Apply layout to controls. Must be done within the dialog.
    for name, d in layout.items():
        ctl = dialog.getControl(name)
        ctl.setPosSize(d[0], d[1], d[2], d[3], POSSIZE)

    dialog.setPosSize(300, 300, lmargin + rmargin + 100 + 250, tmargin + bmargin + (theight * 4), POSSIZE)
    dialog.setVisible(True)

    # Run the dialog. Returns the value of the PushButtonType.
    # 1 = save
    # 2 = cancel
    button_id = dialog.execute()
    logger.debug("Tiingo API key dialog returned: %s", button_id)
    # Unfortunately there is no way to validate an API key, other than attempting to use it
    if button_id == 1:
        return tuple([True, api_key_ctl.getText()])
    else:
        return tuple([False])
