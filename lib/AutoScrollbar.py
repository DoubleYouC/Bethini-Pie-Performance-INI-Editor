"""This is the AutoScrollbar module."""

import sys
import tkinter as tk

if __name__ == "__main__":
    sys.exit(1)


class AutoScrollbar(tk.Scrollbar):
    """This creates a scrollbar if necessary."""
    def set(self, first: float | str, last: float | str) -> None:
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.pack_forget()
        elif self.cget("orient") == "horizontal":
            self.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Scrollbar.set(self, first, last)
