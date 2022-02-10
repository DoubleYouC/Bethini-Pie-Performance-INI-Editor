import tkinter as tk

class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.wait_time = 500
        self.wrap_length = 200
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<ButtonPress>', self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.wait_time, self.show_tip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show_tip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tw = tk.Toplevel(self.widget)

        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry('+%d+%d' % (x, y))
        label = tk.Label(self.tw, text=self.text, justify=tk.LEFT,
                         background='#ffffff', relief=tk.SOLID, borderwidth=1,
                         wraplength = self.wrap_length)
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()

if __name__ == '__main__':
    print('This is the tooltips module.')
