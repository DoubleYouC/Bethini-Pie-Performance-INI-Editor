"""Modification of Hovertip"""

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from idlelib.tooltip import OnHoverTooltipBase

class Hovertip(OnHoverTooltipBase):
    """A tooltip that pops up when a mouse hovers over an anchor widget."""
    def __init__(self, anchor_widget, text, preview_list, wrap_length=250) -> None:
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
        self.preview_window = preview_list[0]
        self.preview_frame = preview_list[1]
        self.photo_for_setting = preview_list[2]

        self.anchor_widget.bind("<Button-3>", self.show_preview)

    def showcontents(self) -> None:
        label = tk.Label(self.tipwindow, text=self.text, justify=tk.LEFT,
                         background="#fff", relief=tk.SOLID, borderwidth=1,
                         font=('Segoe UI', 10), wraplength=self.wrap_length)
        label.pack()

    def show_preview(self, event=None) -> None:
        """Displays the preview window"""
        print(event)
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if self.photo_for_setting:
            self.show_photo()

        tooltip_label = ttk.Label(self.preview_frame, text=self.text, wraplength=1000)
        tooltip_label.pack(anchor=tk.NW)
        self.preview_window.deiconify()

    def show_photo(self) -> None:
        """Packs the image in the preview window."""
        preview_image = Image.open(self.photo_for_setting)
        tk_image = ImageTk.PhotoImage(preview_image)
        preview_label = ttk.Label(self.preview_frame, image=tk_image)
        preview_label.image = tk_image
        preview_label.pack(anchor=tk.NW)
