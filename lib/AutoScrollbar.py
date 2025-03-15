"""This is the AutoScrollbar module."""

import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

if __name__ == "__main__":
    sys.exit(1)


class AutoScrollbar(ttk.Scrollbar):
    """This creates a scrollbar if necessary."""

    def set(self, first: float | str, last: float | str) -> None:
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.pack_forget()
        elif self.cget("orient") == HORIZONTAL:
            self.pack(side=BOTTOM, fill=X)
        else:
            self.pack(side=RIGHT, fill=Y)
        ttk.Scrollbar.set(self, first, last)
