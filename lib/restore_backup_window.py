import sys
import logging
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

if __name__ == "__main__":
    sys.exit(1)

logger = logging.getLogger(__name__)

class RestoreBackupWindow(ttk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Restore Backup")
        self.grab_set()
        self.focus_set()
        self.result = None
        # Set a minimum window size (width=500, height=300)
        self.minsize(500, 300)
        # Get the cursor position
        cursor_x = master.winfo_pointerx()
        cursor_y = master.winfo_pointery()
        # Set the position of the Toplevel window near the cursor
        self.geometry(f"+{cursor_x}+{cursor_y}")

        self.tk_dict = {}

        restore_frame = ttk.Frame(self)
        restore_frame_real = ttk.Frame(restore_frame)

        restore_frame.pack(fill=BOTH, expand=True)
        restore_frame_real.pack(anchor=NW, expand=True)

        for i, ini_file in enumerate(master.app.what_ini_files_are_used(), start=1):
            self.tk_dict[f"Frame_{i}"] = {}
            self.tk_dict[f"Frame_{i}"]["tkFrame"] = ttk.Frame(restore_frame_real)
            self.tk_dict[f"Frame_{i}"][f"Label_{i}"] = ttk.Label(self.tk_dict[f"Frame_{i}"]["tkFrame"], text=ini_file)
            self.tk_dict[f"Frame_{i}"][f"Entry_{i}"] = ttk.Entry(
                self.tk_dict[f"Frame_{i}"]["tkFrame"], width=50)
            self.tk_dict[f"Frame_{i}"][f"Entry_{i}"].insert(0, master.getINILocation(ini_file))

            self.tk_dict[f"Frame_{i}"]["tkFrame"].pack(padx=5, pady=5, anchor=NE)
            self.tk_dict[f"Frame_{i}"][f"Label_{i}"].pack(padx=5, pady=5, side=LEFT)
            self.tk_dict[f"Frame_{i}"][f"Entry_{i}"].pack(padx=5, pady=5)

        self.restore_button = ttk.Button(
            restore_frame, text="Restore", style="success.TButton")
        self.restore_button.pack(side=RIGHT, padx=5, pady=5)

        self.cancel_button = ttk.Button(
            restore_frame, text="Cancel", style="danger.TButton")
        self.cancel_button.pack(side=RIGHT, padx=5, pady=5)

        self.restore_button.bind(
            "<Button-1>", lambda e: self.on_restore(e))
        self.cancel_button.bind(
            "<Button-1>", lambda e: self.on_cancel(e))

    def on_restore(self, event):
        logger.debug("Restore backup")
        self.destroy()

    def on_cancel(self, event):
        logger.debug("Cancel restore backup")
        self.destroy()