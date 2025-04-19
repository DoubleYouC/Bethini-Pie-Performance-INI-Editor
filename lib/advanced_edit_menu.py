import sys
import logging
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

if __name__ == "__main__":
    sys.exit(1)

from lib.customFunctions import set_titlebar_style

logger = logging.getLogger(__name__)

class AdvancedEditMenuPopup(ttk.Toplevel):
    def __init__(self, master, row_data: tuple, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Advanced Edit Menu")
        set_titlebar_style(self)
        self.grab_set()
        self.focus_set()
        self.result = None  # Will store the result from current_value_entry
        self.row_data = row_data

        # Set a minimum window size (width=500, height=300)
        self.minsize(500, 300)

        # Position the Toplevel window near the master window
        x = master.winfo_x()
        y = master.winfo_y()
        self.geometry(f"+{x + 100}+{y + 100}")

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=5, pady=5)


        ini_file_frame = ttk.Frame(info_frame)
        ini_file_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        ini_file_label = ttk.Label(ini_file_frame, text="INI File:")
        ini_file_label.pack(fill=tk.X, expand=NO, anchor=W, pady=3)
        ini_file_entry = ttk.Entry(ini_file_frame)
        ini_file_entry.insert(0, row_data[0])
        ini_file_entry.pack(fill=tk.X, expand=YES, anchor=W)
        ini_file_entry.bind(
            "<FocusOut>", lambda e: self.on_focus_out(e, row_data[0]))
        ini_file_entry.configure(style="secondary.TEntry")

        section_frame = ttk.Frame(info_frame)
        section_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        section_label = ttk.Label(section_frame, text="Section:")
        section_label.pack(fill=tk.X, expand=NO, anchor=W, pady=3)
        section_entry = ttk.Entry(section_frame)
        section_entry.insert(0, row_data[1])
        section_entry.pack(fill=tk.X, expand=YES, anchor=W)
        section_entry.bind(
            "<FocusOut>", lambda e: self.on_focus_out(e, row_data[1]))
        section_entry.configure(style="secondary.TEntry")

        setting_frame = ttk.Frame(info_frame)
        setting_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        setting_label = ttk.Label(setting_frame, text="Setting:")
        setting_label.pack(fill=tk.X, expand=NO, anchor=W, pady=3)
        setting_entry = ttk.Entry(setting_frame)
        setting_entry.insert(0, row_data[2])
        setting_entry.pack(fill=tk.X, expand=YES, anchor=W)
        setting_entry.bind(
            "<FocusOut>", lambda e: self.on_focus_out(e, row_data[2]))
        setting_entry.configure(style="secondary.TEntry")

        default_value_frame = ttk.Frame(info_frame)
        default_value_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        default_value_label = ttk.Label(
            default_value_frame, text="Default Value:")
        default_value_label.pack(fill=tk.X, expand=NO, anchor=W, pady=3)
        default_value_entry = ttk.Entry(default_value_frame)
        default_value_entry.insert(0, row_data[3])
        default_value_entry.pack(fill=tk.X, expand=YES, anchor=W)
        default_value_entry.bind(
            "<FocusOut>", lambda e: self.on_focus_out(e, row_data[3]))
        default_value_entry.configure(style="secondary.TEntry")

        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        notes_label = ttk.Label(notes_frame, text="Notes:")
        notes_label.pack(fill=tk.X, expand=NO, anchor=W, pady=3)
        self.notes_text = ttk.Text(notes_frame, height=14, wrap=WORD)
        self.notes_data = ""
        self.main_ini = master.app.get_main_ini_from_pecking_order(row_data[0])
        if master.app.does_setting_exist(ini=self.main_ini, section=row_data[1], setting=row_data[2]):
            self.notes_data = master.app.get_setting_notes(setting=row_data[2], section=row_data[1])
        self.notes_text.insert("1.0", self.notes_data)
        self.notes_text.pack(fill=tk.X, expand=YES, anchor=W)

        ttk.Separator(self).pack(fill=tk.X, expand=YES, pady=5)

        current_value_frame = ttk.Frame(self)
        current_value_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        current_value_label = ttk.Label(
            current_value_frame, text="Current Value:")
        current_value_label.pack(fill=tk.X, expand=NO, anchor=W, pady=3)
        self.current_value_entry = ttk.Entry(current_value_frame)
        self.current_value_entry.insert(0, row_data[4])
        self.current_value_entry.pack(fill=tk.X, expand=YES, anchor=W)
        self.current_value_entry.configure(style="primary.TEntry")

        self.save_button = ttk.Button(
            self, text="Save", style="success.TButton")
        self.save_button.pack(side=RIGHT, padx=5, pady=5)
        self.cancel_button = ttk.Button(
            self, text="Cancel", style="danger.TButton")
        self.cancel_button.pack(side=RIGHT, padx=5, pady=5)

        self.save_button.bind(
            "<Button-1>", lambda e: self.on_save(e))
        self.cancel_button.bind(
            "<Button-1>", lambda e: self.on_cancel(e))

    def on_save(self, event):
        # Retrieve the current value from the entry widget
        current_val = self.current_value_entry.get()
        if current_val != self.row_data[4]:
            logger.debug("Saved new value: " + str(self.row_data[0:3]) + " " + str(current_val))
            # Store the result so parent code can access it after wait_window
            self.result = current_val

        # Retrieve notes text
        notes = self.notes_text.get("1.0", tk.END).strip()
        if notes != self.notes_data:
            logger.info(f"New notes for {self.row_data[2]}:{self.row_data[1]}: {notes}")
            # Save the notes to the setting
            if self.master.app.update_setting_notes(
                    setting=self.row_data[2],
                    section=self.row_data[1],
                    notes=notes
            ):
                self.master.app.save_data()
                logger.info("Notes saved successfully.")

        self.destroy()

    def on_cancel(self, event):
        logger.debug("Cancel")
        self.destroy()

    def on_focus_out(self, event, default_value):
        widget = event.widget
        widget.delete(0, tk.END)
        widget.insert(0, default_value)