import tkinter as tk

class AutoScrollbar(tk.Scrollbar):
    #def __init__(self, *args, **kwargs):
    #     tk.Scrollbar.__init__(self, *args, **kwargs)
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.pack_forget()
        else:
            if self.cget("orient") == 'horizontal':
                self.pack(side=tk.BOTTOM, fill=tk.X)
            else:
                self.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Scrollbar.set(self, lo, hi)




