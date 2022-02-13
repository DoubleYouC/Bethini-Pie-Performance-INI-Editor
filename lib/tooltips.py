"""Modification of Hovertip"""


from idlelib.tooltip import OnHoverTooltipBase

from tkinter import *
from tkinter import ttk

from PIL import Image, ImageTk



class Hovertip(OnHoverTooltipBase):
    """A tooltip that pops up when a mouse hovers over an anchor widget."""
    def __init__(self, anchor_widget, text, PREVIEW_WINDOW, PREVIEW_FRAME, photo_for_setting=None, wrap_length=250, hover_delay=1000):
        """Create a text tooltip with a mouse hover delay.

        anchor_widget: the widget next to which the tooltip will be shown
        hover_delay: time to delay before showing the tooltip, in milliseconds

        Note that a widget will only be shown when showtip() is called,
        e.g. after hovering over the anchor widget with the mouse for enough
        time.
        """
        super(Hovertip, self).__init__(anchor_widget, hover_delay=hover_delay)
        self.text = text
        self.wrap_length = wrap_length
        self.preview_window = PREVIEW_WINDOW
        self.photo_for_setting = photo_for_setting
        self.preview_frame = PREVIEW_FRAME

    def showcontents(self):
        label = Label(self.tipwindow, text=self.text, justify=LEFT,
                      background="#fff", relief=SOLID, borderwidth=1,
                      font=('Segoe UI','10'), wraplength=self.wrap_length)
        if self.photo_for_setting:
            for widget in self.preview_frame.winfo_children():
                widget.destroy()

            preview_image = Image.open(self.photo_for_setting)
            tk_image = ImageTk.PhotoImage(preview_image)

            preview_label = ttk.Label(self.preview_frame, image=tk_image)
            preview_label.image = tk_image
            preview_label.pack(anchor=NW)

            tooltip_label = ttk.Label(self.preview_frame, text=self.text)
            tooltip_label.pack(anchor=NW)
            self.preview_window.deiconify()
        label.pack()
