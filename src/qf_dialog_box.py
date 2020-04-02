# coding: utf-8
#
# LO Calc dialog box
# Copyright © 2019  Dave Hocker as Qalydon (email: qalydon17@gmail.com)
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

from qf_app_logger import AppLogger
# from qf_configuration import QConfiguration

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


class QFDialogBox:
    def __init__(self):
        pass

    def show(self, dlg_title, dlg_text):
        try:
            return self._show_dialog_box(dlg_title, dlg_text)
        except Exception as ex:
            logger.error("Exception showing dialog box")
            logger.error(str(ex))

    def _add_awt_model(self, dlg_model, srv, ctl_name, prop_list):
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
            #works with awt.UnoControlDialogElement only:
            ctl_model.Name = ctl_name
        dlg_model.insertByName(ctl_name, ctl_model)

    def _show_dialog_box(self, dlg_title, dlg_text):
        """
        Ask user for Intrinio login credentials
        :return: If successful, returns username and password as a tuple (something truthy)
        If canceled, returns False.
        """
        # Reference: https://www.openoffice.org/api/docs/common/ref/com/sun/star/awt/module-ix.html
        global logger

        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        dlg_model = smgr.createInstance("com.sun.star.awt.UnoControlDialogModel")
        dlg_model.Title = dlg_title

        self._add_awt_model(dlg_model, 'FixedText', 'message', {
            'MultiLine': True,
            'Label': dlg_text,
        })

        # self._add_awt_model(dlg_model, 'Edit', 'txtName', {})
        #
        # self._add_awt_model(dlg_model, 'FixedText', 'lblPWD', {
        #     'Label': 'Password',
        # }
        #                )
        # self._add_awt_model(dlg_model, 'Edit', 'txtPWD', {
        #     'EchoChar': 42,
        # }
        #                )
        #
        # self._add_awt_model(dlg_model, 'CheckBox', 'cbDoNotAsk', {
        #     'Label': 'Do not ask again',
        # }
        #                )

        self._add_awt_model(dlg_model, 'Button', 'btnOK', {
            'Label': 'OK',
            'DefaultButton': True,
            'PushButtonType': 1,
        })
        # self._add_awt_model(dlg_model, 'Button', 'btnCancel', {
        #     'Label': 'Cancel',
        #     'PushButtonType': 2,
        # }
        #                )

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
            "message": [lmargin, tmargin, 400, cheight * 3],
            "btnOK": [lmargin + 200 - 50 - 5, tmargin + (theight * 3), 100, cheight],
        }

        dialog = smgr.createInstance("com.sun.star.awt.UnoControlDialog")
        dialog.setModel(dlg_model)

        # Apply layout to controls. Must be done within the dialog.
        for name, d in layout.items():
            ctl = dialog.getControl(name)
            ctl.setPosSize(d[0], d[1], d[2], d[3], POSSIZE)

        dialog.setPosSize(300, 300, lmargin + rmargin + 400, tmargin + bmargin + (theight * 4), POSSIZE)
        dialog.setVisible(True)

        # Run the dialog. Returns the value of the PushButtonType.
        # 1 = OK
        button_id = dialog.execute()
        logger.debug("Dialog box returned: %s", button_id)
        return button_id