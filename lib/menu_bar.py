import sys
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from webbrowser import open_new_tab

if __name__ == "__main__":
    sys.exit(1)

from lib.restore_backup_window import RestoreBackupWindow
from lib.ModifyINI import ModifyINI
from lib.preferences import preferences
from lib.customFunctions import set_theme

class MenuBar(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master.container, *args, **kwargs)
        self.master = master

        # Create the File menu button
        file_menu_button = ttk.Button(self, text="File", command=self.show_file_menu, style="secondary.TButton")
        file_menu_button.pack(side=tk.LEFT, padx=0)

        # Create the Edit menu button
        edit_menu_button = ttk.Button(self, text="Edit", command=self.show_edit_menu, style="secondary.TButton")
        edit_menu_button.pack(side=tk.LEFT, padx=0)

        # Create the Theme menu button
        theme_menu_button = ttk.Button(self, text="Theme", command=self.show_theme_menu, style="secondary.TButton")
        theme_menu_button.pack(side=tk.LEFT, padx=0)

        # Create the Help menu button
        help_menu_button = ttk.Button(self, text="Help", command=self.show_help_menu, style="secondary.TButton")
        help_menu_button.pack(side=tk.LEFT, padx=0)

        # Create the menus
        self.file_menu = tk.Menu(self, tearoff=False)
        self.file_menu.add_command(label="Save", command=master.save_ini_files)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Restore Backup", command=lambda: RestoreBackupWindow(master))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Choose Game", command=lambda: master.choose_game(forced=True))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=master.on_closing)

        self.edit_menu = tk.Menu(self, tearoff=False)
        self.edit_menu.add_command(label="Preferences", command=lambda: preferences(master))
        self.edit_menu.add_command(label="Setup", command=master.show_setup)

        self.theme_menu = tk.Menu(self, tearoff=False)
        theme_names = list(ttk.Style().theme_names())
        for theme_name in theme_names:
            self.theme_menu.add_radiobutton(label=theme_name, variable=master.theme_name,
                                            value=theme_name, command=self.set_theme)

        self.help_menu = tk.Menu(self, tearoff=False)
        self.help_menu.add_command(label="Visit Web Page", command=lambda: open_new_tab("https://www.nexusmods.com/site/mods/631/"))
        self.help_menu.add_command(label="Get Support", command=lambda: open_new_tab("https://stepmodifications.org/forum/forum/200-Bethini-support/"))
        self.help_menu.add_command(label="About", command=master.about)

    def show_file_menu(self) -> None:
        self.file_menu.post(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())

    def show_edit_menu(self) -> None:
        self.edit_menu.post(self.winfo_rootx() + 50, self.winfo_rooty() + self.winfo_height())

    def show_theme_menu(self) -> None:
        self.theme_menu.post(self.winfo_rootx() + 100, self.winfo_rooty() + self.winfo_height())

    def show_help_menu(self) -> None:
        self.help_menu.post(self.winfo_rootx() + 150, self.winfo_rooty() + self.winfo_height())

    def set_theme(self) -> None:
        set_theme(self.master.style_override, self.master.theme_name.get())