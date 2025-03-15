"""This is the alpha_color_picker module."""

import sys
import ttkbootstrap as ttk
from collections import namedtuple
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Querybox
from ttkbootstrap.dialogs.colorchooser import (
    ColorChooser,
    ColorChooserDialog,
)

if __name__ == "__main__":
    sys.exit(1)

from lib.scalar import Scalar

ColorChoice = namedtuple("ColorChoice", "rgb hsl hex alpha")


class AlphaColorChooserDialog(ColorChooserDialog):
    """This class creates a color chooser dialog with an alpha slider."""

    def __init__(
        self, parent=None, title="Color Chooser", initialcolor=None, initialalpha=None
    ):
        super().__init__(parent, title, initialcolor)
        self.alpha = initialalpha

    def create_body(self, master):
        self.colorchooser = ColorChooser(master, self.initialcolor)
        self.colorchooser.pack(fill=BOTH, expand=YES)

        self.alpha_frame = ttk.Frame(master)
        self.alpha_label = ttk.Label(self.alpha_frame, text="Alpha:")
        self.alpha_var = ttk.IntVar(self)
        self.alpha_slider = Scalar(
            self.alpha_frame, from_=0, to=255, orient=HORIZONTAL, variable=self.alpha_var
        )
        self.alpha_spinbox = ttk.Spinbox(
            self.alpha_frame, from_=0, to=255, textvariable=self.alpha_var)
        self.alpha_var.set(self.alpha if self.alpha is not None else 255)
        if self.alpha is not None:
            self.alpha_frame.pack(fill=BOTH, expand=YES, padx=9)
            self.alpha_label.pack(fill=BOTH, expand=NO, side=LEFT)
            self.alpha_slider.pack(fill=BOTH, expand=YES, side=LEFT, padx=5)
            self.alpha_spinbox.pack(fill=BOTH, expand=NO, side=LEFT)

    def on_button_press(self, button):
        if button.cget("text") == "OK":
            values = self.colorchooser.get_variables()
            self.alpha = self.alpha_var.get()
            self._result = ColorChoice(
                rgb=(values.r, values.g, values.b),
                hsl=(values.h, values.s, values.l),
                hex=values.hex,
                alpha=self.alpha,
            )
            self._toplevel.destroy()
        self._toplevel.destroy()


class AlphaColorPicker(Querybox):
    """This class creates a query box with an alpha color picker."""

    def get_color(
        parent=None,
        title="Color Chooser",
        initialcolor=None,
        initialalpha=None,
        **kwargs
    ):
        """Show a color picker and return the select color when the
        user pressed OK.

        ![](../../assets/dialogs/querybox-get-color.png)

        Parameters:

            parent (Widget):
                The parent widget.

            title (str):
                Optional text that appears on the titlebar.

            initialcolor (str):
                The initial color to display in the 'Current' color
                frame.

        Returns:

            Tuple[rgb, hsl, hex, alpha]:
                The selected color in various colors models.
        """

        dialog = AlphaColorChooserDialog(
            parent, title, initialcolor, initialalpha)
        if "position" in kwargs:
            position = kwargs.pop("position")
        else:
            position = None
        dialog.show(position)
        return dialog.result