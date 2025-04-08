import sys
import logging
import ttkbootstrap as ttk
import shutil
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from pathlib import Path

if __name__ == "__main__":
    sys.exit(1)

from lib.customFunctions import set_titlebar_style

logger = logging.getLogger(__name__)


class RestoreBackupWindow(ttk.Toplevel):
    """RestoreBackupWindow shows the Restore Backup Window"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Restore Backup")
        set_titlebar_style(self)
        self.grab_set()
        self.focus_set()
        self.result = False
        # Set a minimum window size (width=500, height=300)
        self.minsize(400, 300)
        # Get the cursor position
        cursor_x = master.winfo_pointerx()
        cursor_y = master.winfo_pointery()
        # Set the position of the Toplevel window near the cursor
        self.geometry(f"+{cursor_x}+{cursor_y}")

        self.tk_dict = {}

        restore_frame = ttk.Frame(self)
        restore_frame_real = ttk.Frame(restore_frame)

        restore_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        restore_frame_real.pack(anchor=CENTER, expand=True)

        # Iterate over the ini files used by the application
        for i, ini_file in enumerate(master.app.what_ini_files_are_used(), start=1):
            n = 0
            self.tk_dict[f"Frame_{i}"] = {}
            self.tk_dict[f"Frame_{i}"]["tkFrame"] = ttk.Frame(
                restore_frame_real)
            self.tk_dict[f"Frame_{i}"][f"Label_{i}"] = ttk.Label(
                self.tk_dict[f"Frame_{i}"]["tkFrame"], text=ini_file)

            self.tk_dict[f"Frame_{i}"]["ini_file"] = ini_file
            ini_location = master.getINILocation(ini_file)
            self.tk_dict[f"Frame_{i}"]["ini_location"] = ini_location
            backup_directory = Path(ini_location, "Bethini Pie backups")
            self.tk_dict[f"Frame_{i}"]["backup_directory"] = backup_directory

            self.tk_dict[f"Frame_{i}"][f"Treeview_{i}"] = ttk.Treeview(
                self.tk_dict[f"Frame_{i}"]["tkFrame"], selectmode=BROWSE, show="tree", columns=("Backup"))

            # Populate the Treeview with backup directories containing the ini file
            for backup_location in backup_directory.iterdir():
                if backup_location.is_dir() and (backup_location / ini_file).exists():
                    has_backup = True
                    n += 1
                    self.tk_dict[f"Frame_{i}"][f"Treeview_{i}"].insert(
                        "", "end", id=backup_location.name, text=backup_location.name, values=ini_file)

            self.tk_dict[f"Frame_{i}"][f"restore_button_{i}"] = ttk.Button(
                self.tk_dict[f"Frame_{i}"]["tkFrame"], text="Restore Selected")

            #Limit the height of the treeview
            if n > 5:
                n = 5
            self.tk_dict[f"Frame_{i}"][f"Treeview_{i}"]["height"] = n + 2
            
            if n > 0:
                self.tk_dict[f"Frame_{i}"]["tkFrame"].pack(
                    padx=5, pady=5, anchor=CENTER)
                self.tk_dict[f"Frame_{i}"][f"Label_{i}"].pack(
                    padx=5, pady=5, anchor=NW)
                self.tk_dict[f"Frame_{i}"][f"Treeview_{i}"].pack(
                    padx=5, pady=5)
                self.tk_dict[f"Frame_{i}"][f"restore_button_{i}"].pack(
                    padx=5, pady=5)
                self.tk_dict[f"Frame_{i}"][f"restore_button_{i}"].pack_forget()

            # Bind the Treeview selection event to show the restore button
            self.tk_dict[f"Frame_{i}"][f"Treeview_{i}"].bind(
                "<ButtonRelease-1>", lambda e, i=i: self.on_treeview_click(e, i))

        self.close_button = ttk.Button(
            restore_frame, text="Close")
        self.close_button.pack(side=RIGHT, padx=10, pady=5)

        self.close_button.bind(
            "<Button-1>", lambda e: self.on_close(e))

        # Bind the window close event to the on_close method
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_close(None))

    def on_close(self, event):
        """Handle the window close event."""
        logger.debug("Closed restore backup window")
        if self.result:
            Messagebox.show_info(message="A backup has been restored. Bethini Pie will now close.",
                                 title="Bethini Pie will now close", parent=self)
            self.master.quit()
        self.destroy()

    def on_treeview_click(self, event, i):
        """Handle the Treeview selection event to show the restore button."""
        item = self.tk_dict[f"Frame_{i}"][f"Treeview_{i}"].focus()
        if item:
            self.tk_dict[f"Frame_{i}"][f"restore_button_{i}"].pack()
            self.tk_dict[f"Frame_{i}"][f"restore_button_{i}"].bind(
                "<Button-1>", lambda e, i=i, item=item: self.on_restore_button_click(e, i, item))
        else:
            self.tk_dict[f"Frame_{i}"][f"restore_button_{i}"].pack_forget()

    def on_restore_button_click(self, event, i, item):
        """Handle the restore button click event."""
        logger.debug(f"Restore button clicked for backup {item}")
        ini_file = self.tk_dict[f"Frame_{i}"]["ini_file"]
        backup_directory = Path(self.tk_dict[f"Frame_{i}"]["backup_directory"])
        backup_file = backup_directory / item / ini_file
        response = Messagebox.show_question(
            parent=self, title="Restore Backup", message=f"Are you sure you want to restore this backup?\n{backup_file}", buttons=["No:secondary", "Yes:primary"])
        logger.debug(f"User clicked {response}")
        if response == "No":
            Messagebox.show_info(parent=self, title="Cancelled restore",
                                 message="Restore backup cancelled. No files were modified.")
        elif response == "Yes":
            self.restore_backup(i, item)

    def restore_backup(self, i, item):
        """Restore the selected backup."""
        ini_file = self.tk_dict[f"Frame_{i}"]["ini_file"]
        ini_location = Path(self.tk_dict[f"Frame_{i}"]["ini_location"])
        backup_directory = Path(self.tk_dict[f"Frame_{i}"]["backup_directory"])
        original_file = ini_location / ini_file
        backup_file = backup_directory / item / ini_file
        logger.info(f"Restoring backup {backup_file} to {original_file}")
        try:
            shutil.copyfile(backup_file, original_file)
            msg = f"Restoring backup {backup_file} to {original_file} was successful."
            Messagebox.show_info(parent=self, title="Successfully restored backup",
                                 message=f"Restoring backup {backup_file} to {original_file} was successful.")
            logger.info(msg)
            self.result = True
        except FileNotFoundError:
            msg = f"Restoring {backup_file} to {original_file} failed due to {backup_file} not existing."
            logger.exception(msg)
            Messagebox.show_error(
                parent=self, title="Error restoring backup", message=msg)
