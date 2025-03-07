#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import ast
import inspect
import logging
import math
import os
import sys
import tkinter as tk
import webbrowser
from collections.abc import Sequence
from datetime import datetime
from operator import eq, ge, gt, le, lt, ne
from pathlib import Path
from shutil import copyfile
from tkinter import colorchooser, messagebox, simpledialog
from typing import TYPE_CHECKING, Literal, cast

import ttkbootstrap as ttk
from simpleeval import simple_eval  # type: ignore[reportUnknownVariableType]
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Icon
from ttkbootstrap.themes import standard as standThemes
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tableview import Tableview

from lib.app import AppName
from lib.AutoScrollbar import AutoScrollbar
from lib.customFunctions import (
    CustomFunctions,
    browse_to_location,
    decimal_to_rgb,
    hex_to_decimal,
    hex_to_rgb,
    rgb_to_hex,
    rgba_to_hex,
)
from lib.ModifyINI import ModifyINI
from lib.scalar import Scalar
from lib.tooltips import Hovertip
from lib.type_helpers import *

if TYPE_CHECKING:
    from collections.abc import Callable

# from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR, S_IWGRP, S_IWRITE
# This is for changing file read-only access via os.chmod(filename, S_IREAD,
# S_IRGRP, #S_IROTH) Not currently used.

# Configure Logging
LOG_DIR_DATE: str = datetime.now().strftime("%Y %m-%b %d %a - %H.%M.%S")
APP_LOG_DIR = Path.cwd() / "logs" / LOG_DIR_DATE
APP_LOG_DIR.mkdir(parents=True, exist_ok=True)
APP_LOG_FILE = APP_LOG_DIR / "log.log"

fmt = "%(asctime)s  [%(levelname)s]  %(filename)s  %(funcName)s:%(lineno)s:  %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
preferencesWindow: ttk.Toplevel
logging.basicConfig(filename=APP_LOG_FILE, filemode="w", format=fmt, datefmt=datefmt, encoding="utf-8", level=logging.DEBUG)
logger = logging.getLogger()
_log_stdout = logging.StreamHandler(sys.stdout)  # to console
_log_stdout.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
logger.addHandler(_log_stdout)
logger.info(f"Logging to '{APP_LOG_FILE}'")


# This dictionary maps the operator modules to specific text.
operator_dictionary = {
    "greater-than": gt,
    "greater-or-equal-than": ge,
    "less-than": lt,
    "less-or-equal-than": le,
    "not-equal": ne,
    "equal": eq,
}

types_without_label = ["Checkbutton", "preset", "radioPreset", "description"]
types_packed_left = ["Dropdown", "Combobox", "Entry", "Spinbox", "Slider", "Color"]

# Specify the name of the application.
my_app_name = "Bethini Pie"
my_app_short_name = "Bethini"


def set_theme(style_object: ttk.Style, theme_name: str) -> None:
    """Set the application theme."""

    style_object.theme_use(theme_name)
    style_object.configure("choose_game_button.TButton", font=("Segoe UI", 14))
    ModifyINI.app_config().assign_setting_value("General", "sTheme", theme_name)

class log_list_handler(logging.Handler):
    def __init__(self, log_list):
        super().__init__()
        self.log_list = log_list

    def emit(self, record):
        msg = self.format(record)
        self.log_list.append(msg)

