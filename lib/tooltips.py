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
        description: str,
        code: list[str] | None,
        preview_window: ttk.Toplevel,
        preview_frame: ttk.Frame,
        photo_for_setting: Path | None,
        bootstyle: str = None,
        wraplength: int = 250,
        delay: int = 500,
        **kwargs,
    ) -> None:
        """A tooltip popup window that shows text when the
        mouse is hovering over the widget and closes when the mouse is no
        longer hovering over the widget. Also serves as our Preview Window handler.


        ToolTip Parameters:

            widget (Widget):
                The tooltip window will position over this widget when
                hovering.

            text (str):
                The text to display in the tooltip window.

            description (str):
                The description to display in the preview window.

            code list[str]:
                A list of strings, typically ini settings in their section and ini file, placed inside a "code block" or Entry widget.

            preview_window (ttk.Toplevel):
                The toplevel widget for the preview window.

            preview_frame (ttk.Frame):
                The frame widget inside the preview window.

            photo_for_setting (Path):
                The photo to be placed inside the preview window.

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

        self.description = description
        self.preview_window = preview_window
        self.preview_frame = preview_frame
        self.photo_for_setting = photo_for_setting
        self.widget = widget
        self.code = code
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
            text=self.description,
            wraplength=1000,
        ).pack(anchor=NW, padx = 10, pady = 10)

        if self.code:
            code_text = ttk.Text(self.preview_frame)
            for iterator, line in enumerate(self.code, start = 1):
                code_text.insert(END, line + "\n")
                code_text.configure(height=iterator)
            code_text.pack(anchor=NW, padx = 10, pady=10)

        self.preview_window.minsize(300, 50)
        self.preview_window.deiconify()
