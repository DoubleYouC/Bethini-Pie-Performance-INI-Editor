import tkinter as tk

class AutoScrollbar(tk.Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.pack_forget()
        else:
            if self.cget("orient") == 'horizontal':
                self.pack(side=tk.BOTTOM, fill=tk.X)
            else:
                self.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Scrollbar.set(self, lo, hi)

if __name__ == '__main__':
    print('This is the AutoScrollbar module.')