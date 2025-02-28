"""Modification of Hovertip"""

import sys
import tkinter as tk
from idlelib.tooltip import OnHoverTooltipBase
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

if __name__ == "__main__":
    sys.exit(1)


class Hovertip(OnHoverTooltipBase):
    """A tooltip that pops up when a mouse hovers over an anchor widget."""

    # Assigned in TooltipBase.__init__()
    anchor_widget: tk.Widget

    def __init__(
        self,
        anchor_widget: tk.Widget,
        text: str,
        preview_window: tk.Toplevel,
        preview_frame: ttk.Frame,
        photo_for_setting: Path | None,
        wrap_length: int = 250,
    ) -> None:
        """Create a text tooltip with a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, in milliseconds

        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.
        """

        super().__init__(anchor_widget, hover_delay=500)
        self.text = text
        self.wrap_length = wrap_length
        self.preview_window = preview_window
        self.preview_frame = preview_frame
        self.photo_for_setting = photo_for_setting
        self.preview_image: ImageTk.PhotoImage | None = None
        self.anchor_widget.bind("<Button-3>", self.show_preview)

    def showcontents(self) -> None:
        tk.Label(
            self.tipwindow,
            text=self.text,
            justify=tk.LEFT,
            background="#fff",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 10),
            wraplength=self.wrap_length,
        ).pack()

    def show_preview(self, _event: "tk.Event[tk.Widget] | None" = None) -> None:
        """Display the preview window."""

        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if self.photo_for_setting:
            if self.preview_image is None:
                self.preview_image = ImageTk.PhotoImage(Image.open(self.photo_for_setting))

            ttk.Label(
                self.preview_frame,
                image=self.preview_image,
            ).pack(anchor=tk.NW)

        ttk.Label(
            self.preview_frame,
            text=self.text,
            wraplength=1000,
        ).pack(anchor=tk.NW)
        self.preview_window.deiconify()