class observable_list(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.observers = []

    def append(self, item):
        super().append(item)
        self.notify_observers()

    def extend(self, iterable):
        super().extend(iterable)
        self.notify_observers()

    def insert(self, index, item):
        super().insert(index, item)
        self.notify_observers()

    def notify_observers(self):
        for observer in self.observers:
            observer()

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

class bethini_app(ttk.Window):
    """This is the main app, the glue that creates the GUI."""

    def __init__(self, themename: str) -> None:
        super().__init__(f"{my_app_name} {version}", themename, "Icons/Icon.png", minsize=(400, 200))

        CustomFunctions.screenwidth = self.winfo_screenwidth()
        CustomFunctions.screenheight = self.winfo_screenheight()

        # Variables
        self.tab_dictionary: dict[TabId, DisplayTab] = {}
        self.setting_dictionary: dict[str, BethiniSetting] = {}
        self.dependent_settings_dictionary: dict[str, dict[str, DependentSetting]] = {}
        self.settings_that_settings_depend_on: dict[str, dict[str, DependentSetting]] = {}
        self.tab = []
        self.previous_tab = None

        self.widget_type_function = {
            "Checkbutton": self.checkbox,
            "preset": self.preset,
            "Dropdown": self.dropdown,
            "Entry": self.entry,
            "Spinbox": self.spinbox,
            "Combobox": self.combobox,
            "Color": self.color,
            "Slider": self.slider,
            "radioPreset": self.radio_preset,
        }

        self.widget_type_value = {
            "TkCheckbutton": self.checkbox_value,
            "TkOptionMenu": self.dropdown_value,
            "TkEntry": self.entry_value,
            "TkSpinbox": self.spinbox_value,
            "TkCombobox": self.combobox_value,
            "TkColor": self.color_value,
            "TkSlider": self.slider_value,
            "TkRadioPreset": self.radio_preset_value,
        }

        self.widget_type_assign_value = {
            "TkCheckbutton": self.checkbox_assign_value,
            "TkOptionMenu": self.dropdown_assign_value,
            "TkEntry": self.entry_assign_value,
            "TkSpinbox": self.spinbox_assign_value,
            "TkCombobox": self.combobox_assign_value,
            "TkColor": self.color_assign_value,
            "TkSlider": self.slider_assign_value,
        }

        self.style_override = ttk.Style()

        self.the_canvas = ttk.Canvas(self)
        self.hsbframeholder = ttk.Frame(self)

        self.vsb = AutoScrollbar(self, orient=tk.VERTICAL, command=self.the_canvas.yview)  # type: ignore[reportUnknownArgumentType]
        self.hsb = AutoScrollbar(self.hsbframeholder, orient=tk.HORIZONTAL, command=self.the_canvas.xview)  # type: ignore[reportUnknownArgumentType]
        self.the_canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.container = ttk.Frame(self.the_canvas)
        self.container.bind_all("<Control-s>", self.save_ini_files)

        self.hsbframeholder.pack(side=tk.BOTTOM, fill=tk.X)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.the_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_frame = self.the_canvas.create_window((4, 4), window=self.container, tags="self.container")
        self.container.bind("<Configure>", self.on_frame_configure)
        self.sub_container = ttk.Notebook(self.container)
        self.sub_container.bind("<Configure>", self.sub_container_configure)

        self.statusbar_text = tk.StringVar(self)
        self.statusbar = ttk.Entry(self.hsbframeholder, textvariable=self.statusbar_text)

        self.pw = ttk.Label(self.hsbframeholder, text="Loading... Please Wait... ")
        self.p = ttk.Progressbar(self.hsbframeholder, orient=tk.HORIZONTAL, mode=ttk.INDETERMINATE)
        self.start_progress()
        self.statusbar.pack(anchor=tk.W, side=tk.BOTTOM, fill=tk.X)

        self.choose_game_window = ttk.Toplevel(f"Bethini Pie {version}")

        self.choose_game_frame = ttk.Frame(self.choose_game_window)

        self.choose_game_frame_2 = ttk.Frame(self.choose_game_frame)

        self.label_Bethini = ttk.Label(self.choose_game_frame_2, text="Bethini Pie", font=("Segoe UI", 20))
        self.label_Pie = ttk.Label(
            self.choose_game_frame_2,
            text="Performance INI Editor\nby DoubleYou",
            font=("Segoe UI", 15),
            justify=tk.CENTER,
            style=ttk.WARNING,
        )
        self.label_link = ttk.Label(
            self.choose_game_frame_2,
            text="www.nexusmods.com/site/mods/631",
            font=("Segoe UI", 10),
            cursor="hand2",
            style=ttk.INFO,
        )

        self.choose_game_label = ttk.Label(self.choose_game_frame_2, text="Choose Game", font=("Segoe UI", 15))

        self.choose_game_tree = ttk.Treeview(self.choose_game_frame_2, selectmode=tk.BROWSE, show="tree", columns=("Name"))
        self.choose_game_tree.column("#0", width=0, stretch=tk.NO)
        self.choose_game_tree.column("Name", anchor=tk.W, width=300)

        self.style_override.configure("choose_game_button.TButton", font=("Segoe UI", 14))
        self.choose_game_button = ttk.Button(
            self.choose_game_frame_2,
            text="Select Game",
            style="choose_game_button.TButton",
            command=lambda: self.choose_game_done(self.choose_game_tree.focus()),
        )

        self.choose_game_tip = ttk.Label(
            self.choose_game_frame_2,
            text="Tip: You can change the game at any time\nby going to File > Choose Game.",
            font=("Segoe UI", 12),
            justify=tk.CENTER,
            style="success",
        )
        for option in Path("apps").iterdir():
            self.choose_game_tree.insert("", tk.END, id=option.name, text=option.name, values=[option.name])

        self.preferences_frame = ttk.Frame(self.choose_game_frame_2)

        self.theme_label = ttk.Label(self.preferences_frame, text="Theme:")
        theme_names = standThemes.STANDARD_THEMES.keys()
        self.theme_name = tk.StringVar(self)
        self.theme_dropdown = ttk.OptionMenu(
            self.preferences_frame,
            self.theme_name,
            ModifyINI.app_config().get_value("General", "sTheme", "superhero"),
            *theme_names,
            command=lambda t: set_theme(self.style_override, t.get()),
        )
        self.theme_dropdown.var = self.theme_name  # type: ignore[reportAttributeAccessIssue]

        self.choose_game_frame.pack(fill=tk.BOTH, expand=True)
        self.choose_game_frame_2.pack(anchor=tk.CENTER, expand=True)

        self.label_Bethini.pack(padx=5, pady=5)
        self.label_Pie.pack(padx=5, pady=15)
        self.label_link.pack(padx=25, pady=5)
        self.label_link.bind("<Button-1>", lambda _event: webbrowser.open_new_tab("https://www.nexusmods.com/site/mods/631"))

        self.preferences_frame.pack()
        self.theme_label.pack(side=tk.LEFT)
        self.theme_dropdown.pack(padx=5, pady=15)
        self.choose_game_label.pack(padx=5, pady=2)
        self.choose_game_tree.pack(padx=10)
        self.choose_game_button.pack(pady=15)
        self.choose_game_tip.pack(pady=10)
        self.choose_game_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.choose_game_window.minsize(300, 35)

        self.preset_var = tk.StringVar(self, "Bethini")

    def on_frame_configure(self, _event: "tk.Event[ttk.Frame]") -> None:
        self.the_canvas.configure(scrollregion=self.the_canvas.bbox("all"))

    def sub_container_configure(self, event: "tk.Event[ttk.Notebook]") -> None:
        the_width = event.width + 40
        the_height = event.height + 65
        self.geometry(f"{the_width}x{the_height}")

    def start_progress(self) -> None:
        self.pw.pack(side=tk.LEFT, anchor=tk.S)
        self.p.pack(expand=True, fill=tk.X, anchor=tk.S)
        self.p.start()

    def stop_progress(self) -> None:
        self.pw.destroy()
        self.p.stop()
        self.p.destroy()
        self.pw = ttk.Label(self.hsbframeholder, text="Loading... Please Wait... ")
        self.p = ttk.Progressbar(self.hsbframeholder, orient=tk.HORIZONTAL, mode=ttk.INDETERMINATE)

    def sme(self, message: str, *, exception: Exception | None = None) -> None:
        if exception is not None:
            logger.error(exception, exc_info=True)  # noqa: LOG014
        else:
            logger.debug(message)
        self.statusbar_text.set(message)
        self.update()

    @staticmethod
    def choose_color(button_to_modify: tk.Button, color_value_type: ColorType = "hex") -> ColorValue:
        """This allows us to have our very convenient tkinter colorchooser dialog."""

        # Window modify a button
        new_alpha: int | None = None
        old_color: ColorValue = cast("tk.StringVar", button_to_modify.var).get()  # type: ignore[reportAttributeAccessIssue]
        # old_color is in format (255, 255, 255)

        if color_value_type == "rgb":
            old_color = rgb_to_hex(ast.literal_eval(old_color))

        elif color_value_type == "rgba":
            # (255, 255, 255, 170)
            old_color_original = ast.literal_eval(old_color)
            old_color_hex = rgba_to_hex(old_color_original)
            # ffffffaa
            old_color = old_color_hex[0:7]
            # ffffff
            alpha = old_color_original[3]
            # 170
            try:
                new_alpha = simpledialog.askinteger(
                    "Alpha",
                    "Alpha transparency (0 - 255):",
                    initialvalue=alpha,
                    minvalue=0,
                    maxvalue=255,
                )
                logger.debug(f"New alpha: {new_alpha}")
            except:
                new_alpha = alpha

        elif color_value_type == "rgb 1":
            # "(1.0000, 1.0000, 1.0000)"
            # (255, 255, 255)
            old_color = rgb_to_hex(cast("tuple[int, int, int]", tuple(int(float(i) * 255) for i in ast.literal_eval(old_color))))

        elif color_value_type == "decimal":
            old_color = rgb_to_hex(decimal_to_rgb(old_color))

        response = colorchooser.askcolor(color=old_color)
        new_color = response[1].upper() if response[1] else old_color

        rgb = hex_to_rgb(new_color)
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        the_text_color = "#FFFFFF" if luminance < 128 else "#000000"
        button_to_modify.configure(bg=new_color, activebackground=new_color, fg=the_text_color)
        if TYPE_CHECKING:
            assert isinstance(button_to_modify.var, tk.StringVar)  # type: ignore[reportAttributeAccessIssue]
        if color_value_type == "rgb":
            button_to_modify.var.set(str(hex_to_rgb(new_color)).replace(" ", ""))  # type: ignore[reportAttributeAccessIssue]

        elif color_value_type == "rgba":
            new_color_tuple = hex_to_rgb(new_color)
            new_color_list = list(new_color_tuple)
            if new_alpha is not None:
                new_color_list.append(new_alpha)
            new_color_tuple = tuple(new_color_list)
            button_to_modify.var.set(str(new_color_tuple).replace(" ", ""))  # type: ignore[reportAttributeAccessIssue]

        elif color_value_type == "rgb 1":
            # (255, 255, 255)
            # "(1.0000, 1.0000, 1.0000)"
            the_rgb = str(tuple(round(i / 255, 4) for i in hex_to_rgb(new_color)))
            button_to_modify.var.set(the_rgb)  # type: ignore[reportAttributeAccessIssue]

        elif color_value_type == "decimal":
            button_to_modify.var.set(hex_to_decimal(new_color))  # type: ignore[reportAttributeAccessIssue]

        else:
            button_to_modify.var.set(new_color)  # type: ignore[reportAttributeAccessIssue]
        preferencesWindow.lift()

        return new_color

    def tooltip(
        self,
        tab_id: TabId,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_id: SettingId,
        widget_id: WidgetId,
    ) -> None:
        """Sets the tooltips."""

        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]

        # Fetches the tooltip description.
        tooltip_description = setting.get("tooltip", "No description available.")

        tooltip_wrap_length = setting.get("tooltip_wrap_length", 200)

        # Checks for INI settings specified, and adds them to the bottom of the tooltip if found.
        target_ini_files = setting.get("targetINIs", [])
        if target_ini_files:  # If there are INI settings specified
            target_sections = setting.get("targetSections", [])
            target_settings = setting.get("settings", [])

            # Place INI settings into a dictionary to filter out duplicate target INI files and sections.
            settings_location_dict: dict[str, dict[str, list[str]]] = {}
            for n in range(len(target_ini_files)):
                if target_ini_files[n] not in settings_location_dict:
                    settings_location_dict[target_ini_files[n]] = {}
                if target_sections[n] not in settings_location_dict[target_ini_files[n]]:
                    settings_location_dict[target_ini_files[n]][target_sections[n]] = []
                settings_location_dict[target_ini_files[n]][target_sections[n]].append(target_settings[n])

            # Iterates through the dictionary and makes a formatted string to append to the bottom of the tooltip description.
            tooltip_INI_targets = ""
            for iterator, target_ini in enumerate(settings_location_dict, start=1):
                if iterator > 1:
                    tooltip_INI_targets += "\n"
                tooltip_INI_targets += target_ini

                for target_section in settings_location_dict[target_ini]:
                    tooltip_INI_targets += f"\n[{target_section}]"
                    for target_setting in settings_location_dict[target_ini][target_section]:
                        tooltip_INI_targets += f"\n{target_setting}"
                if iterator != len(settings_location_dict):
                    tooltip_INI_targets += "\n"

            # Appends our formatted string of INI settings to the bottom of the tooltip description.
            tooltip_text = f"{tooltip_description}\n\n{tooltip_INI_targets}"
        else:  # If there are no INI settings specified, only the tooltip description will be used.
            tooltip_text = tooltip_description

        setting_name = setting.get("Name")
        photo_for_setting: Path | None = Path.cwd() / "apps" / GAME_NAME / "images" / f"{setting_name}.jpg"
        if not (photo_for_setting and photo_for_setting.is_file()):
            photo_for_setting = None

        anchor_widget = setting[widget_id]
        if anchor_widget is not None:
            Hovertip(anchor_widget, tooltip_text, PREVIEW_WINDOW, PREVIEW_FRAME, photo_for_setting, tooltip_wrap_length)

    def choose_game(self, *, forced: bool = False) -> None:
        self.withdraw()
        # The Choose App/Game dialog window.  The window is skipped here if
        # sAppName is already set in the Bethini.ini file.
        try:
            choose_game_var = ModifyINI.app_config().get_value("General", "sAppName")
            if forced:
                self.sme("Force choose game/application.")
                raise NameError

            always_select_game = ModifyINI.app_config().get_value("General", "bAlwaysSelectGame")
            if always_select_game is None:
                ModifyINI.app_config().assign_setting_value("General", "bAlwaysSelectGame", "1")

            if always_select_game != "0":
                self.sme("Force choose game/application at startup.")
                # By calling the global variable GAME_NAME before it has been created,
                # we raise an exception to force the app/game to be chosen only at startup.
                GAME_NAME  # type: ignore[reportUnusedExpression] # noqa: B018
            # raise Exception("Forcing you to choose")
            self.choose_game_done(choose_game_var)

        except NameError:
            self.sme("Choose game/application.")
            self.choose_game_window.deiconify()

        except Exception as e:
            self.sme("An unhandled exception occurred.", exception=e)
            messagebox.showerror(
                title="Unhandled exception",
                message=f"An unhandled exception occurred. See log for details.\n{e}\nThis program will now close. No files will be modified.",
            )
            self.quit()
            sys.exit(1)

    def choose_game_done(self, game: str | None, *, from_choose_game_window: bool = False) -> None:
        if not game:
            return

        self.choose_game_window.withdraw()

        # Once the app/game is selected, this loads it.
        if game != ModifyINI.app_config().get_value("General", "sAppName"):
            self.sme(f"App/Game specified in {ModifyINI.app_config_name} differs from the game chosen, so it will be changed to the one you chose.")
            ModifyINI.app_config().assign_setting_value("General", "sAppName", game)
            from_choose_game_window = True

        self.wm_title(f"{my_app_name} {version} - {game}")

        # #############
        # App Globals
        # #############

        global APP
        APP = AppName(self, game)
        global GAME_NAME
        GAME_NAME = APP.data["gameName"]
        self.sme(f"Application/game is {GAME_NAME}")

        # The self.tab_dictionary lists all the tabs, which
        # is variable, based upon the tabs listed in the associated Bethini.json

        for tab in self.tab_dictionary:
            if self.tab_dictionary[tab]["Name"] == "Setup":
                try:
                    self.tab_dictionary[tab]["SetupWindow"].destroy()

                except:
                    tk_frame = self.tab_dictionary[tab].get("TkFrameForTab")
                    if tk_frame:
                        tk_frame.destroy()
            else:
                tk_frame = self.tab_dictionary[tab].get("TkFrameForTab")
                if tk_frame:
                    tk_frame.destroy()
        
        try:
            log_list.remove_observer(self.update_log_text)
            self.log_tab.destroy()
            self.advanced_tab.destroy()
        except AttributeError:
            self.sme("No log tab found. It will be created.")
        except ValueError:
            self.sme("Log List observer not created yet.")

        self.tab_dictionary = {}
        for tab_number, tab in enumerate(APP.bethini["displayTabs"], start=1):
            self.tab_dictionary[f"Page{tab_number}"] = {"Name": tab}

        self.setting_dictionary = {}
        self.dependent_settings_dictionary = {}
        self.settings_that_settings_depend_on = {}
        self.tab = []

        if not from_choose_game_window:
            self.deiconify()
        try:
            self.createTabs(from_choose_game_window=from_choose_game_window)

        except Exception as e:
            self.sme("An unhandled exception occurred.", exception=e)
            messagebox.showerror(
                title="Unhandled exception",
                message=f"An unhandled exception occurred. See log for details.\n{e}\nThis program will now close. No files will be modified.",
            )
            self.quit()
            sys.exit(1)

        self.menu(self.style_override)

    def menu(self, style_object: ttk.Style) -> None:
        menubar = tk.Menu(self)

        # File
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Save", command=self.save_ini_files)
        filemenu.add_separator()
        filemenu.add_command(label="Choose Game", command=lambda: self.choose_game(forced=True))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=lambda: on_closing(self))

        # Edit
        editmenu = tk.Menu(menubar, tearoff=False)
        editmenu.add_command(label="Preferences", command=preferencesWindow.deiconify)
        editmenu.add_command(label="Setup", command=self.show_setup)

        # Theme
        theme_menu = tk.Menu(menubar, tearoff=False)
        theme_names = list(standThemes.STANDARD_THEMES.keys())
        for theme_name in theme_names:
            theme_menu.add_command(label=theme_name, command=lambda t=theme_name: set_theme(style_object, t))

        # Help
        helpmenu = tk.Menu(menubar, tearoff=False)
        helpmenu.add_command(
            label="Visit Web Page",
            command=lambda: webbrowser.open_new_tab("https://www.nexusmods.com/site/mods/631/"),
        )
        helpmenu.add_command(
            label="Get Support",
            command=lambda: webbrowser.open_new_tab("https://stepmodifications.org/forum/forum/200-Bethini-support/"),
        )
        helpmenu.add_command(label="About", command=self.about)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Theme", menu=theme_menu)
        menubar.add_cascade(label="Help", menu=helpmenu)

        ttk.Window.config(self, menu=menubar)

    @staticmethod
    def about() -> None:
        about_window = ttk.Toplevel("About")

        about_frame = ttk.Frame(about_window)
        about_frame_real = ttk.Frame(about_frame)

        about_label = ttk.Label(
            about_frame_real,
            text=f"About {my_app_name} {version}\n\n{my_app_name} was created by DoubleYou.\n\nLicensing is CC BY-NC-SA.",
            justify=tk.CENTER,
        )

        about_frame.pack(fill=tk.BOTH, expand=True)
        about_frame_real.pack(anchor=tk.CENTER, expand=True)
        about_label.pack(anchor=tk.CENTER, padx=10, pady=10)

    def show_setup(self) -> None:
        CustomFunctions.refresh_backups(GAME_NAME, "", None)
        self.withdraw()
        SETUP_WINDOW.deiconify()

    def withdraw_setup(self) -> None:
        SETUP_WINDOW.withdraw()
        self.deiconify()
        self.updateValues()

    def create_first_time_backup(self, ini_location: Path, ini_objects: list[ModifyINI]) -> None:
        backups_path = ini_location / f"{my_app_name} backups"
        first_time_backup_path = backups_path / "First-Time-Backup"
        first_time_backup_path.mkdir(parents=True)
        for ini_file in ini_objects:
            try:
                copyfile(ini_file.ini_path, first_time_backup_path / ini_file.ini_path.name)
            except FileNotFoundError as e:
                self.sme(
                    f"{ini_file.ini_path} does not exist, so it cannot be backed up. This is typically caused by a path not being set correctly.",
                    exception=e,
                )
        copyfile(APP_LOG_FILE, first_time_backup_path / APP_LOG_FILE.name)

    def save_ini_files(self, _event: "tk.Event[tk.Misc] | None" = None) -> None:
        self.remove_invalid_settings()
        try:
            self.apply_ini_dict(APP.preset_values("fixedDefault"), only_if_missing=True)
        except NameError as e:
            self.sme(f"NameError: {e}", exception=e)
            return

        files_to_remove = [*list(ModifyINI.open_inis)[1:], APP_LOG_FILE.name]
        inis_by_location: dict[Path, list[ModifyINI]] = {}
        inis_by_location_modified: dict[Path, list[ModifyINI]] = {}
        locations_without_first_backup: set[Path] = set()

        for each_ini in ModifyINI.open_inis:
            if each_ini == ModifyINI.app_config_name:
                continue

            for ini_path, ini_object in ModifyINI.open_inis[each_ini].items():
                inis_by_location.setdefault(ini_path, []).append(ini_object)
                if ini_object.has_been_modified:
                    inis_by_location_modified.setdefault(ini_path, []).append(ini_object)

                backups_path = ini_path / f"{my_app_name} backups"
                first_time_backup_path = backups_path / "First-Time-Backup"
                if not first_time_backup_path.exists():
                    locations_without_first_backup.add(ini_path)

        if not inis_by_location_modified:
            self.sme("No files were modified. Saving skipped.")
            return

        files_saved = False
        for ini_location, inis in inis_by_location_modified.items():
            backups_path = ini_location / f"{my_app_name} backups"
            for ini_object in inis:
                if messagebox.askyesno(
                    f"Save {ini_object.ini_path.name}?",
                    f"Do you want to save this ini?\n{ini_object.ini_path}?",
                ):
                    remove_excess_directory_files(
                        backups_path,
                        int(cast("str", ModifyINI.app_config().get_value("General", "iMaxBackups", "-1"))),
                        files_to_remove,
                    )
                    if ini_location in locations_without_first_backup:
                        locations_without_first_backup.remove(ini_location)
                        self.create_first_time_backup(ini_location, inis_by_location[ini_location])

                    current_backup_path = backups_path / LOG_DIR_DATE
                    current_backup_path.mkdir(parents=True, exist_ok=True)
                    current_backup_file_path = current_backup_path / ini_object.ini_path.name
                    if current_backup_file_path.exists():
                        self.sme(f"{current_backup_file_path} already exists, so it will not be overwritten.")
                    else:
                        try:
                            copyfile(ini_object.ini_path, current_backup_file_path)
                        except FileNotFoundError as e:
                            self.sme(
                                f"{ini_object.ini_path} does not exist, so it cannot be backed up. This is typically caused by a path not being set correctly.",
                                exception=e,
                            )
                    ini_object.save_ini_file(sort=True)
                    files_saved = True
                    self.sme(f"{ini_object.ini_path} saved.")
                    copyfile(APP_LOG_FILE, current_backup_path / APP_LOG_FILE.name)

        if not files_saved:
            self.sme("No files were modified. Saving skipped.")

    def set_preset(self, preset_id: str) -> None:
        self.start_progress()
        if preset_id == "Default":
            self.apply_ini_dict(APP.preset_values("default"))
            self.remove_ini_dict(APP.can_remove())
            self.apply_ini_dict(APP.preset_values("fixedDefault"))
            preset_var = ""
        elif preset_id == "recommended":
            preset_dict = APP.preset_values(preset_id)
            self.apply_ini_dict(preset_dict)
            preset_var = ""
        else:
            preset_var = self.preset_var.get()
            preset_dict = APP.preset_values(f"{preset_var} {preset_id}")
            self.apply_ini_dict(preset_dict)
        self.stop_progress()
        self.updateValues()
        self.sme(f"Preset {preset_var} {preset_id} applied.")

    def remove_invalid_settings(self) -> None:
        for each_ini in ModifyINI.open_inis:
            if each_ini == ModifyINI.app_config_name or not APP.get_ini_setting_name(each_ini):
                continue

            for ini_object in ModifyINI.open_inis[each_ini].values():
                sections = ini_object.get_sections()

                for section in sections:
                    settings = ini_object.get_settings(section)
                    if not settings:
                        ini_object.remove_section(section)
                        self.sme(f"{section} was removed because it was empty.")
                        continue

                    for setting_name in settings:
                        if ";" in setting_name or "#" in setting_name:
                            self.sme(f"{setting_name}:{section} will be preserved, as it is a comment.")

                        elif not APP.does_setting_exist(each_ini, section, setting_name):
                            # Removal of unknown settings (disabled)
                            # ini_object.remove_setting(section, setting_name)

                            self.sme(f"{setting_name}:{section} {each_ini} appears to be invalid.")
                            if not ini_object.get_settings(section):
                                ini_object.remove_section(section)
                                self.sme(f"{section} was removed because it was empty.")

    def apply_ini_dict(self, ini_dict: dict[str, GameSetting], *, only_if_missing: bool = False) -> None:
        for setting_and_section in ini_dict:
            # Settings are in the format `setting:section`
            # e.g. sAntiAliasing:Display

            target_setting = setting_and_section.split(":")[0]
            if not only_if_missing and target_setting in APP.bethini["presetsIgnoreTheseSettings"]:
                continue

            target_ini = ini_dict[setting_and_section]["ini"]
            target_section = ini_dict[setting_and_section]["section"]
            this_value = str(ini_dict[setting_and_section]["value"])

            if target_ini is None:
                msg = f"{setting_and_section} has no INI set."
                raise TypeError(msg)

            ini_location = bethini_app.getINILocation(target_ini)
            target_ini_object = ModifyINI.open(target_ini, Path(ini_location))

            # Check if we are only supposed to add the value if the value is missing
            if only_if_missing and (target_ini_object.get_value(target_section, target_setting) is not None):
                continue

            target_ini_object.assign_setting_value(target_section, target_setting, this_value)
            self.sme(f"{target_ini} [{target_section}] {target_setting}={this_value}")

    def remove_ini_dict(self, ini_dict: dict[str, GameSetting]) -> None:
        for setting_and_section in ini_dict:
            target_setting = setting_and_section.split(":")[0]
            target_ini = ini_dict[setting_and_section]["ini"]
            target_section = ini_dict[setting_and_section]["section"]
            this_value = str(ini_dict[setting_and_section]["value"])

            if target_ini is None:
                msg = f"{setting_and_section} has no INI set."
                raise TypeError(msg)

            ini_location = bethini_app.getINILocation(target_ini)
            target_ini_object = ModifyINI.open(target_ini, Path(ini_location))
            current_value = cast("str", target_ini_object.get_value(target_section, target_setting, this_value))

            if current_value == this_value:
                if target_ini_object.remove_setting(target_section, target_setting):
                    self.sme(
                        f"{target_ini} [{target_section}] {target_setting}={this_value}, which is the default value, and since it is not set to alwaysPrint, it will be removed",
                    )
                else:
                    self.sme(f"No section {target_section} exists for {target_setting} in {target_ini_object}.")

    def create_tab_image(self, tab_id: TabId) -> None:
        icon_path = Path.cwd() / "icons" / f"{self.tab_dictionary[tab_id]['Name']}.png"
        try:
            if not icon_path.is_file():
                icon_path = icon_path.with_name("Blank.png")
                if not icon_path.is_file():
                    self.sme(f"No icon for tab '{tab_id}'")
                    tab_icon = tk.PhotoImage(data=Icon.warning)
                    return

            tab_icon = tk.PhotoImage(file=icon_path, height=16, width=16)

        except tk.TclError as e:
            self.sme(f"Failed to load icon for tab '{tab_id}':\n{icon_path}", exception=e)
            tab_icon = tk.PhotoImage(data=Icon.warning)

        self.tab_dictionary[tab_id]["TkPhotoImageForTab"] = tab_icon

    def label_frames_for_tab(self, tab_id: TabId) -> None:
        the_dict = self.tab_dictionary[tab_id]
        the_dict["LabelFrames"] = {}
        for label_frame_number, frame_name in enumerate(APP.bethini["displayTabs"][the_dict["Name"]], start=1):
            label_frame_id = f"LabelFrame{label_frame_number}"
            the_dict["LabelFrames"][label_frame_id] = {"Name": frame_name}
            if frame_name != "NoLabelFrame":
                the_dict["LabelFrames"][label_frame_id]["TkLabelFrame"] = ttk.Labelframe(
                    the_dict["TkFrameForTab"],
                    text=frame_name,
                    width=200,
                )
            else:
                the_dict["LabelFrames"][label_frame_id]["TkLabelFrame"] = ttk.Frame(the_dict["TkFrameForTab"])

            pack_settings = APP.pack_settings(self.tab_dictionary[tab_id]["Name"], frame_name)

            the_dict["LabelFrames"][label_frame_id]["TkLabelFrame"].pack(
                anchor=pack_settings.get("Anchor", tk.NW),
                side=pack_settings.get("Side", tk.TOP),
                fill=pack_settings.get("Fill", tk.BOTH),
                expand=pack_settings.get("Expand", 1),
                padx=10,
                pady=10,
            )
            self.settings_frames_for_label_frame(tab_id, frame_name, label_frame_id)

    def settings_frames_for_label_frame(self, tab_id: TabId, label_frame_name: str, label_frame_id: LabelFrameId) -> None:
        setting_frames: dict[str, dict[str, BethiniSetting]] = {}
        self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"] = setting_frames
        number_of_vertically_stacked_settings = int(
            APP.number_of_vertically_stacked_settings(self.tab_dictionary[tab_id]["Name"], label_frame_name),
        )

        for setting_number, setting_name in enumerate(
            cast(
                "dict[str, BethiniSetting]",
                APP.bethini["displayTabs"][self.tab_dictionary[tab_id]["Name"]][label_frame_name]["Settings"],
            ),
            start=1,
        ):
            setting_frame_id = f"SettingFrame{math.ceil(setting_number / number_of_vertically_stacked_settings) - 1}"
            if setting_frame_id not in setting_frames:
                setting_frames[setting_frame_id] = {}
                setting_frame = ttk.Frame(
                    self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["TkLabelFrame"],
                )
                setting_frames[setting_frame_id]["TkSettingFrame"] = setting_frame  # type: ignore[reportArgumentType]
                setting_frame.pack(side=tk.LEFT, anchor=tk.NW)
            setting_id = f"Setting{setting_number}"
            setting: BethiniSetting = {"Name": setting_name}
            setting_frames[setting_frame_id][setting_id] = setting
            setting["TkFinalSettingFrame"] = ttk.Frame(
                cast("ttk.Frame", setting_frames[setting_frame_id]["TkSettingFrame"]),
            )
            setting["TkFinalSettingFrame"].pack(anchor=tk.W, padx=5, pady=2)
            if setting_name != "Placeholder":
                setting.update(
                    cast(
                        "BethiniSetting",
                        APP.bethini["displayTabs"][self.tab_dictionary[tab_id]["Name"]][label_frame_name]["Settings"][setting_name],
                    ),
                )
                self.setting_label(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id)

    def setting_label(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]
        setting_type = setting.get("type")
        if setting_type not in types_without_label:
            setting_label = setting_name if setting_type else ""
            setting_label_width = setting.get("customWidth")
            setting["TkLabel"] = ttk.Label(
                setting["TkFinalSettingFrame"],
                text=setting_label,
                width=int(setting_label_width) if setting_label_width else "",
                anchor=tk.E,
            )
            if setting_type in types_packed_left:
                setting["TkLabel"].pack(anchor=tk.CENTER, side=tk.LEFT, padx=5, pady=5)
            else:
                setting["TkLabel"].pack(anchor=tk.CENTER, padx=5, pady=5)
        setting_description = setting.get("Description")
        if setting_description:
            setting["TkDescriptionLabel"] = ttk.Label(
                setting["TkFinalSettingFrame"],
                text=setting_description,
                justify=tk.LEFT,
                wraplength=900,
            )
            setting["TkDescriptionLabel"].pack(anchor=tk.N)
        self.setting_type_switcher(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, setting_type)

    def setting_type_switcher(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
        setting_type: str | None,
    ) -> None:
        func = self.widget_type_function.get(setting_type) if setting_type else None

        if func is not None:
            func(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id)

    def widget_type_switcher(self, setting_name: str) -> ValueList | str | None:
        setting: BethiniSetting = self.setting_dictionary[setting_name]
        func = self.widget_type_value.get(setting["widget_id"])

        if inspect.isroutine(func):
            return func(setting_name)
        return None

    def add_to_setting_dictionary(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
        widget_id: WidgetId,
    ) -> None:
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]
        tk_widget = setting[widget_id]
        if TYPE_CHECKING:
            assert tk_widget is not None
        self.setting_dictionary[setting_name] = {
            "tab_id": tab_id,
            "label_frame_name": label_frame_name,
            "setting_frame_id": setting_frame_id,
            "setting_id": setting_id,
            "widget_id": widget_id,
            "tk_widget": tk_widget,
            "targetINIs": setting.get("targetINIs", []),
            "settings": setting.get("settings", []),
            "targetSections": setting.get("targetSections", []),
        }

        dependent_settings = setting.get("dependentSettings")
        if dependent_settings:
            self.dependent_settings_dictionary[setting_name] = dependent_settings

    def checkbox(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        """Create a ttk.Checkbutton."""

        widget_id = "TkCheckbutton"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]
        setting["tk_var"] = tk.StringVar(self)
        on_value = setting["Onvalue"]
        off_value = setting["Offvalue"]
        setting[widget_id] = ttk.Checkbutton(
            setting["TkFinalSettingFrame"],
            text=setting_name,
            variable=setting["tk_var"],
            onvalue=on_value,
            offvalue=off_value,
        )
        setting[widget_id].var = setting["tk_var"]  # type: ignore[reportAttributeAccessIssue]
        setting[widget_id].pack(anchor=tk.W, padx=5, pady=7)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)
        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({
            "tk_var": setting["tk_var"],
            "Onvalue": on_value,
            "Offvalue": off_value,
        })

    def preset(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        """Create a Preset ttk.Button."""

        widget_id = "TkPresetButton"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]
        preset_id = setting["preset id"]
        setting[widget_id] = ttk.Button(setting["TkFinalSettingFrame"], text=setting_name, command=lambda: self.set_preset(preset_id))
        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=0)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)
        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)

    def radio_preset(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        """Create a Preset Radiobutton."""

        widget_id = "TkRadioPreset"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]
        value = setting.get("value")
        setting[widget_id] = ttk.Radiobutton(setting["TkFinalSettingFrame"], text=setting_name, variable=self.preset_var, value=value)
        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=7)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)
        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({"tk_var": self.preset_var})

    def dropdown(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        """Create a ttk.OptionMenu."""

        widget_id = "TkOptionMenu"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]
        choices = setting.get("choices", [])

        # Custom functions allow us to auto-detect certain
        # predefined options that can then easily be selected.

        if isinstance(choices, str):
            if "FUNC" in choices:
                option_string = APP.bethini["customFunctions"][choices]
                if "{}" in option_string:
                    custom_function_name = APP.bethini["customFunctions"][f"{choices}Format"]
                    custom_function = cast("Callable[[str], list[str]]", getattr(CustomFunctions, custom_function_name))
                    choices = custom_function(GAME_NAME)
        else:
            for n in range(len(choices)):
                if "FUNC" in choices[n]:
                    option_string = APP.bethini["customFunctions"][choices[n]]
                    if "{}" in option_string:
                        custom_function_name = APP.bethini["customFunctions"][f"{choices[n]}Format"]
                        value_to_insert = getattr(CustomFunctions, custom_function_name)(GAME_NAME)
                        choices[n] = option_string.format(value_to_insert)

        tk_var = setting["tk_var"] = tk.StringVar(self)
        browse = setting.get("browse", ("directory", "directory", "directory"))
        func_name = setting.get("custom_function", "")

        def browse_to_loc(
            choice: str,
            var: tk.StringVar = tk_var,
            browse: BrowseSettings = browse,
            func_name: str = func_name,
        ) -> None:
            location = browse_to_location(choice, browse)
            if location:
                var.set(location)
            elif choices[0] not in {"Browse...", "Manual...", "Choose...", "None found"}:
                var.set(choices[0])
            else:
                var.set("")

            if func_name:
                custom_function = cast("Callable[[str, str, str | None], str | None]", getattr(CustomFunctions, func_name))
                second_return_value = custom_function(GAME_NAME, choice, location)
                logger.debug(f"Return value of {func_name}: {second_return_value}")

        setting[widget_id] = ttk.OptionMenu(
            setting["TkFinalSettingFrame"],
            tk_var,
            choices[0],
            *choices,
            command=lambda c: browse_to_loc(cast("str", c)),
        )
        setting[widget_id].var = tk_var  # type: ignore[reportAttributeAccessIssue]
        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)

        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({
            "tk_var": tk_var,
            "choices": choices,
            "settingChoices": setting.get("settingChoices"),
            "delimiter": setting.get("delimiter"),
            "decimal places": setting.get("decimal places"),
            "fileFormat": setting.get("fileFormat"),
            "forceSelect": setting.get("forceSelect"),
            "partial": setting.get("partial"),
        })

    def combobox(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        """Create a ttk.Combobox."""
        widget_id = "TkCombobox"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]

        choices = cast("list[str]", setting.get("choices", []))
        width = int(setting.get("width") or 20)
        validate = setting.get("validate")

        setting["tk_var"] = tk.StringVar(self)

        if validate:
            setting["validate"] = self.register(self.validate)
            setting[widget_id] = ttk.Combobox(
                setting["TkFinalSettingFrame"],
                textvariable=setting["tk_var"],
                width=width,
                values=choices,
                validate="key",
                validatecommand=(setting["validate"], "%P", "%s", validate),
            )
        else:
            setting[widget_id] = ttk.Combobox(
                setting["TkFinalSettingFrame"],
                textvariable=setting["tk_var"],
                width=width,
                values=choices,
            )

        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)
        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({
            "tk_var": setting["tk_var"],
            "choices": choices,
            "decimal places": setting.get("decimal places"),
        })

    def entry(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        """Create a ttk.Entry."""
        widget_id = "TkEntry"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]

        entry_width = int(setting.get("entry_width") or 20)
        validate = setting.get("validate")

        setting["tk_var"] = tk.StringVar(self)

        if validate:
            setting["validate"] = self.register(self.validate)
            setting[widget_id] = ttk.Entry(
                setting["TkFinalSettingFrame"],
                width=entry_width,
                validate="key",
                validatecommand=(setting["validate"], "%P", "%s", validate),
                textvariable=setting["tk_var"],
            )
        else:
            setting[widget_id] = ttk.Entry(setting["TkFinalSettingFrame"], width=entry_width, textvariable=setting["tk_var"])

        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)

        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({
            "tk_var": setting["tk_var"],
            "formula": setting.get("formula"),
            "decimal places": setting.get("decimal places"),
            "partial": setting.get("partial"),
            "fileFormat": setting.get("fileFormat"),
        })

    def slider(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        widget_id = "TkSlider"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]

        from_value = float(setting["from"])
        to_value = float(setting["to"])
        decimal_places = setting["decimal places"] or "0"
        increment = float(setting.get("increment", 0))
        width = int(setting["width"])
        length = int(setting["length"])
        validate = setting["validate"]

        setting["tk_var"] = tk.StringVar(self)

        setting[widget_id] = Scalar(
            setting["TkFinalSettingFrame"],
            from_=from_value,
            to=to_value,
            orient=tk.HORIZONTAL,
            length=length,
            decimal_places=decimal_places,
            variable=setting["tk_var"],  # type: ignore[reportArgumentType]
        )

        reversed_ = setting.get("reversed")
        if reversed_:
            from_value = float(setting["to"])
            to_value = float(setting["from"])

        second_tk_widget: ttk.Spinbox | None = None
        if validate:
            setting["validate"] = self.register(self.validate)
            second_tk_widget = ttk.Spinbox(
                setting["TkFinalSettingFrame"],
                width=width,
                validate="key",
                increment=increment,
                from_=from_value,
                to=to_value,
                validatecommand=(setting["validate"], "%P", "%s", validate),
                textvariable=setting["tk_var"],
            )
        else:
            second_tk_widget = ttk.Spinbox(
                setting["TkFinalSettingFrame"],
                width=width,
                increment=increment,
                from_=from_value,
                to=to_value,
                textvariable=setting["tk_var"],
            )
        setting["second_tk_widget"] = second_tk_widget

        second_tk_widget.pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)

        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, "second_tk_widget")
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)

        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({
            "tk_var": setting["tk_var"],
            "decimal places": setting.get("decimal places"),
            "second_tk_widget": setting["second_tk_widget"],
        })

    def spinbox(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        widget_id = "TkSpinbox"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]

        from_value = float(setting["from"])
        to_value = float(setting["to"])
        increment = float(setting.get("increment", 0))
        width = int(setting["width"])
        validate = setting.get("validate")

        setting["tk_var"] = tk.StringVar(self)

        if validate:
            setting["validate"] = self.register(self.validate)
            setting[widget_id] = ttk.Spinbox(
                setting["TkFinalSettingFrame"],
                from_=from_value,
                to=to_value,
                increment=increment,
                width=width,
                validate="key",
                validatecommand=(setting["validate"], "%P", "%s", validate),
                textvariable=setting["tk_var"],
            )
        else:
            setting[widget_id] = ttk.Spinbox(
                setting["TkFinalSettingFrame"],
                from_=from_value,
                to=to_value,
                increment=increment,
                width=width,
                textvariable=setting["tk_var"],
            )

        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)

        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({
            "tk_var": setting["tk_var"],
        })

    def color(
        self,
        tab_id: TabId,
        label_frame_name: str,
        label_frame_id: LabelFrameId,
        setting_frame_id: SettingFrameId,
        setting_name: str,
        setting_id: SettingId,
    ) -> None:
        widget_id = "TkColor"
        setting: BethiniSetting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][setting_frame_id][setting_id]

        color_value_type = setting.get("colorValueType")

        setting["tk_var"] = tk.StringVar(self)
        if color_value_type == "hex":
            setting["tk_var"].set("#FFFFFF")
        elif color_value_type == "rgb":
            setting["tk_var"].set("(255, 255, 255)")
        elif color_value_type == "rgba":
            setting["tk_var"].set("(255, 255, 255, 255)")
        elif color_value_type == "rgb 1":
            setting["tk_var"].set("(1.0000, 1.0000, 1.0000)")
        elif color_value_type == "decimal":
            setting["tk_var"].set("16777215")
        else:
            msg = "Unknown color value type."
            raise ValueError(msg)

        setting[widget_id] = tk.Button(
            setting["TkFinalSettingFrame"],
            textvariable=setting["tk_var"],
            command=lambda: self.choose_color(setting[widget_id], color_value_type),
        )
        setting[widget_id].var = setting["tk_var"]  # type: ignore[reportAttributeAccessIssue]
        setting[widget_id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(tab_id, label_frame_id, setting_frame_id, setting_id, widget_id)

        self.add_to_setting_dictionary(tab_id, label_frame_name, label_frame_id, setting_frame_id, setting_name, setting_id, widget_id)
        self.setting_dictionary[setting_name].update({
            "tk_var": setting["tk_var"],
            "colorValueType": color_value_type,
            "rgbType": setting.get("rgbType"),
        })

    def radio_preset_value(self, _setting_name: str) -> str:
        return self.preset_var.get()

    def checkbox_value(self, setting_name: str) -> ValueList | None:
        setting_value = self.get_setting_values(
            self.setting_dictionary[setting_name].get("targetINIs", []),
            self.setting_dictionary[setting_name].get("targetSections", []),
            self.setting_dictionary[setting_name].get("settings", []),
        )

        if setting_value and None not in setting_value:
            tk_var = self.setting_dictionary[setting_name]["tk_var"]
            on_value = self.setting_dictionary[setting_name]["Onvalue"]
            off_value = self.setting_dictionary[setting_name]["Offvalue"]

            if setting_value == on_value:
                this_value = on_value
            elif setting_value == off_value:
                this_value = off_value
            else:
                this_value = on_value if all(v in on_value[i] for i, v in enumerate(setting_value)) else off_value
            tk_var.set(this_value)  # type: ignore[reportArgumentType]

            try:
                logger.debug(f"{setting_name} = {this_value}")
                self.setting_dictionary[setting_name]["valueSet"] = True
            except:
                logger.warning(f"No value set for checkbox {setting_name}.")
            else:
                return this_value
        return None

    def dropdown_value(self, setting_name: str) -> int | float | str | tuple[str, str] | None:
        setting_value = self.get_setting_values(
            self.setting_dictionary[setting_name].get("targetINIs", []),
            self.setting_dictionary[setting_name].get("targetSections", []),
            self.setting_dictionary[setting_name].get("settings", []),
            self.setting_dictionary[setting_name].get("settingChoices"),
            self.setting_dictionary[setting_name].get("delimiter"),
        )

        if setting_value and None not in setting_value:
            setting_value = cast("list[str]", setting_value)
            decimal_places_str = self.setting_dictionary[setting_name].get("decimal places")
            if decimal_places_str:
                decimal_places = int(decimal_places_str)
                this_value = round(float(setting_value[0]), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)
                self.setting_dictionary[setting_name]["tk_var"].set(this_value)  # type: ignore[reportArgumentType]
            else:
                file_format = self.setting_dictionary[setting_name].get("fileFormat")
                if file_format:
                    this_value = os.path.split(setting_value[0])  # type: ignore[assignment]
                    if file_format == "directory":
                        this_value = this_value[0]
                        if this_value and this_value[-1] != "\\":
                            this_value += "\\"
                    elif file_format == "file":
                        this_value = this_value[1]
                    self.setting_dictionary[setting_name]["tk_var"].set(this_value)  # type: ignore[reportArgumentType]
                else:
                    setting_choices = self.setting_dictionary[setting_name].get("settingChoices")
                    if setting_choices and setting_value[0] not in setting_choices:
                        this_value = "Custom"  # type: ignore[assignment]
                        self.setting_dictionary[setting_name]["tk_var"].set(this_value)  # type: ignore[reportArgumentType]
                    else:
                        this_value = setting_value[0]  # type: ignore[assignment]
                        self.setting_dictionary[setting_name]["tk_var"].set(this_value)  # type: ignore[reportArgumentType]
            logger.debug(f"{setting_name} = {this_value}")
            self.setting_dictionary[setting_name]["valueSet"] = True
            return this_value
        return None

    def combobox_value(self, setting_name: str) -> str | None:
        setting_value = self.get_setting_values(
            self.setting_dictionary[setting_name].get("targetINIs", []),
            self.setting_dictionary[setting_name].get("targetSections", []),
            self.setting_dictionary[setting_name].get("settings", []),
        )
        if setting_value and None not in setting_value:
            setting_value = cast("list[str]", setting_value)

            str_value = setting_value[0]

            decimal_places_str = self.setting_dictionary[setting_name].get("decimal places")
            if decimal_places_str:
                decimal_places = int(decimal_places_str)
                float_value = round(float(str_value), decimal_places)
                str_value = str(int(float_value)) if decimal_places == 0 else str(float_value)

            self.setting_dictionary[setting_name]["tk_var"].set(str_value)  # type: ignore[reportArgumentType]
            logger.debug(f"{setting_name} = {str_value}")
            self.setting_dictionary[setting_name]["valueSet"] = True
            return str_value
        return None

    def entry_value(self, setting_name: str) -> int | float | str | None:
        setting_value = self.get_setting_values(
            self.setting_dictionary[setting_name].get("targetINIs", []),
            self.setting_dictionary[setting_name].get("targetSections", []),
            self.setting_dictionary[setting_name].get("settings", []),
        )
        if setting_value and None not in setting_value:
            setting_value = cast("list[str]", setting_value)

            formula = self.setting_dictionary[setting_name].get("formula")
            file_format = self.setting_dictionary[setting_name].get("fileFormat")
            this_value: float | str
            if formula:
                this_value = cast("float", simple_eval(formula.format(setting_value[0])))
                decimal_places_str = self.setting_dictionary[setting_name].get("decimal places")
                if decimal_places_str:
                    decimal_places = int(decimal_places_str)
                    this_value = round(this_value, decimal_places)  # type: ignore[reportArgumentType]
                    if decimal_places == 0:
                        this_value = int(this_value)
            else:
                this_value = setting_value[0]
                if file_format and file_format == "file":
                    this_value = os.path.split(this_value)[1]

            try:
                self.setting_dictionary[setting_name]["tk_var"].set(this_value)  # type: ignore[reportArgumentType]
                logger.debug(f"{setting_name} = {this_value}")
                self.setting_dictionary[setting_name]["valueSet"] = True
            except:
                logger.warning(f"No value set for entry {setting_name}.")
            else:
                return this_value
        return None

    def slider_value(self, setting_name: str) -> str | None:
        setting_value = self.get_setting_values(
            self.setting_dictionary[setting_name].get("targetINIs", []),
            self.setting_dictionary[setting_name].get("targetSections", []),
            self.setting_dictionary[setting_name].get("settings", []),
        )

        if setting_value and None not in setting_value:
            setting_value = cast("list[str]", setting_value)

            str_value = setting_value[0]
            decimal_places_str = self.setting_dictionary[setting_name].get("decimal places")
            if decimal_places_str:
                decimal_places = int(decimal_places_str)
                float_value = round(float(str_value), decimal_places)
                str_value = str(int(float_value)) if decimal_places == 0 else str(float_value)

            try:
                self.setting_dictionary[setting_name]["tk_var"].set(str_value)  # type: ignore[reportArgumentType]
                logger.debug(f"{setting_name} = {str_value}")
                self.setting_dictionary[setting_name]["valueSet"] = True
            except:
                logger.warning(f"no value set for slider {setting_name}")
            else:
                return str_value
        return None

    def spinbox_value(self, setting_name: str) -> str | None:
        setting_value = self.get_setting_values(
            self.setting_dictionary[setting_name].get("targetINIs", []),
            self.setting_dictionary[setting_name].get("targetSections", []),
            self.setting_dictionary[setting_name].get("settings", []),
        )
        if setting_value and None not in setting_value:
            setting_value = cast("list[str]", setting_value)

            this_value = setting_value[0]
            try:
                self.setting_dictionary[setting_name]["tk_var"].set(this_value)  # type: ignore[reportArgumentType]
                logger.debug(f"{setting_name} = {this_value}")
                self.setting_dictionary[setting_name]["valueSet"] = True
            except:
                logger.warning(f"no value set for spinbox {setting_name}")
            else:
                return this_value
        return None

    def color_value(self, setting_name: str) -> str | None:
        setting_value = self.get_setting_values(
            self.setting_dictionary[setting_name].get("targetINIs", []),
            self.setting_dictionary[setting_name].get("targetSections", []),
            self.setting_dictionary[setting_name].get("settings", []),
        )

        if setting_value and None not in setting_value:
            setting_value = cast("list[str]", setting_value)

            this_value = None
            new_color = None
            color_value_type = self.setting_dictionary[setting_name].get("colorValueType")
            if color_value_type == "hex":
                this_value = setting_value[0]
                new_color = this_value
            elif color_value_type == "decimal":
                this_value = setting_value[0]
                new_color = rgb_to_hex(decimal_to_rgb(setting_value[0]))
            elif color_value_type == "rgb":
                rgb_type = self.setting_dictionary[setting_name].get("rgbType")
                if rgb_type == "multiple settings":
                    this_value_as_tuple = tuple(int(i) for i in setting_value)
                    new_color = rgb_to_hex(cast("tuple[int, int, int]", this_value_as_tuple))
                    this_value = str(this_value_as_tuple)
                else:
                    this_value = "("
                    for n in range(len(setting_value)):
                        this_value += setting_value[n]
                    this_value += ")"
                    new_color = rgb_to_hex(ast.literal_eval(this_value))
            elif color_value_type == "rgba":
                rgb_type = self.setting_dictionary[setting_name].get("rgbType")
                if rgb_type == "multiple settings":
                    this_value_as_tuple = tuple(int(i) for i in setting_value)
                    new_color = rgb_to_hex(cast("tuple[int, int, int]", this_value_as_tuple[:3]))
                    this_value = str(this_value_as_tuple)
                else:
                    this_value = "("
                    for n in range(len(setting_value)):
                        this_value += setting_value[n]
                    this_value += ")"
                    new_color = rgb_to_hex(ast.literal_eval(this_value)[0:3])
            elif color_value_type == "rgb 1":
                rgb_type = self.setting_dictionary[setting_name].get("rgbType")
                if rgb_type == "multiple settings":
                    this_value_as_tuple = tuple(round(float(i), 4) for i in setting_value)
                    new_color = rgb_to_hex(cast("tuple[int, int, int]", tuple(int(float(i) * 255) for i in setting_value)))
                    this_value = str(this_value_as_tuple)

            if this_value is not None and new_color is not None:
                self.setting_dictionary[setting_name]["tk_var"].set(this_value)
                tk_widget = cast("tk.Button", self.setting_dictionary[setting_name]["tk_widget"])
                rgb = hex_to_rgb(new_color)
                luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
                the_text_color = "#FFFFFF" if luminance < 128 else "#000000"
                tk_widget.configure(bg=new_color, activebackground=new_color, fg=the_text_color)
                logger.debug(f"{setting_name} = {this_value}")
                self.setting_dictionary[setting_name]["valueSet"] = True
                return this_value
        return None

    def check_dependents(self, setting_name: str) -> None:
        for dependent_setting_name in self.settings_that_settings_depend_on[setting_name]:
            var = self.settings_that_settings_depend_on[setting_name][dependent_setting_name].get("var")

            operator_func = self.settings_that_settings_depend_on[setting_name][dependent_setting_name].get("operator_func")
            value = self.settings_that_settings_depend_on[setting_name][dependent_setting_name].get("value")
            current_value = self.widget_type_switcher(setting_name)
            second_tk_widget = self.setting_dictionary[dependent_setting_name].get("second_tk_widget")
            if var == "float":
                value = float(cast("str", value))
                current_value = float(current_value)  # type: ignore[assignment]
            if inspect.isroutine(operator_func) and operator_func(current_value, value):
                self.setting_dictionary[dependent_setting_name]["tk_widget"].configure(state=tk.NORMAL)
                if second_tk_widget:
                    second_tk_widget.configure(state=tk.NORMAL)
            else:
                set_to_off = self.settings_that_settings_depend_on[setting_name][dependent_setting_name].get("setToOff")
                if set_to_off:
                    off_value = self.setting_dictionary[dependent_setting_name].get("Offvalue")

                    self.setting_dictionary[dependent_setting_name]["tk_var"].set(off_value)  # type: ignore[reportArgumentType]
                self.setting_dictionary[dependent_setting_name]["tk_widget"].configure(state=tk.DISABLED)
                if second_tk_widget:
                    second_tk_widget.configure(state=tk.DISABLED)

    def assign_value(self, setting_name: str) -> None:
        widget_id = self.setting_dictionary[setting_name]["widget_id"]
        func = self.widget_type_assign_value.get(widget_id)
        if func is not None:
            func(setting_name)

        if setting_name in list(self.settings_that_settings_depend_on.keys()):
            self.check_dependents(setting_name)

    def checkbox_assign_value(self, setting_name: str) -> None:
        setting = self.setting_dictionary[setting_name]
        this_value = setting["tk_var"].get()
        if setting_name == "Always Select Game":
            pass

        # this_value is whatever the state of the on_value/off_value is... not a simple boolean

        targetINIs = self.setting_dictionary[setting_name].get("targetINIs", [])
        targetSections = self.setting_dictionary[setting_name].get("targetSections", [])
        theSettings = self.setting_dictionary[setting_name].get("settings", [])

        on_value = self.setting_dictionary[setting_name]["Onvalue"]
        off_value = self.setting_dictionary[setting_name]["Offvalue"]
        setting_value = self.get_setting_values(targetINIs, targetSections, theSettings)

        try:
            this_value = list(ast.literal_eval(this_value))  # type: ignore[assignment]
            for n in range(len(this_value)):
                if isinstance(this_value[n], tuple):
                    this_value[n] = list(this_value[n])
        except Exception as e:
            self.sme(
                f"{this_value} .... Make sure that the {setting_name} checkbutton Onvalue and Offvalue are lists within lists in the json.",
                exception=e,
            )

        if not targetINIs:
            return

        for n in range(len(targetINIs)):
            ini_location = self.getINILocation(targetINIs[n])
            the_target_ini = ModifyINI.open(targetINIs[n], Path(ini_location))

            if this_value not in (on_value, off_value):
                continue
            setting_value = cast("list[str]", setting_value)

            if isinstance(this_value[n], list):  # type: ignore[reportUnnecessaryIsInstance]
                if setting_value[n] in this_value[n]:
                    theValue = setting_value[n]
                elif this_value[n][0] in self.setting_dictionary:
                    self.assign_value(this_value[n][0])
                    continue

                else:
                    theValue = this_value[n][0]
                    try:
                        the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                        self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}")
                    except AttributeError as e:
                        self.sme(
                            f"Failed to assign {targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue} because the {targetINIs[n]} has an issue.",
                            exception=e,
                        )
                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}")

            else:
                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value[n])  # type: ignore[reportArgumentType]
                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value[n]}")

    def dropdown_assign_value(self, setting_name: str) -> None:
        this_value = self.setting_dictionary[setting_name]["tk_var"].get()
        targetINIs = self.setting_dictionary[setting_name].get("targetINIs", [])
        targetSections = self.setting_dictionary[setting_name].get("targetSections", [])
        theSettings = self.setting_dictionary[setting_name].get("settings", [])

        setting_choices = self.setting_dictionary[setting_name].get("settingChoices")
        delimiter = self.setting_dictionary[setting_name].get("delimiter")
        file_format = self.setting_dictionary[setting_name].get("fileFormat")
        partial = self.setting_dictionary[setting_name].get("partial")
        theValueStr = ""
        if partial:
            for each_partial_setting in partial:
                partial_setting = self.setting_dictionary[each_partial_setting]
                if each_partial_setting == setting_name:
                    theValueStr += "{}"
                else:
                    try:
                        if partial_setting["valueSet"]:
                            theValueStr += partial_setting["tk_var"].get()
                        else:
                            self.sme(f"{each_partial_setting} is not set yet.")
                            return
                    except KeyError:
                        self.sme(f"{each_partial_setting} is not set yet.")
                        return

        if not targetINIs:
            return

        for n in range(len(targetINIs)):
            theValue = ""
            ini_location = self.getINILocation(targetINIs[n])
            the_target_ini = ModifyINI.open(targetINIs[n], Path(ini_location))

            if this_value in {"Manual...", "Browse..."}:
                theValue = ""
            elif delimiter:
                listOfValues = this_value.split(delimiter)
                try:
                    theValue = listOfValues[n]
                except IndexError:
                    theValue = ""
            elif setting_choices:
                if this_value not in setting_choices:
                    return
                theValue = setting_choices[this_value][n]
            elif file_format:
                if file_format == "directory" and this_value == "\\":
                    this_value = this_value[:-1]
                theValue = this_value
            else:
                theValue = this_value

            if partial:
                theValue = theValueStr.format(this_value)
            the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
            self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}")

    def combobox_assign_value(self, setting_name: str) -> None:
        targetINIs = self.setting_dictionary[setting_name].get("targetINIs")

        if not targetINIs:
            return

        str_value = self.setting_dictionary[setting_name]["tk_var"].get()
        targetSections = self.setting_dictionary[setting_name].get("targetSections", [])
        theSettings = self.setting_dictionary[setting_name].get("settings", [])

        decimal_places_str = self.setting_dictionary[setting_name].get("decimal places")
        for n in range(len(targetINIs)):
            ini_location = self.getINILocation(targetINIs[n])
            the_target_ini = ModifyINI.open(targetINIs[n], Path(ini_location))

            if decimal_places_str and str_value:
                decimal_places = int(decimal_places_str)
                float_value = round(float(str_value), decimal_places)
                str_value = str(int(str_value)) if decimal_places == 0 else str(float_value)

            the_target_ini.assign_setting_value(targetSections[n], theSettings[n], str_value)
            self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={str_value}")

    def entry_assign_value(self, setting_name: str) -> None:
        targetINIs = self.setting_dictionary[setting_name].get("targetINIs")
        partial = self.setting_dictionary[setting_name].get("partial")
        theValueStr = ""
        if partial:
            for each_partial_setting in partial:
                partial_setting = self.setting_dictionary[each_partial_setting]
                if each_partial_setting == setting_name:
                    theValueStr += "{}"
                elif partial_setting["valueSet"]:
                    theValueStr += partial_setting["tk_var"].get()
                else:
                    return

        if not targetINIs:
            return

        this_value = self.setting_dictionary[setting_name]["tk_var"].get()
        targetSections = self.setting_dictionary[setting_name].get("targetSections", [])
        theSettings = self.setting_dictionary[setting_name].get("settings", [])

        formula = self.setting_dictionary[setting_name].get("formula")

        for n in range(len(targetINIs)):
            ini_location = self.getINILocation(targetINIs[n])
            the_target_ini = ModifyINI.open(targetINIs[n], Path(ini_location))

            if formula:
                formulaValue = formula.format(this_value)
                try:
                    this_value = str(round(cast("float", simple_eval(formulaValue)), 8))
                except:
                    self.sme(f"Failed to evaluate formula value for {this_value}.")

            if partial:
                this_value = theValueStr.format(this_value)
            the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
            self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")

    def slider_assign_value(self, setting_name: str) -> None:
        setting: BethiniSetting = self.setting_dictionary[setting_name]
        targetINIs = setting.get("targetINIs")

        if not targetINIs:
            return

        this_value = setting["tk_var"].get()
        targetSections = setting.get("targetSections", [])
        theSettings = setting.get("settings", [])

        for n in range(len(targetINIs)):
            ini_location = self.getINILocation(targetINIs[n])
            the_target_ini = ModifyINI.open(targetINIs[n], Path(ini_location))

            try:
                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")

            except AttributeError as e:
                self.sme(
                    f"Failed to set {targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value} because the {targetINIs[n]} has an issue.",
                    exception=e,
                )

    def spinbox_assign_value(self, setting_name: str) -> None:
        targetINIs = self.setting_dictionary[setting_name].get("targetINIs")

        if not targetINIs:
            return

        this_value = self.setting_dictionary[setting_name]["tk_var"].get()
        targetSections = self.setting_dictionary[setting_name].get("targetSections", [])
        theSettings = self.setting_dictionary[setting_name].get("settings", [])

        for n in range(len(targetINIs)):
            ini_location = self.getINILocation(targetINIs[n])
            the_target_ini = ModifyINI.open(targetINIs[n], Path(ini_location))

            the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
            self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")

    def color_assign_value(self, setting_name: str) -> None:
        targetINIs = self.setting_dictionary[setting_name].get("targetINIs")

        if not targetINIs:
            return

        this_value = self.setting_dictionary[setting_name]["tk_var"].get()
        targetSections = self.setting_dictionary[setting_name].get("targetSections", [])
        theSettings = self.setting_dictionary[setting_name].get("settings", [])

        color_value_type = self.setting_dictionary[setting_name].get("colorValueType")
        for n in range(len(targetINIs)):
            ini_location = self.getINILocation(targetINIs[n])
            the_target_ini = ModifyINI.open(targetINIs[n], Path(ini_location))

            if color_value_type in {"hex", "decimal"}:
                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")
            elif color_value_type in {"rgb", "rgb 1", "rgba"}:
                if len(theSettings) > 1:
                    theValue = str(ast.literal_eval(this_value)[n])
                    the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                    self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}")
                else:
                    this_value = this_value.lstrip("(").rstrip(")")
                    the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                    self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")

    def createTabs(self, *, from_choose_game_window: bool = False) -> None:
        global PREVIEW_WINDOW
        PREVIEW_WINDOW = ttk.Toplevel("Preview")
        global PREVIEW_FRAME
        PREVIEW_FRAME = ttk.Frame(PREVIEW_WINDOW)
        PREVIEW_FRAME.pack(padx=5, pady=5)
        preview_close_button = ttk.Button(PREVIEW_WINDOW, text="Close", command=PREVIEW_WINDOW.withdraw)
        preview_close_button.pack(anchor=tk.SE, padx=5, pady=5)
        PREVIEW_WINDOW.protocol("WM_DELETE_WINDOW", PREVIEW_WINDOW.withdraw)
        PREVIEW_WINDOW.withdraw()

        for tab_id in self.tab_dictionary:
            # self.tab_dictionary[tab_id]["Name"] is the name of each tab

            self.create_tab_image(tab_id)
            if self.tab_dictionary[tab_id]["Name"] == "Setup":
                global SETUP_WINDOW
                SETUP_WINDOW = ttk.Toplevel("Setup")
                self.tab_dictionary[tab_id]["SetupWindow"] = SETUP_WINDOW
                self.tab_dictionary[tab_id]["TkFrameForTab"] = ttk.Frame(SETUP_WINDOW)
                self.tab_dictionary[tab_id]["TkFrameForTab"].pack()

                setup_ok_button = ttk.Button(SETUP_WINDOW, text="OK", command=self.withdraw_setup)
                setup_ok_button.pack(anchor=tk.SE, padx=5, pady=5)

                SETUP_WINDOW.protocol("WM_DELETE_WINDOW", self.withdraw_setup)
                if not from_choose_game_window:
                    SETUP_WINDOW.withdraw()
            elif self.tab_dictionary[tab_id]["Name"] == "Preferences":
                global preferencesWindow
                self.tab_dictionary[tab_id]["PreferencesWindow"] = ttk.Toplevel("Preferences")
                preferencesWindow = self.tab_dictionary[tab_id]["PreferencesWindow"]
                self.tab_dictionary[tab_id]["TkFrameForTab"] = ttk.Frame(preferencesWindow)
                self.tab_dictionary[tab_id]["TkFrameForTab"].pack()

                preferences_ok_button = ttk.Button(preferencesWindow, text="OK", command=preferencesWindow.withdraw)
                preferences_ok_button.pack(anchor=tk.SE, padx=5, pady=5)
                preferencesWindow.minsize(300, 100)

                preferencesWindow.protocol("WM_DELETE_WINDOW", preferencesWindow.withdraw)
                preferencesWindow.withdraw()

            else:
                self.tab_dictionary[tab_id]["TkFrameForTab"] = ttk.Frame(self.sub_container)
                self.sub_container.add(
                    self.tab_dictionary[tab_id]["TkFrameForTab"],
                    text=self.tab_dictionary[tab_id]["Name"],
                    image=self.tab_dictionary[tab_id]["TkPhotoImageForTab"],
                    compound=tk.LEFT,
                )

            self.label_frames_for_tab(tab_id)

        self.advanced_tab = ttk.Frame(self.sub_container)
        icon_path = Path.cwd() / "icons" / "Advanced.png"
        self.advanced_tab_image = tk.PhotoImage(file=icon_path, height=16, width=16)
        self.sub_container.add(
            self.advanced_tab,
            text="Advanced",
            image=self.advanced_tab_image,
            compound=tk.LEFT,
        )

        # Add Tableview to Advanced tab
        self.advanced_coldata = [
                "INI File",
                "Section",
                "Setting",
                "Default Value",
                "Current Value",
            ]
        self.advanced_table = Tableview(
            self.advanced_tab,
            coldata=self.advanced_coldata,
            rowdata=[],
            searchable=True,
            autoalign=False,
        )
        self.advanced_table.pack(fill=tk.BOTH, expand=YES)

        self.log_tab = ttk.Frame(self.sub_container)
        icon_path = Path.cwd() / "icons" / "Log.png"
        self.log_tab_image = tk.PhotoImage(file=icon_path, height=16, width=16)

        self.sub_container.add(
            self.log_tab,
            text="Log",
            image=self.log_tab_image,
            compound=tk.LEFT,
        )
        self.log_text = ScrolledText(self.log_tab, padding=5)
        self.log_text.pack(fill=tk.BOTH, expand=YES)
        log_list.add_observer(self.update_log_text)

        self.stop_progress()
        if not from_choose_game_window:
            self.updateValues()
        self.start_progress()
        self.bindTkVars()

        self.sub_container.pack(fill=tk.BOTH, expand=True)
        self.stop_progress()
        self.sme("Loading complete.")

        # Bind the <<NotebookTabChanged>> event to refresh the advanced table
        self.sub_container.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event: tk.Event) -> None:
        selected_tab = event.widget.select()
        selected_tab_text = event.widget.tab(selected_tab, "text")
        
        if self.previous_tab == "Advanced" and selected_tab_text != "Advanced":
            self.updateValues()
        
        if selected_tab_text == "Advanced":
            self.refresh_advanced_table()
        
        self.previous_tab = selected_tab_text  # Update the previously selected tab


    def refresh_advanced_table(self) -> None:
        """Refresh the advanced tableview with INI files and their sections/settings."""
        rowdata = self.populate_advanced_table()
        self.advanced_table.build_table_data(coldata=self.advanced_coldata, rowdata=rowdata)
        self.advanced_table.align_column_left(cid=4)
        self.advanced_table.align_heading_left(cid=4)

    def populate_advanced_table(self):
        """Populate the advanced tableview with INI files and their sections/settings."""
        rowdata = []

        ini_section_setting_dict = APP.preset_values("default")

        for setting_and_section in ini_section_setting_dict:

            target_setting = setting_and_section.split(":")[0]
            target_ini = ini_section_setting_dict[setting_and_section]["ini"]
            target_section = ini_section_setting_dict[setting_and_section]["section"]
            default_value = ini_section_setting_dict[setting_and_section]["value"]

            ini_location = self.getINILocation(target_ini)
            the_target_ini = ModifyINI.open(target_ini, Path(ini_location))
            current_value = the_target_ini.get_value(target_section, target_setting, default_value)

            rowdata.append((target_ini, target_section, target_setting, default_value, current_value))

        return rowdata

    def bindTkVars(self) -> None:
        for setting_name in self.setting_dictionary:
            tk_var = self.setting_dictionary[setting_name].get("tk_var")
            if tk_var:
                tk_var.trace_add(
                    "write",
                    lambda _var, _index, _mode, setting_name=setting_name: self.assign_value(setting_name),
                )
            if self.setting_dictionary[setting_name].get("forceSelect"):
                self.assign_value(setting_name)

    def update_log_text(self) -> None:
        try:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "\n".join(log_list) + '\n')
            self.log_text.see(tk.END)
        except tk.TclError:
            self.sme("Log tab currently unavailable.")

    def updateValues(self) -> None:
        self.start_progress()
        self.sme("Updating INI values.")
        for setting_name in self.setting_dictionary:
            self.widget_type_switcher(setting_name)
        self.sme("Checking for dependent settings.")
        self.dependents()
        self.sme("Update values complete.")
        self.stop_progress()

    def dependents(self) -> None:
        for setting_name in self.dependent_settings_dictionary:
            for master_setting_name in self.dependent_settings_dictionary[setting_name]:
                dependent_setting = self.dependent_settings_dictionary[setting_name][master_setting_name]
                operator_name = dependent_setting["operator"]
                operator_func = operator_dictionary[operator_name]
                set_to_off = dependent_setting.get("setToOff", False)
                if operator_name in {"equal", "not-equal"}:
                    value = dependent_setting.get("value")
                    current_value = self.widget_type_switcher(master_setting_name)
                    var: Literal["string", "float"] = "string"
                else:
                    value = float(dependent_setting["value"])  # type: ignore[reportArgumentType]
                    current_value = float(self.widget_type_switcher(master_setting_name))  # type: ignore[assignment]
                    var = "float"
                setting = self.setting_dictionary[setting_name]
                second_tk_widget = setting.get("second_tk_widget")

                if operator_func(current_value, value):  # type: ignore[reportArgumentType]
                    setting["tk_widget"].configure(state=tk.NORMAL)
                    if second_tk_widget:
                        second_tk_widget.configure(state=tk.NORMAL)
                else:
                    if set_to_off:
                        off_value = dependent_setting.get("Offvalue")
                        setting["tk_var"].set(off_value)  # type: ignore[reportArgumentType]
                    setting["tk_widget"].configure(state=tk.DISABLED)
                    if second_tk_widget:
                        second_tk_widget.configure(state=tk.DISABLED)

                if master_setting_name not in self.settings_that_settings_depend_on:
                    self.settings_that_settings_depend_on[master_setting_name] = {}

                self.settings_that_settings_depend_on[master_setting_name][setting_name] = {
                    "operator": dependent_setting["operator"],
                    "operator_func": cast("Callable[[Any], Any]", operator_func),
                    "value": value or "",
                    "var": var,
                    "setToOff": set_to_off,
                }

    def validate(self, new_value: str, _old_value: str, validate: Literal["integer", "whole", "counting", "float"]) -> bool:
        try:
            if validate == "integer":
                if not new_value or str(abs(int(new_value))).isdigit():
                    return True

            elif validate == "float" and (not new_value or isinstance(float(new_value), float)):
                return True

            elif validate == "whole":
                if not new_value or new_value.isdigit():
                    return True

            elif validate == "counting" and new_value != "0" and (not new_value or new_value.isdigit()):
                return True

        except ValueError:
            pass

        self.sme(f"'{new_value}' is an invalid value for this option.")
        return False

    @staticmethod
    def getINILocation(ini_name: ININame) -> str | Literal[""]:
        if ini_name == ModifyINI.app_config_name:
            return str(Path.cwd())
        ini_setting_name = APP.get_ini_setting_name(ini_name)
        if not ini_setting_name:
            msg = f"Unknown INI: {ini_name}"
            raise NotImplementedError(msg)
        return ModifyINI.app_config().get_value("Directories", ini_setting_name) or ""

    def get_setting_values(
        self,
        target_inis: list[ININame],
        target_sections: list[str],
        target_settings: list[str],
        setting_choices: dict[str, list[str]] | None = None,
        delimiter: Literal["x"] | None = None,
    ) -> Sequence[str | None]:
        """Return the current values of a setting from the given INIs."""

        setting_values: list[str | None] = []
        if not all((target_inis, target_sections, target_settings)):
            return setting_values

        for i, ini_name in enumerate(target_inis):
            ini_location = self.getINILocation(ini_name)
            if ini_location:
                current_section = target_sections[i]
                current_setting = target_settings[i]

                # This looks for a default value in the settings.json
                default_value = None if ModifyINI.app_config_name == ini_name else APP.setting_values[current_setting].get("default")

                target_ini_object = ModifyINI.open(ini_name, Path(ini_location))
                try:
                    value = str(target_ini_object.get_value(current_section, current_setting, default_value))  # type: ignore[reportArgumentType]
                except AttributeError as e:
                    self.sme(
                        f"There was a problem with the existing {target_ini_object} [{current_section}] {current_setting}, so {default_value} will be used.",
                        exception=e,
                    )
                    value = str(default_value)
                setting_values.append(value)

        if not setting_values:
            return setting_values

        # Check to see if the settings correspond with specified setting_name choices.
        if setting_choices:
            for choice in setting_choices:
                if setting_choices[choice] == setting_values:
                    setting_values = [choice]

        # Check to see if there are multiple values separated by a delimiter
        if delimiter and None not in setting_values:
            setting_values = [delimiter.join(cast("list[str]", setting_values))]

        return setting_values


