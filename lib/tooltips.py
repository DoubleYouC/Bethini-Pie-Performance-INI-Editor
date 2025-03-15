"""Modification of Hovertip"""

import sys
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from pathlib import Path

from PIL import Image, ImageTk

if __name__ == "__main__":
    sys.exit(1)

from lib.customFunctions import set_titlebar_style


class Hovertip(ToolTip):
    """A tooltip that pops up when a mouse hovers over an anchor widget."""

    def __init__(
        self,
        widget: tk.Widget,
        text: str,
        preview_window: ttk.Toplevel,
        preview_frame: ttk.Frame,
        photo_for_setting: Path | None,
        bootstyle: str = None,
        wraplength: int = 250,
        delay: int = 500,
        **kwargs,
    ) -> None:
        """A semi-transparent tooltip popup window that shows text when the
        mouse is hovering over the widget and closes when the mouse is no
        longer hovering over the widget. Clicking a mouse button will also
        close the tooltip.


        ToolTip Parameters:

            widget (Widget):
                The tooltip window will position over this widget when
                hovering.

            text (str):
                The text to display in the tooltip window.

            bootstyle (str):
                The style to apply to the tooltip label. You can use
                any of the standard ttkbootstrap label styles.

            wraplength (int):
                The width of the tooltip window in screenunits before the
                text is wrapped to the next line. By default, this will be
                a scaled factor of 300.

            **kwargs (Dict):
                Other keyword arguments passed to the `Toplevel` window.

        """

        super().__init__(
            widget,
            text,
            bootstyle,
            wraplength,
            delay,
            **kwargs,)

        self.text = text
        self.preview_window = preview_window
        self.preview_frame = preview_frame
        self.photo_for_setting = photo_for_setting
        self.widget = widget
        self.preview_image: ImageTk.PhotoImage | None = None
        self.widget.bind("<Button-3>", self.show_preview)

    def show_preview(self, _event: "tk.Event[tk.Widget] | None" = None) -> None:
        """Display the preview window."""

        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        set_titlebar_style(self.preview_window)

        if self.photo_for_setting:
            if self.preview_image is None:
                self.preview_image = ImageTk.PhotoImage(
                    Image.open(self.photo_for_setting))

            ttk.Label(
                self.preview_frame,
                image=self.preview_image,
            ).pack(anchor=NW)

        ttk.Label(
            self.preview_frame,
            text=self.text,
            wraplength=1000,
        ).pack(anchor=NW)
        self.preview_window.minsize(300, 50)
        self.preview_window.deiconify()
