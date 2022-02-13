from tkinter import *
from idlelib.tooltip import OnHoverTooltipBase

class Hovertip(OnHoverTooltipBase):
    "A tooltip that pops up when a mouse hovers over an anchor widget."
    def __init__(self, anchor_widget, text, wrap_length=250, hover_delay=1000):
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

    def showcontents(self):
        label = Label(self.tipwindow, text=self.text, justify=LEFT,
                      background="#fff", relief=SOLID, borderwidth=1,
                      font=('Segoe UI','10'), wraplength=self.wrap_length)
        label.pack()