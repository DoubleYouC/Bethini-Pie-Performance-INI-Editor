import sys
import logging
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

if __name__ == "__main__":
    sys.exit(1)

from lib.ModifyINI import ModifyINI
from lib.customFunctions import set_titlebar_style

logger = logging.getLogger(__name__)


class preferences(ttk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Preferences")
        set_titlebar_style(self)
        self.grab_set()
        self.focus_set()
        self.result = None

        # Set a minimum window size (width=500, height=300)
        self.minsize(300, 100)

        # Get the cursor position
        cursor_x = master.winfo_pointerx()
        cursor_y = master.winfo_pointery()

        # Set the position of the Toplevel window near the cursor
        self.geometry(f"+{cursor_x}+{cursor_y}")

        preferences_frame = ttk.Frame(self)
        preferences_frame_real = ttk.Frame(preferences_frame)

        general_lf = ttk.LabelFrame(preferences_frame_real, text="General")

        log_level_frame = ttk.Frame(general_lf)
        log_level_label = ttk.Label(log_level_frame, text="Log Level")
        self.log_level_var = ttk.StringVar(self)
        log_level_mb = ttk.Menubutton(log_level_frame, textvariable=self.log_level_var)
        log_level_menu = ttk.Menu(log_level_mb)
        log_level_list = ["Critical",
                          "Error",
                          "Warning",
                          "Info",
                          "Debug"]
        for option in log_level_list:
            log_level_menu.add_radiobutton(label=option, value=option, variable=self.log_level_var)
        log_level_mb["menu"] = log_level_menu
        self.log_level_var.set(ModifyINI.app_config().get_value("General", "sLogLevel", "Info"))

        max_backup_frame = ttk.Frame(general_lf)
        max_backups_label = ttk.Label(
            max_backup_frame, text="Max Backups to Keep")
        self.max_backups_var = ttk.StringVar(self)
        max_backups_sb = ttk.Spinbox(
            max_backup_frame, from_=-1, to=100, increment=1, width=5, textvariable=self.max_backups_var)
        self.max_backups_var.set(ModifyINI.app_config().get_value(
            "General", "iMaxBackups", "-1"))

        max_logs_frame = ttk.Frame(general_lf)
        max_logs_label = ttk.Label(max_logs_frame, text="Max Logs to Keep")
        self.max_logs_var = ttk.StringVar(self)
        max_logs_sb = ttk.Spinbox(
            max_logs_frame, from_=-1, to=100, increment=1, width=5, textvariable=self.max_logs_var)
        self.max_logs_var.set(ModifyINI.app_config().get_value(
            "General", "iMaxLogs", "5"))

        always_select_game_frame = ttk.Frame(general_lf)
        self.always_select_game_var = ttk.StringVar(self)
        always_select_game_cb = ttk.Checkbutton(
            always_select_game_frame, text="Always Select Game", onvalue="1", offvalue="0")
        always_select_game_cb.var = self.always_select_game_var
        always_select_game_cb.var.set(ModifyINI.app_config().get_value(
            "General", "bAlwaysSelectGame", "1"))
        always_select_game_cb.configure(variable=always_select_game_cb.var)

        preferences_frame.pack(fill=BOTH, expand=True)
        preferences_frame_real.pack(anchor=CENTER, expand=True)
        general_lf.pack(anchor=CENTER, padx=10, pady=10)

        log_level_frame.pack(anchor=E, padx=10, pady=10)
        log_level_label.pack(side=LEFT)
        log_level_mb.pack(padx=10)

        max_backup_frame.pack(anchor=E, padx=10, pady=10)
        max_backups_label.pack(side=LEFT)
        max_backups_sb.pack(padx=10)

        max_logs_frame.pack(anchor=E, padx=10, pady=10)
        max_logs_label.pack(side=LEFT)
        max_logs_sb.pack(padx=10)

        always_select_game_frame.pack(anchor=E, padx=10, pady=10)
        always_select_game_cb.pack(side=LEFT, padx=10)

        self.save_button = ttk.Button(
            preferences_frame, text="Save", style="success.TButton")
        self.save_button.pack(side=RIGHT, padx=5, pady=5)
        self.cancel_button = ttk.Button(
            preferences_frame, text="Cancel", style="danger.TButton")
        self.cancel_button.pack(side=RIGHT, padx=5, pady=5)

        self.save_button.bind(
            "<Button-1>", lambda e: self.on_save(e))
        self.cancel_button.bind(
            "<Button-1>", lambda e: self.on_cancel(e))

    def on_save(self, event):
        logger.debug("Save")
        ModifyINI.app_config().assign_setting_value(
            "General", "sLogLevel", self.log_level_var.get())
        ModifyINI.app_config().assign_setting_value(
            "General", "iMaxBackups", self.max_backups_var.get())
        ModifyINI.app_config().assign_setting_value(
            "General", "iMaxLogs", self.max_logs_var.get())
        ModifyINI.app_config().assign_setting_value(
            "General", "bAlwaysSelectGame", self.always_select_game_var.get())

        self.destroy()

    def on_cancel(self, event):
        logger.debug("Cancel")
        self.destroy()