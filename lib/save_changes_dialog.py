import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from lib.tableview_scrollable import TableviewScrollable
from lib.ModifyINI import ModifyINI

if __name__ == "__main__":
    sys.exit(1)


class SaveChangesDialog(ttk.Toplevel):
    def __init__(self, parent, ini_object: ModifyINI, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.ini_object = ini_object
        ini_name = ini_object.ini_path.name
        self.result = False

        self.title(f"Save {ini_name}?")
        self.minsize(600, 500)
        self.grab_set()
        self.focus_set()

        # Set the position of the window to align with the Northwest corner of the parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        self.geometry(f"+{parent_x}+{parent_y}")

        # Create a frame for the table
        frame = ttk.Frame(self)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        question = ttk.Label(
            frame, text=f"Would you like to save the following changes to {ini_name}?")
        question.pack(fill=X, expand=False, pady=5)

        # Create the TableviewScrollable
        coldata = ["Section", "ID", "Change"]
        rowdata = [
            (section, setting, value)
            for section, settings in ini_object.modifications.items()
            for setting, value in settings.items()
        ]
        self.table = TableviewScrollable(
            frame, coldata=coldata, rowdata=rowdata, searchable=False, autoalign=False, yscrollbar=True)
        self.table.pack(fill=BOTH, expand=True)
        self.table.autofit_columns()

        # Create buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=X, padx=10, pady=10)

        save_button = ttk.Button(
            button_frame, text="Save", command=self.on_save, style="success.TButton")
        save_button.pack(side=RIGHT, padx=5)

        cancel_button = ttk.Button(
            button_frame, text="Cancel", command=self.on_cancel, style="danger.TButton")
        cancel_button.pack(side=RIGHT, padx=5)

    def on_save(self):
        self.result = True
        self.destroy()

    def on_cancel(self):
        self.result = False
        self.destroy()
