#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import tkinter as tk
from typing import TYPE_CHECKING, Literal

import ttkbootstrap as ttk

if TYPE_CHECKING:
    from lib.type_helpers import *


class Scalar(ttk.Scale):
    """A ttk.Scale with limited decimal places."""

    def __init__(
        self,
        master: tk.Misc | None = None,
        # command: str | Callable[[str], object] = "",
        from_: float = 0,
        length: int = 100,
        orient: Literal["horizontal", "vertical"] = "horizontal",
        to: float = 1,
        variable: ttk.IntVar | ttk.DoubleVar | None = None,
        decimal_places: IntStr = "0",
    ) -> None:
        self.decimal_places = int(decimal_places)
        # Currently unused. Supports the above commented command parameter.
        # if command:
        #     self.chain = command
        # else:
        #     self.chain = lambda *_a: None
        super().__init__(master, command=self._value_changed, from_=from_, length=length, orient=orient, to=to)
        self.variable = variable
        if self.variable:
            self.configure(variable=self.variable)

    def _value_changed(self, _new_value: str) -> None:
        if self.variable:
            value = self.get()
            value = int(value) if self.decimal_places == 0 else round(value, self.decimal_places)

            if isinstance(self.variable, ttk.IntVar):
                self.variable.set(int(value))
            else:
                self.variable.set(value)

            # See above comments.
            # if isinstance(self.chain, str):
            #     pass
            # else:
            #     self.chain(value)