def on_closing(root: bethini_app) -> None:
    """Ask if the user wants to save INI files if any have been modified before quitting.

    This is bound to the main app window closing.
    """

    if messagebox.askyesno("Quit?", "Do you want to quit?"):
        if ModifyINI.app_config().has_been_modified:
            ModifyINI.app_config().save_ini_file(sort=True)
        root.save_ini_files()
        root.quit()


def remove_excess_directory_files(directory: Path, max_to_keep: int, files_to_remove: list[str]) -> None:
    """Remove excess logs or backups.

    directory: The directory to remove files from.
    max_to_keep: The maximum amount of directories that will be excluded from removal.
    files_to_remove: List of files that will be removed.
    """

    if max_to_keep <= -1:
        return

    try:
        subdirectories = [d for d in directory.iterdir() if d.is_dir()]
    except FileNotFoundError:
        return

    if subdirectories:
        subdirectories = [d for d in subdirectories if d.name != "First-Time-Backup"]
    if len(subdirectories) <= max_to_keep:
        return

    subdirectories.sort(key=os.path.getctime, reverse=True)
    for index, dir_path in enumerate(subdirectories):
        if index < max_to_keep:
            logger.debug(f"{dir_path} will be kept.")
            continue

        file_delete_failed = False
        for file in files_to_remove:
            file_path = dir_path / file
            try:
                file_path.unlink(missing_ok=True)
            except OSError:
                logger.exception("Failed to delete file old.")
                file_delete_failed = True

        if file_delete_failed:
            logger.error(f"Old folder cannot be deleted: {dir_path}")
            continue

        try:
            dir_path.rmdir()
        except OSError:
            logger.exception(f"Failed to delete old folder: {dir_path}")
        else:
            logger.debug(f"Old folder was deleted: {dir_path}")


if __name__ == "__main__":
    log_list = observable_list()
    app_log_list_handler = log_list_handler(log_list)
    app_log_list_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(app_log_list_handler)

    iMaxLogs = cast("str", ModifyINI.app_config().get_value("General", "iMaxLogs", "5"))
    ModifyINI.app_config().assign_setting_value("General", "iMaxLogs", iMaxLogs)
    ModifyINI.app_config().assign_setting_value(
        "General",
        "iMaxBackups",
        cast("str", ModifyINI.app_config().get_value("General", "iMaxBackups", "5")),
    )

    # Theme
    theme = ModifyINI.app_config().get_value("General", "sTheme", "superhero")
    if theme not in standThemes.STANDARD_THEMES:
        theme = "superhero"
    ModifyINI.app_config().assign_setting_value("General", "sTheme", theme)

    # Remove excess log files.
    remove_excess_directory_files(Path.cwd() / "logs", int(iMaxLogs), [APP_LOG_FILE.name])

    # Get version
    try:
        with Path("changelog.txt").open(encoding="utf-8") as changelog:
            version = changelog.readline().replace("\n", "")
    except FileNotFoundError:
        version = ""

    window = bethini_app(themename=theme)
    window.choose_game()

    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()
