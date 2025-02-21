#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#
import ast
import configparser
import logging
import math
import os
import sys
import tkinter as tk
import webbrowser
from collections.abc import Callable
from datetime import datetime
from operator import eq, ge, gt, le, lt, ne
from pathlib import Path
from shutil import copyfile
from tkinter import colorchooser, messagebox, simpledialog
from typing import TYPE_CHECKING, Any, Literal, NotRequired, TypeAlias, TypedDict

import ttkbootstrap as ttk
from simpleeval import simple_eval
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Icon
from ttkbootstrap.themes import standard as standThemes

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
from lib.tooltips import Hovertip

IntStr: TypeAlias = str
"""A string representing an integer."""

BoolIntStr: TypeAlias = Literal["0", "1"]
"""A string representing an integer boolean."""

FloatStr: TypeAlias = str
"""A string representing an float."""

ValidationType: TypeAlias = Literal["integer", "whole", "counting", "float"]

Browse: TypeAlias = tuple[Literal["directory"], Literal["directory"] | str, Literal["directory", "file"]]

ColorType: TypeAlias = Literal["rgb", "rgb 1", "rgba", "decimal", "hex"]
ColorValue: TypeAlias = str | tuple[int, ...]

SettingType: TypeAlias = Literal[
    "Checkbutton",
    "Color",
    "Combobox",
    "Dropdown",
    "Entry",
    "preset",
    "radioPreset",
    "Slider",
    "Spinbox",
]

class GameSetting(TypedDict):
    name: str
    section: str
    alwaysPrint: bool
    ini: str
    type: Literal["boolean", "float", "number", "string"]
    value: dict[Literal["default", "recommended"] | str, int | float | str]


class DependentSetting(TypedDict):
    operator: Literal["greater-than", "greater-or-equal-than", "less-than", "less-or-equal-than", "not-equal", "equal"]
    value: str | list[list[str]]

class BethiniSetting(
    TypedDict(
        "Setting",
        {
            "decimal places": NotRequired[IntStr],
            "from": NotRequired[IntStr],
            "preset id": NotRequired[str],
        },
    )
):
    """Type annotations for setting dictionary values.

    :Usage:
    setting: Setting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
    """

    Name: str
    browse: Browse
    choices: str | list[Literal["Browse...", "Manual..."] | str]
    colorValueType: ColorType
    custom_function: str
    customWidth: IntStr
    delimiter: Literal["x"]
    dependentSettings: dict[str, DependentSetting]
    entry_width: IntStr
    fileFormat: Literal["directory", "file"]
    forceSelect: IntStr
    increment: IntStr
    length: IntStr
    Offvalue: list[list[Literal[""] | BoolIntStr | IntStr | FloatStr | str]]
    Onvalue: list[list[Literal[""] | BoolIntStr | IntStr | FloatStr | str]]
    partial: list[str]
    rgbType: Literal["multiple settings"]
    second_tk_widget: ttk.Spinbox
    settingChoices: dict[str, list[str]]
    settings: list[str]
    targetINIs: list[str]
    targetSections: list[str]
    tk_var: tk.StringVar
    TkCheckbutton: ttk.Checkbutton
    TkColor: tk.Button
    TkCombobox: ttk.Combobox
    TkDescriptionLabel: ttk.Label
    TkEntry: ttk.Entry
    TkFinalSettingFrame: ttk.Frame
    TkLabel: ttk.Label
    TkOptionMenu: ttk.OptionMenu
    TkPresetButton: ttk.Button
    TkRadioPreset: ttk.Radiobutton
    TkSlider: "Scalar"
    TkSpinbox: ttk.Spinbox
    to: IntStr
    tooltip_wrap_length: int
    tooltip_wrap_length: int
    tooltip: str
    type: SettingType
    validate: ValidationType | str
    value: str
    width: IntStr


class PackSettings(TypedDict):
    Anchor: Literal["NW", "N", "NE", "W", "Center", "E", "SW", "S", "SE"]
    Expand: Literal[0, 1]
    Fill: Literal["None", "X", "Y", "Both"]
    Side: Literal["Left", "Right", "Top", "Bottom"]


class DisplayTab(TypedDict):
    NumberOfVerticallyStackedSettings: IntStr
    Pack: PackSettings
    Settings: dict[str, BethiniSetting]


class AppSettings(TypedDict):
    customFunctions: dict[str, str]
    Default: Literal[""]
    displayTabs: dict[str, dict[Literal["NoLabelFrame"] | str, DisplayTab]]
    INIs: dict[str, str]
    presetsIgnoreTheseSettings: list[str]
    valueTypes: list[str]


# from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR, S_IWGRP, S_IWRITE
# This is for changing file read-only access via os.chmod(filename, S_IREAD,
# S_IRGRP, #S_IROTH) Not currently used.

# Configure Logging
# TODO Refactor usage of "the_backup_directory"
LOG_DIR_DATE: str = f"{datetime.now().strftime("%Y %m-%b %d %a - %H.%M.%S")}"
APP_LOG_DIR = Path.cwd() / "logs" / LOG_DIR_DATE
APP_LOG_DIR.mkdir(parents=True, exist_ok=True)
APP_LOG_FILE = APP_LOG_DIR / "log.log"

fmt: str = "%(asctime)s  [%(levelname)s]  %(filename)s  %(funcName)s:%(lineno)s:  %(message)s"
datefmt: str  = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(filename=APP_LOG_FILE, filemode="w", format=fmt, datefmt=datefmt, encoding="utf-8", level=logging.DEBUG)
logger = logging.getLogger()
_log_stdout = logging.StreamHandler(sys.stdout) # to console
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
    "equal": eq
    }

tkinter_switch_dict = {
    "left": tk.LEFT,
    "right": tk.RIGHT,
    "top": tk.TOP,
    "bottom": tk.BOTTOM,
    "x": tk.X,
    "y": tk.Y,
    "center": tk.CENTER,
    "both": tk.BOTH,
    "horizontal": tk.HORIZONTAL,
    "flat": tk.FLAT,
    "n": tk.N,
    "ne": tk.NE,
    "nw": tk.NW,
    "ns": tk.NS,
    "nsew": tk.NSEW,
    "s": tk.S,
    "se": tk.SE,
    "sw": tk.SW,
    "e": tk.E,
    "ew": tk.EW,
    "w": tk.W,
    "none": tk.NONE,
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
    app_config.assign_setting_value("General", "sTheme", theme_name)

class Scalar(ttk.Scale):
    """A ttk.Scale with limited decimal places."""

    def __init__(
        self,
        master: tk.Misc | None = None,
        command: str | Callable[[str], object] = "",
        from_: float = 0,
        length: int = 100,
        orient: Literal["horizontal", "vertical"] = "horizontal",
        to: float = 1,
        variable: ttk.IntVar | ttk.DoubleVar = ...,
        decimal_places: IntStr = "0") -> None:

        self.decimal_places = decimal_places
        if command:
            self.chain = command
        else:
            self.chain = lambda *_a: None
        super().__init__(master, command=self._value_changed, from_=from_, length=length, orient=orient, to=to, variable=variable)

    def _value_changed(self, new_value: str) -> None:
        decimal_places = int(self.decimal_places)
        value = round(float(new_value), decimal_places)
        if decimal_places == 0:
            value = int(value)
        self.winfo_toplevel().globalsetvar(self.cget("variable"), (value))
        self.chain(value)

class bethini_app(ttk.Window):
    """This is the main app, the glue that creates the GUI."""

    def __init__(self, themename: str) -> None:
        super().__init__(self, themename=themename, iconphoto=Path("Icons/Icon.png"), minsize=(400, 200))

        CustomFunctions.screenwidth = self.winfo_screenwidth()
        CustomFunctions.screenheight = self.winfo_screenheight()

        # Variables
        self.setup_dictionary = {}
        self.tab_dictionary: dict[str, dict[str, Any]] = {}  # Temporary Any annotation to replace invalid type "tab"
        self.setting_dictionary = {}
        self.dependent_settings_dictionary = {}
        self.settings_that_settings_depend_on = {}
        self.tab = []

        self.widget_type_function = {
            "Checkbutton": self.checkbox,
            "preset": self.preset,
            "Dropdown": self.dropdown,
            "Entry": self.entry,
            "Spinbox": self.spinbox,
            "Combobox": self.combobox,
            "Color": self.color,
            "Slider": self.slider,
            "radioPreset": self.radio_preset
            }

        self.widget_type_value = {
            "TkCheckbutton": self.checkbox_value,
            "TkOptionMenu": self.dropdown_value,
            "TkEntry": self.entry_value,
            "TkSpinbox": self.spinbox_value,
            "TkCombobox": self.combobox_value,
            "TkColor": self.color_value,
            "TkSlider": self.slider_value,
            "TkRadioPreset": self.radio_preset_value
            }

        self.widget_type_assign_value = {
            "TkCheckbutton": self.checkbox_assign_value,
            "TkOptionMenu": self.dropdown_assign_value,
            "TkEntry": self.entry_assign_value,
            "TkSpinbox": self.spinbox_assign_value,
            "TkCombobox": self.combobox_assign_value,
            "TkColor": self.color_assign_value,
            "TkSlider": self.slider_assign_value
            }

        self.style_override = ttk.Style()

        self.the_canvas = ttk.Canvas(self)
        self.hsbframeholder = ttk.Frame(self)

        self.vsb = AutoScrollbar(self, orient=tk.VERTICAL,
                                 command=self.the_canvas.yview)
        self.hsb = AutoScrollbar(self.hsbframeholder, orient=tk.HORIZONTAL,
                                 command=self.the_canvas.xview)
        self.the_canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.container = ttk.Frame(self.the_canvas)
        self.container.bind_all("<Control-s>", self.save_ini_files)

        self.hsbframeholder.pack(side=tk.BOTTOM, fill=tk.X)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.the_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_frame = self.the_canvas.create_window((4,4),
                                                          window=self.container,
                                                          tags="self.container")
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
        self.label_Pie = ttk.Label(self.choose_game_frame_2, text="Performance INI Editor\nby DoubleYou", font=("Segoe UI", 15), justify=tk.CENTER, style=ttk.WARNING)
        self.label_link = ttk.Label(self.choose_game_frame_2, text="www.nexusmods.com/site/mods/631", font=("Segoe UI", 10), cursor="hand2", style=ttk.INFO)

        self.choose_game_label = ttk.Label(self.choose_game_frame_2, text="Choose Game", font=("Segoe UI", 15))

        self.choose_game_tree = ttk.Treeview(self.choose_game_frame_2, selectmode=tk.BROWSE, show="tree", columns=("Name"))
        self.choose_game_tree.column("#0", width=0, stretch=tk.NO)
        self.choose_game_tree.column("Name", anchor=tk.W, width=300)

        self.style_override.configure("choose_game_button.TButton", font=("Segoe UI", 14))
        self.choose_game_button = ttk.Button(self.choose_game_frame_2, text="Select Game", style="choose_game_button.TButton",
                                             command=lambda: self.choose_game_done(self.choose_game_tree.focus()))

        self.choose_game_tip = ttk.Label(self.choose_game_frame_2, text="Tip: You can change the game at any time\nby going to File > Choose Game.", font=("Segoe UI", 12), justify=tk.CENTER, style="success")
        for option in Path("apps").iterdir():
            self.choose_game_tree.insert("", tk.END, id=option.name, text=option.name, values=[option.name])


        self.preferences_frame = ttk.Frame(self.choose_game_frame_2)

        self.theme_label = ttk.Label(self.preferences_frame, text="Theme:")
        theme_names = standThemes.STANDARD_THEMES.keys()
        self.theme_name = tk.StringVar(self)
        self.theme_dropdown = ttk.OptionMenu(self.preferences_frame,
                                             self.theme_name, app_config.get_value("General", "sTheme", "superhero"), *theme_names,
                                             command=lambda t: set_theme(self.style_override, t))
        self.theme_dropdown.var = self.theme_name

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
        self.choose_game_window.minsize(300,35)

        self.preset_var = tk.StringVar(self)
        self.preset_var.set("Bethini")

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
        old_color: ColorValue = button_to_modify.var.get()
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
                new_alpha = simpledialog.askinteger("Alpha", "Alpha transparency (0 - 255):", initialvalue=alpha, minvalue = 0, maxvalue = 255)
                logger.debug(f"New alpha: {new_alpha}")
            except:
                new_alpha = alpha

        elif color_value_type == "rgb 1":
            # "(1.0000, 1.0000, 1.0000)"
            # (255, 255, 255)
            old_color = tuple(int(float(i)*255) for i in ast.literal_eval(old_color))

        elif color_value_type == "decimal":
            old_color = rgb_to_hex(decimal_to_rgb(old_color))

        response = colorchooser.askcolor(color=old_color)
        new_color = response[1].upper() if response[1] else old_color

        rgb = hex_to_rgb(new_color)
        luminance = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
        the_text_color = "#FFFFFF" if luminance < 128 else "#000000"
        button_to_modify.configure(bg=new_color, activebackground=new_color, fg=the_text_color)
        if color_value_type == "rgb":
            button_to_modify.var.set(str(hex_to_rgb(new_color)).replace(" ",""))

        elif color_value_type == "rgba":
            new_color_tuple = hex_to_rgb(new_color)
            new_color_list = list(new_color_tuple)
            if new_alpha is not None:
                new_color_list.append(new_alpha)
            new_color_tuple = tuple(new_color_list)
            button_to_modify.var.set(str(new_color_tuple).replace(" ",""))

        elif color_value_type == "rgb 1":
            # (255, 255, 255)
            # "(1.0000, 1.0000, 1.0000)"
            the_rgb = str(tuple(round(i/255,4) for i in hex_to_rgb(new_color)))
            button_to_modify.var.set(the_rgb)

        elif color_value_type == "decimal":
            button_to_modify.var.set(hex_to_decimal(new_color))

        else:
            button_to_modify.var.set(new_color)
        preferencesWindow.lift()

        return new_color

    def tooltip(self, each_tab, the_label_frame, on_frame, the_setting, id_) -> None:
        """Sets the tooltips."""

        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]

        # Fectches the tooltip description.
        tooltip_description = setting.get("tooltip", "No description available.")

        tooltip_wrap_length = setting.get("tooltip_wrap_length", 200)

        # Checks for INI settings specified, and adds them to the bottom of the tooltip if found.
        target_ini_files = setting.get("targetINIs", [])
        if target_ini_files: #If there are INI settings specified
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
        else: #If there are no INI settings specified, only the tooltip description will be used.
            tooltip_text = tooltip_description

        setting_name = setting.get("Name")
        photo_for_setting: Path | None = Path.cwd() / "apps" / GAME_NAME / "images" / f"{setting_name}.jpg"
        if not (photo_for_setting and photo_for_setting.is_file()):
            photo_for_setting = None

        Hovertip(setting[id_], tooltip_text, [PREVIEW_WINDOW, PREVIEW_FRAME, photo_for_setting], tooltip_wrap_length)

    def choose_game(self, *, forced: bool=False) -> None:
        self.withdraw()
        # The Choose App/Game dialog window.  The window is skipped here if
        # sAppName is already set in the Bethini.ini file.
        try:
            choose_game_var = app_config.get_value("General","sAppName")
            if forced:
                self.sme("Force choose game/application.")
                raise NameError

            if app_config.get_value("General", "bAlwaysSelectGame", "1") != "0":
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
            messagebox.showerror(title="Unhandled exception", message=f"An unhandled exception occurred. See log for details.\n{e}\nThis program will now close. No files will be modified.")
            self.quit()
            sys.exit(1)

    def choose_game_done(self, game: str, *, from_choose_game_window: bool=False) -> None:
        if not game:
            return

        self.choose_game_window.withdraw()

        # Once the app/game is selected, this loads it.
        try:
            self.choose_game_var = app_config.get_value("General","sAppName")
            if self.choose_game_var != game:
                self.sme(f"Change of game from {self.choose_game_var} to {game}")
                msg = f"App/Game specified in {my_app_config} differs from the game chosen, so it will be changed to the one you chose."
                raise Exception(msg)

        except Exception as e:
            self.sme("Change of game/application", exception=e)
            app_config.assign_setting_value("General","sAppName", game)
            from_choose_game_window = True

        self.wm_title(f"{my_app_name} {version} - {game}")

        # #############
        # App globals
        # #############

        global APP
        APP = AppName(game)
        global GAME_NAME
        GAME_NAME = APP.data["gameName"]  # type: ignore[reportUnknownVariableType]
        if TYPE_CHECKING:
            assert isinstance(GAME_NAME, str)
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

        self.tab_dictionary = {}
        for tab_number, tab in enumerate(APP.bethini["displayTabs"], start=1):
            self.tab_dictionary[f"Page{tab_number}"] = {"Name": tab}

        self.setup_dictionary = {}
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
            messagebox.showerror(title="Unhandled exception", message=f"An unhandled exception occurred. See log for details.\n{e}\nThis program will now close. No files will be modified.")
            self.quit()
            sys.exit(1)

        self.menu(self.style_override)


    def menu(self, style_object: ttk.Style) -> None:
        menubar = tk.Menu(self)

        # File
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Save", command = self.save_ini_files)
        filemenu.add_separator()
        filemenu.add_command(label="Choose Game", command = lambda: self.choose_game(forced=True))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command= lambda: on_closing(self))

        # Edit
        editmenu = tk.Menu(menubar, tearoff=False)
        editmenu.add_command(label="Preferences", command = preferencesWindow.deiconify)
        editmenu.add_command(label="Setup", command = self.show_setup)

        # Theme
        theme_menu = tk.Menu(menubar, tearoff=False)
        theme_names = list(standThemes.STANDARD_THEMES.keys())
        for theme_name in theme_names:
            theme_menu.add_command(label=theme_name, command = lambda t=theme_name: set_theme(style_object, t))

        # Help
        helpmenu = tk.Menu(menubar, tearoff=False)
        helpmenu.add_command(label="Visit Web Page",
                             command = lambda: webbrowser.open_new_tab("https://www.nexusmods.com/site/mods/631/"))
        helpmenu.add_command(label="Get Support",
                             command = lambda: webbrowser.open_new_tab("https://stepmodifications.org/forum/forum/200-Bethini-support/"))
        helpmenu.add_command(label="About", command = self.about)

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

        about_label = ttk.Label(about_frame_real,
                               text=f"About {my_app_name} {version}\n\n{my_app_name} was created by DoubleYou.\n\nLicensing is CC BY-NC-SA.",
                               justify=tk.CENTER)

        about_frame.pack(fill=tk.BOTH, expand=True)
        about_frame_real.pack(anchor=tk.CENTER, expand=True)
        about_label.pack(anchor=tk.CENTER, padx=10, pady=10)

    def show_setup(self) -> None:
        self.withdraw()
        SETUP_WINDOW.deiconify()

    def withdraw_setup(self) -> None:
        SETUP_WINDOW.withdraw()
        self.deiconify()
        self.updateValues()

    def save_ini_files(self, _event: "tk.Event[tk.Misc] | None" = None) -> None:
        # self.openINIs = {
        #    my_app_config : {
        #        "located": {
        #            "1": {
        #                "at": "",
        #                "object": app_config
        #                }
        #            }
        #        }
        #    }
        files_saved = False
        self.remove_invalid_settings()
        try:
            self.apply_ini_dict(APP.preset_values("fixedDefault"), only_if_missing=True)
        except NameError as e:
            self.sme(f"NameError: {e}", exception=e)
            return

        files_to_remove = [*list(open_inis)[1:], "log.log"]
        for each_ini in open_inis:
            location_list = list(open_inis[each_ini]["located"].keys())
            for n in range(len(location_list)):
                located_at = open_inis[each_ini]["located"][str(n+1)].get("at")
                this_location = Path(located_at) if located_at else Path.cwd()
                this_ini_object = open_inis[each_ini]["located"][str(n+1)]["object"]
                if each_ini == my_app_config:
                    continue
                if not this_ini_object.has_been_modified:
                    self.sme(f"{each_ini} has not been modified, so there is no reason to resave it.")
                    continue
                if messagebox.askyesno(f"Save {each_ini}", f"Do you want to save {this_location / each_ini}?"):
                    # We need to make a backup of each save before actually saving.
                    do_first_time_backup = remove_excess_directory_files(this_location / f"{my_app_name} backups",
                                                                    int(app_config.get_value("General", "iMaxBackups", "-1")),
                                                                    files_to_remove)
                    if do_first_time_backup:
                        the_backup_directory = this_location / f"{my_app_name} backups" / "First-Time-Backup"
                        the_backup_directory.mkdir(parents=True, exist_ok=True)
                        if (the_backup_directory / each_ini).exists():
                            self.sme(f"{the_backup_directory / each_ini} exists, so it will not be overwritten.")
                        else:
                            try:
                                copyfile(this_location / each_ini, the_backup_directory / each_ini)
                            except FileNotFoundError as e:
                                self.sme(f"{this_location / each_ini} does not exist, so it cannot be backed up. This is typically caused by a path not being set correctly.", exception=e)
                        copyfile(APP_LOG_FILE, the_backup_directory / "log.log")
                    the_backup_directory = this_location / f"{my_app_name} backups" / LOG_DIR_DATE
                    the_backup_directory.mkdir(parents=True, exist_ok=True)
                    if (the_backup_directory / each_ini).exists():
                        self.sme(f"{the_backup_directory / each_ini} exists, so it will not be overwritten.")
                    else:
                        try:
                            copyfile(this_location / each_ini, the_backup_directory / each_ini)
                        except FileNotFoundError as e:
                            self.sme(f"{this_location / each_ini} does not exist, so it cannot be backed up. This is typically caused by a path not being set correctly.", exception=e)
                    copyfile(APP_LOG_FILE, the_backup_directory / "log.log")
                    this_ini_object.save_ini_file(sort=True)
                    files_saved = True
                    self.sme(f"{this_location / each_ini} saved.")
        if not files_saved:
            self.sme("No files were modified.")

    def set_preset(self, preset_id) -> None:
        self.start_progress()
        if preset_id == "Default":
            self.apply_ini_dict(APP.preset_values("default"))
            self.remove_ini_dict(APP.can_remove())
            self.apply_ini_dict(APP.preset_values("fixedDefault"))
            preset_var = ""
        elif preset_id == "recommended":
            preset_dict = APP.preset_values(f"{preset_id}")
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
        for each_ini in open_inis:
            if each_ini == my_app_config:
                continue
            if APP.inis(each_ini):
                location_list = list(open_inis[each_ini]["located"].keys())
                for n in range(len(location_list)):
                    this_ini_object = open_inis[each_ini]["located"][str(n+1)]["object"]

                    sections = this_ini_object.get_sections()

                    for section in sections:
                        settings = this_ini_object.get_settings(section)
                        if settings == []:
                            this_ini_object.remove_section(section)
                            self.sme(f"{section} was removed because it was empty.")
                        else:
                            for each_setting in settings:
                                if ";" in each_setting or "#" in each_setting:
                                    self.sme(f"{each_setting}:{section} will be preserved, as it is a comment.")
                                elif not APP.does_setting_exist(each_ini, section, each_setting):
                                    # sm(this_ini_object.remove_setting(section, each_setting))
                                    # Disabling the removal of unknown settings.
                                    self.sme(f"{each_setting}:{section} {each_ini} appears to be invalid.")
                                    if this_ini_object.get_settings(section) == []:
                                        this_ini_object.remove_section(section)
                                        self.sme(f"{section} was removed because it was empty.")

    def apply_ini_dict(self, ini_dict, *, only_if_missing: bool=False) -> None:
        for each_setting in ini_dict:
            target_setting = each_setting.split(":")[0]
            if target_setting in APP.bethini["presetsIgnoreTheseSettings"] and not only_if_missing:
                continue
            target_ini = ini_dict[each_setting]["ini"]
            target_section = ini_dict[each_setting]["section"]
            this_value = str(ini_dict[each_setting]["value"])

            ini_location = APP.inis(target_ini)
            if ini_location:
                ini_location = app_config.get_value("Directories", ini_location)
            the_target_ini = open_ini(ini_location, target_ini)

            # Check if we are only supposed to add the value if the value is missing
            if only_if_missing and (the_target_ini.get_value(target_section, target_setting) is not None):
                continue
            the_target_ini.assign_setting_value(target_section, target_setting, this_value)
            self.sme(f"{target_ini} [{target_section}] {target_setting}={this_value}")

    def remove_ini_dict(self, ini_dict) -> None:
        for each_setting in ini_dict:
            target_setting = each_setting.split(":")[0]
            target_ini = ini_dict[each_setting]["ini"]
            target_section = ini_dict[each_setting]["section"]
            this_value = str(ini_dict[each_setting]["value"])

            ini_location = APP.inis(target_ini)
            if ini_location:
                ini_location = app_config.get_value("Directories", ini_location)
            the_target_ini = open_ini(ini_location, target_ini)

            current_value = the_target_ini.get_value(target_section, target_setting, this_value)

            if current_value == this_value:
                if the_target_ini.remove_setting(target_section, target_setting):
                    self.sme(f"{target_ini} [{target_section}] {target_setting}={this_value}, which is the default value, and since it is not set to alwaysPrint, it will be removed")
                else:
                    self.sme(f"No section {target_section} exists for {target_setting} in {the_target_ini}.")

    def create_tab_image(self, each_tab) -> None:
        icon_path = Path.cwd() / f"icons/{self.tab_dictionary[each_tab]['Name']}.png"
        try:
            if not icon_path.is_file():
                icon_path = icon_path.with_name("Blank.png")
                if not icon_path.is_file():
                    self.sme(f"No icon for tab '{each_tab}'")
                    tab_icon = tk.PhotoImage(data=Icon.warning)
                    return

            tab_icon = tk.PhotoImage(file=icon_path, height=16, width=16)

        except tk.TclError as e:
            self.sme(f"Failed to load icon for tab '{each_tab}':\n{icon_path}", exception=e)
            tab_icon = tk.PhotoImage(data=Icon.warning)

        finally:
            self.tab_dictionary[each_tab]["TkPhotoImageForTab"] = tab_icon

    def label_frames_for_tab(self, each_tab) -> None:
        the_dict = self.tab_dictionary[each_tab]
        the_dict["LabelFrames"] = {}
        for label_frame_number, label_frame in enumerate(APP.bethini["displayTabs"][the_dict["Name"]], start=1):
            the_label_frame=f"LabelFrame{label_frame_number}"
            the_dict["LabelFrames"][the_label_frame] = {"Name": label_frame}
            if "NoLabelFrame" not in label_frame:
                the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"] = ttk.LabelFrame(the_dict["TkFrameForTab"], text=label_frame, width=200)
            else:
                the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"] = ttk.Frame(the_dict["TkFrameForTab"])

            pack_settings = APP.pack_settings(self.tab_dictionary[each_tab]["Name"], label_frame)
            the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"].pack(anchor=tkinter_switch_dict[pack_settings.get("Anchor", tk.NW).lower()],
                                                                          side=tkinter_switch_dict[pack_settings.get("Side", tk.TOP).lower()],
                                                                          fill=tkinter_switch_dict[pack_settings.get("Fill", tk.BOTH).lower()],
                                                                          expand=pack_settings.get("Expand", 1),
                                                                          padx=10, pady=10)
            self.settings_frames_for_label_frame(each_tab, label_frame, the_label_frame)

    def settings_frames_for_label_frame(self, each_tab, label_frame, the_label_frame) -> None:
        setting_frames = {}
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"] = setting_frames
        number_of_vertically_stacked_settings = int(APP.number_of_vertically_stacked_settings(self.tab_dictionary[each_tab]["Name"], label_frame))

        for setting_number, each_setting in enumerate(APP.bethini["displayTabs"][self.tab_dictionary[each_tab]["Name"]][label_frame]["Settings"], start=1):
            on_frame = f"SettingFrame{math.ceil(setting_number / number_of_vertically_stacked_settings) - 1}"
            if on_frame not in setting_frames:
                setting_frames[on_frame] = {}
                setting_frames[on_frame]["TkSettingFrame"] = ttk.Frame(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["TkLabelFrame"])
                setting_frames[on_frame]["TkSettingFrame"].pack(side=tk.LEFT, anchor=tk.NW)
            the_setting = f"Setting{setting_number}"
            setting_frames[on_frame][the_setting] = {"Name": each_setting}
            setting_frames[on_frame][the_setting]["TkFinalSettingFrame"] = ttk.Frame(setting_frames[on_frame]["TkSettingFrame"])
            setting_frames[on_frame][the_setting]["TkFinalSettingFrame"].pack(anchor=tk.W, padx=5, pady=2)
            if "Placeholder" not in each_setting:
                setting_frames[on_frame][the_setting].update(APP.bethini["displayTabs"][self.tab_dictionary[each_tab]["Name"]][label_frame]["Settings"][each_setting])
                self.setting_label(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting)

    def setting_label(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        setting_type = setting.get("type")
        if setting_type not in types_without_label:
            setting_label = each_setting if setting_type else ""
            setting_label_width = setting.get("customWidth")
            setting["TkLabel"] = ttk.Label(setting["TkFinalSettingFrame"], text=setting_label, width=setting_label_width, anchor=tk.E)
            if setting_type in types_packed_left:
                setting["TkLabel"].pack(anchor=tk.CENTER, side=tk.LEFT, padx=5, pady=5)
            else:
                setting["TkLabel"].pack(anchor=tk.CENTER, padx=5, pady=5)
        setting_description = setting.get("Description")
        if setting_description:
            setting["TkDescriptionLabel"] = ttk.Label(setting["TkFinalSettingFrame"], text=setting_description, justify=tk.LEFT, wraplength=900)
            setting["TkDescriptionLabel"].pack(anchor=tk.N)
        self.setting_type_switcher(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, setting_type)

    def setting_type_switcher(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, setting_type) -> None:
        func = self.widget_type_function.get(setting_type)
        if func is not None:
            func(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting)

    def widget_type_switcher(self, each_setting):
        id_ = self.setting_dictionary[each_setting].get("id")
        func = self.widget_type_value.get(id_)
        if func is not None:
            return func(each_setting)
        return None

    def add_to_setting_dictionary(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_) -> None:
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        self.setting_dictionary.update({
            each_setting: {
                "each_tab": each_tab,
                "label_frame": label_frame,
                "the_label_frame": the_label_frame,
                "on_frame": on_frame,
                "the_setting": the_setting,
                "id": id_,
                "tk_widget": setting[id_],
                "targetINIs": setting.get("targetINIs"),
                "settings": setting.get("settings"),
                "targetSections": setting.get("targetSections"),
            }
        })

        dependent_settings = setting.get("dependentSettings")
        if dependent_settings:
            self.dependent_settings_dictionary[each_setting] = dependent_settings

    def checkbox(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        """Create a ttk.Checkbutton."""

        id_ = "TkCheckbutton"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        setting["tk_var"] = tk.StringVar(self)
        on_value = setting.get("Onvalue")
        off_value = setting.get("Offvalue")
        setting[id_] = ttk.Checkbutton(setting["TkFinalSettingFrame"], text=each_setting, variable=setting["tk_var"], onvalue=on_value, offvalue=off_value)
        setting[id_].var = setting["tk_var"]
        setting[id_].pack(anchor=tk.W, padx=5, pady=7)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": setting["tk_var"],
            "onvalue": on_value,
            "offvalue": off_value,
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def preset(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        """Create a Preset ttk.Button."""

        id_ = "TkPresetButton"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        preset_id = setting.get("preset id")
        setting[id_] = ttk.Button(setting["TkFinalSettingFrame"], text=each_setting, command=lambda: self.set_preset(preset_id))
        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=0)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

    def radio_preset(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        """Create a Preset Radiobutton."""

        id_ = "TkRadioPreset"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        value = setting.get("value")
        setting[id_] = ttk.Radiobutton(setting["TkFinalSettingFrame"], text=each_setting, variable=self.preset_var, value=value)
        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=7)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": self.preset_var
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def dropdown(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        """Create a ttk.OptionMenu."""

        id_ = "TkOptionMenu"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        options = setting.get("choices")

        # Custom functions allow us to auto-detect certain
        # predefined options that can then easily be selected.

        if isinstance(options, str):
            if "FUNC" in options:
                option_string = APP.bethini["customFunctions"][options]
                if "{}" in option_string:
                    custom_function = APP.bethini["customFunctions"][f"{options}Format"]
                    value_to_insert = getattr(CustomFunctions, custom_function)(GAME_NAME)
                    options = value_to_insert
        else:
            for n in range(len(options)):
                if "FUNC" in options[n]:
                    option_string = APP.bethini["customFunctions"][options[n]]
                    if "{}" in option_string:
                        custom_function = APP.bethini["customFunctions"][f"{options[n]}Format"]
                        value_to_insert = getattr(CustomFunctions, custom_function)(GAME_NAME)
                        options[n] = option_string.format(value_to_insert)

        setting["tk_var"] = tk.StringVar(self)

        browse = setting.get("browse", ("directory", "directory", "directory"))
        func = setting.get("custom_function", "")
        def browse_to_loc(choice: str, var: tk.StringVar = setting["tk_var"], browse: Browse = browse, function: str = func) -> None:
            location = browse_to_location(choice, browse, function, GAME_NAME)
            if location:
                var.set(location)
            elif options[0] not in {"Browse...", "Manual..."}:
                var.set(options[0])
            else:
                var.set("")

        setting[id_] = ttk.OptionMenu(
            setting["TkFinalSettingFrame"],
            setting["tk_var"],
            options[0],
            *options,
            command=browse_to_loc,
        )
        setting[id_].var = setting["tk_var"]
        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": setting["tk_var"],
            "options": options,
            "settingChoices": setting.get("settingChoices"),
            "delimiter": setting.get("delimiter"),
            "decimal places": setting.get("decimal places"),
            "fileFormat": setting.get("fileFormat"),
            "forceSelect": setting.get("forceSelect"),
            "partial": setting.get("partial"),
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def combobox(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        """Create a ttk.Combobox."""

        id_ = "TkCombobox"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        options = setting.get("choices")
        width = setting.get("width")
        validate = setting.get("validate")

        setting["tk_var"] = tk.StringVar(self)

        if validate:
            setting["validate"] = self.register(self.validate)
            setting[id_] = ttk.Combobox(
                setting["TkFinalSettingFrame"],
                textvariable=setting["tk_var"],
                width=width,
                values=options,
                validate="key",
                validatecommand=(setting["validate"], "%P", "%s", validate),
            )
        else:
            setting[id_] = ttk.Combobox(
                setting["TkFinalSettingFrame"],
                textvariable=setting["tk_var"],
                width=width,
                values=options,
            )

        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": setting["tk_var"],
            "options": options,
            "decimal places": setting.get("decimal places")
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def entry(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        """Create a ttk.Entry."""

        id_ = "TkEntry"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        entry_width = setting.get("entry_width")
        validate = setting.get("validate")

        setting["tk_var"] = tk.StringVar(self)

        if validate:
            setting["validate"] = self.register(self.validate)
            setting[id_] = ttk.Entry(
                setting["TkFinalSettingFrame"],
                width=entry_width,
                validate="key",
                validatecommand=(setting["validate"], "%P", "%s", validate),
                textvariable=setting["tk_var"],
            )
        else:
            setting[id_] = ttk.Entry(setting["TkFinalSettingFrame"], width=entry_width, textvariable=setting["tk_var"])

        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": setting["tk_var"],
            "formula": setting.get("formula"),
            "decimal places": setting.get("decimal places"),
            "partial": setting.get("partial"),
            "fileFormat": setting.get("fileFormat"),
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def slider(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        id_ = "TkSlider"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        from_value = setting.get("from")
        to_value = setting.get("to")
        decimal_places = setting.get("decimal places")
        length_value = setting.get("length")

        setting["tk_var"] = tk.StringVar(self)

        setting[id_] = Scalar(
            setting["TkFinalSettingFrame"],
            from_=from_value,
            to=to_value,
            orient=tk.HORIZONTAL,
            length=length_value,
            decimal_places=decimal_places,
            variable=setting["tk_var"],
        )

        width = setting.get("width")
        validate = setting.get("validate")
        increment_value = setting.get("increment")

        reversed_ = setting.get("reversed")
        if reversed_:
            from_value = setting.get("to")
            to_value = setting.get("from")

        if validate:
            setting["validate"] = self.register(self.validate)
            setting["second_tk_widget"] = ttk.Spinbox(
                setting["TkFinalSettingFrame"],
                width=width,
                validate="key",
                increment=increment_value,
                from_=from_value,
                to=to_value,
                validatecommand=(setting["validate"], "%P", "%s", validate),
                textvariable=setting["tk_var"],
            )
        else:
            setting["second_tk_widget"] = ttk.Spinbox(
                setting["TkFinalSettingFrame"],
                width=width,
                increment=increment_value,
                from_=from_value,
                to=to_value,
                textvariable=setting["tk_var"],
            )

        setting["second_tk_widget"].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)

        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, "second_tk_widget")
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": setting["tk_var"],
            "decimal places": setting.get("decimal places"),
            "second_tk_widget": setting["second_tk_widget"]
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def spinbox(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        id_ = "TkSpinbox"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]
        from_value = setting.get("from")
        to_value = setting.get("to")
        increment = setting.get("increment")
        width = setting.get("width")
        validate = setting.get("validate")

        setting["tk_var"] = tk.StringVar(self)

        if validate:
            setting["validate"] = self.register(self.validate)
            setting[id_] = ttk.Spinbox(
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
            setting[id_] = ttk.Spinbox(
                setting["TkFinalSettingFrame"],
                from_=from_value,
                to=to_value,
                increment=increment,
                width=width,
                textvariable=setting["tk_var"],
            )

        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": setting["tk_var"],
        }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def color(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting) -> None:
        # chooseColor(colorToChange, buttonToModify)
        id_ = "TkColor"
        setting: BethiniSetting = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]

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

        setting[id_] = tk.Button(
            setting["TkFinalSettingFrame"],
            textvariable=setting["tk_var"],
            command=lambda: self.choose_color(setting[id_], color_value_type),
        )
        setting[id_].var = setting["tk_var"]
        setting[id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, the_label_frame, on_frame, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            "tk_var": setting["tk_var"],
            "colorValueType": color_value_type,
            "rgbType": setting.get("rgbType")
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def radio_preset_value(self, _each_setting) -> str:
        return self.preset_var.get()

    def checkbox_value(self, each_setting):
        setting_value = self.get_setting_values(
            self.setting_dictionary[each_setting].get("targetINIs"),
            self.setting_dictionary[each_setting].get("targetSections"),
            self.setting_dictionary[each_setting].get("settings"),
        )

        if setting_value and None not in setting_value:
            on_value = self.setting_dictionary[each_setting].get("onvalue")
            off_value = self.setting_dictionary[each_setting].get("offvalue")
            if setting_value == on_value:
                this_value = on_value
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            elif setting_value == off_value:
                this_value = off_value
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            else:
                this_value = []
                for n in range(len(setting_value)):
                    if setting_value[n] in on_value[n]:
                        this_value.append(1)
                    else:
                        this_value.append(0)

                this_value = on_value if all(this_value) else off_value
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            try:
                logger.debug(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]["valueSet"] = True
                return this_value
            except:
                logger.warning(f"No value set for checkbox {each_setting}.")
        return None

    def dropdown_value(self, each_setting):
        setting_value = self.get_setting_values(
            self.setting_dictionary[each_setting].get("targetINIs"),
            self.setting_dictionary[each_setting].get("targetSections"),
            self.setting_dictionary[each_setting].get("settings"),
            self.setting_dictionary[each_setting].get("settingChoices"),
            self.setting_dictionary[each_setting].get("delimiter"),
        )

        if setting_value and None not in setting_value:
            decimal_places = self.setting_dictionary[each_setting].get("decimal places")
            if decimal_places:
                decimal_places = int(decimal_places)
                this_value = round(float(setting_value[0]), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            else:
                file_format = self.setting_dictionary[each_setting].get("fileFormat")
                if file_format:
                    this_value = os.path.split(setting_value[0])
                    if file_format == "directory":
                        this_value = this_value[0]
                        if this_value and this_value[-1] != "\\":
                            this_value += "\\"
                    elif file_format == "file":
                        this_value = this_value[1]
                    self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                else:
                    setting_choices = self.setting_dictionary[each_setting].get("settingChoices")
                    if setting_choices and setting_value[0] not in setting_choices:
                        this_value = "Custom"
                        self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                    else:
                        this_value = setting_value[0]
                        self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            logger.debug(f"{each_setting} = {this_value}")
            self.setting_dictionary[each_setting]["valueSet"] = True
            return this_value
        return None

    def combobox_value(self, each_setting):
        setting_value = self.get_setting_values(
            self.setting_dictionary[each_setting].get("targetINIs"),
            self.setting_dictionary[each_setting].get("targetSections"),
            self.setting_dictionary[each_setting].get("settings"),
        )
        if setting_value and None not in setting_value:
            this_value = setting_value[0]

            decimal_places = self.setting_dictionary[each_setting].get("decimal places")
            if decimal_places:
                decimal_places = int(decimal_places)
                this_value = round(float(this_value), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)

            self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            logger.debug(f"{each_setting} = {this_value}")
            self.setting_dictionary[each_setting]["valueSet"] = True
            return this_value
        return None

    def entry_value(self, each_setting):
        setting_value = self.get_setting_values(
            self.setting_dictionary[each_setting].get("targetINIs"),
            self.setting_dictionary[each_setting].get("targetSections"),
            self.setting_dictionary[each_setting].get("settings"),
        )
        if setting_value and None not in setting_value:
            formula = self.setting_dictionary[each_setting].get("formula")
            file_format = self.setting_dictionary[each_setting].get("fileFormat")
            if formula:
                decimal_places = int(self.setting_dictionary[each_setting].get("decimal places"))
                this_value = round(simple_eval(formula.format(setting_value[0])), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)
            elif file_format:
                this_value = setting_value[0]
                if file_format == "file":
                    this_value = os.path.split(this_value)
                    this_value = this_value[1]
            else:
                this_value = setting_value[0]
            try:
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                logger.debug(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]["valueSet"] = True
                return this_value
            except:
                logger.warning(f"No value set for entry {each_setting}.")
        return None

    def slider_value(self, each_setting):
        setting_value = self.get_setting_values(
            self.setting_dictionary[each_setting].get("targetINIs"),
            self.setting_dictionary[each_setting].get("targetSections"),
            self.setting_dictionary[each_setting].get("settings"),
        )

        if setting_value and None not in setting_value:
            this_value = setting_value[0]

            decimal_places = self.setting_dictionary[each_setting].get("decimal places")
            if decimal_places:
                decimal_places = int(decimal_places)
                this_value = round(float(this_value), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)

            try:
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                logger.debug(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]["valueSet"] = True
                return this_value
            except:
                logger.warning(f"no value set for slider {each_setting}")
        return None

    def spinbox_value(self, each_setting):
        setting_value = self.get_setting_values(
            self.setting_dictionary[each_setting].get("targetINIs"),
            self.setting_dictionary[each_setting].get("targetSections"),
            self.setting_dictionary[each_setting].get("settings"),
        )
        if setting_value and None not in setting_value:
            this_value = setting_value[0]
            try:
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                logger.debug(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]["valueSet"] = True
                return this_value
            except:
                logger.warning(f"no value set for spinbox {each_setting}")
        return None

    def color_value(self, each_setting):
        setting_value = self.get_setting_values(
            self.setting_dictionary[each_setting].get("targetINIs"),
            self.setting_dictionary[each_setting].get("targetSections"),
            self.setting_dictionary[each_setting].get("settings"),
        )

        this_value = None
        new_color = None
        if setting_value and None not in setting_value:
            color_value_type = self.setting_dictionary[each_setting].get("colorValueType")
            if color_value_type == "hex":
                this_value = setting_value[0]
                new_color = this_value
            elif color_value_type == "decimal":
                this_value = setting_value[0]
                # Convert decimal value to hex
                new_color = rgb_to_hex(decimal_to_rgb(setting_value[0]))
            elif color_value_type == "rgb":
                rgb_type = self.setting_dictionary[each_setting].get("rgbType")
                if rgb_type == "multiple settings":
                    this_value = tuple(int(i) for i in setting_value)
                    new_color = rgb_to_hex(this_value)
                    this_value = str(this_value)
                else:
                    this_value = "("
                    for n in range(len(setting_value)):
                        this_value += setting_value[n]
                    this_value += ")"
                    new_color = rgb_to_hex(ast.literal_eval(this_value))
            elif color_value_type == "rgba":
                rgb_type = self.setting_dictionary[each_setting].get("rgbType")
                if rgb_type == "multiple settings":
                    this_value = tuple(int(i) for i in setting_value)
                    new_color = rgb_to_hex(this_value[0:3])
                    this_value = str(this_value)
                else:
                    this_value = "("
                    for n in range(len(setting_value)):
                        this_value += setting_value[n]
                    this_value += ")"
                    new_color = rgb_to_hex(ast.literal_eval(this_value)[0:3])
            elif color_value_type == "rgb 1":
                rgb_type = self.setting_dictionary[each_setting].get("rgbType")
                if rgb_type == "multiple settings":
                    this_value = tuple(round(float(i),4) for i in setting_value)
                    new_color = rgb_to_hex(tuple(int(float(i)*255) for i in setting_value))
                    this_value = str(this_value)

            if this_value is not None and new_color is not None:
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                tk_widget = self.setting_dictionary[each_setting].get("tk_widget")
                rgb = hex_to_rgb(new_color)
                luminance = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
                the_text_color = "#FFFFFF" if luminance < 128 else "#000000"
                tk_widget.configure(bg=new_color, activebackground=new_color, fg=the_text_color)
                logger.debug(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]["valueSet"] = True
        return this_value

    def check_dependents(self, each_setting) -> None:
        for each_dependent_setting in self.settings_that_settings_depend_on[each_setting]:
            var = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get("var")

            the_operator = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get("theOperator")
            value = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get("value")
            current_value = self.widget_type_switcher(each_setting)
            second_tk_widget = self.setting_dictionary[each_dependent_setting].get("second_tk_widget")
            if var == "float":
                value = float(value)
                current_value = float(current_value)
            if the_operator(current_value, value):
                self.setting_dictionary[each_dependent_setting]["tk_widget"].configure(state=tk.NORMAL)
                if second_tk_widget:
                    second_tk_widget.configure(state=tk.NORMAL)
            else:
                set_to_off = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get("setToOff")
                if set_to_off:
                    off_value = self.setting_dictionary[each_dependent_setting].get("offvalue")

                    self.setting_dictionary[each_dependent_setting]["tk_var"].set(off_value)
                self.setting_dictionary[each_dependent_setting]["tk_widget"].configure(state=tk.DISABLED)
                if second_tk_widget:
                    second_tk_widget.configure(state=tk.DISABLED)

    def assign_value(self, each_setting) -> None:
        id_ = self.setting_dictionary[each_setting].get("id")
        func = self.widget_type_assign_value.get(id_)
        if func is not None:
            func(each_setting)

        if each_setting in list(self.settings_that_settings_depend_on.keys()):
            self.check_dependents(each_setting)

    def checkbox_assign_value(self, each_setting: str) -> None:
        setting = self.setting_dictionary[each_setting]
        this_value = setting["tk_var"].get()
        # this_value is whatever the state of the on_value/off_value is... not a simple boolean


        targetINIs = self.setting_dictionary[each_setting].get("targetINIs")
        targetSections = self.setting_dictionary[each_setting].get("targetSections")
        theSettings = self.setting_dictionary[each_setting].get("settings")

        on_value = self.setting_dictionary[each_setting].get("onvalue")
        off_value = self.setting_dictionary[each_setting].get("offvalue")

        setting_value = self.get_setting_values(targetINIs, targetSections, theSettings)

        try:
            this_value = list(ast.literal_eval(this_value))
            for n in range(len(this_value)):
                if type(this_value[n]) is tuple:
                    this_value[n] = list(this_value[n])
        except Exception as e:
            self.sme(f"{this_value} .... Make sure that the {each_setting} checkbutton Onvalue and Offvalue are lists within lists in the json.", exception=e)

        if targetINIs:
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(ini_location, targetINIs[n])
                # 1
                if this_value in (on_value, off_value):
                    if type(this_value[n]) is list:
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
                                self.sme(f"Failed to assign {targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue} because the {targetINIs[n]} has an issue.", exception=e)

                        the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                        self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}")
                    else:
                        the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value[n])
                        self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value[n]}")

    def dropdown_assign_value(self, each_setting: str) -> None:
        tk_var = self.setting_dictionary[each_setting].get("tk_var")
        this_value = tk_var.get()
        targetINIs = self.setting_dictionary[each_setting].get("targetINIs")
        targetSections = self.setting_dictionary[each_setting].get("targetSections")
        theSettings = self.setting_dictionary[each_setting].get("settings")

        setting_choices = self.setting_dictionary[each_setting].get("settingChoices")
        delimiter = self.setting_dictionary[each_setting].get("delimiter")
        file_format = self.setting_dictionary[each_setting].get("fileFormat")
        # decimal_places = self.setting_dictionary[each_setting].get("decimal places")
        partial = self.setting_dictionary[each_setting].get("partial")
        theValueStr = ""
        if partial:
            for each_partial_setting in partial:
                if each_partial_setting == each_setting:
                    theValueStr += "{}"
                else:
                    try:
                        if self.setting_dictionary[each_partial_setting]["valueSet"]:
                            theValueStr += self.setting_dictionary[each_partial_setting]["tk_var"].get()
                        else:
                            self.sme(f"{each_partial_setting} is not set yet.")
                            return
                    except Exception as e:
                        self.sme(f"{each_partial_setting} is not set yet.", exception=e)
                        return


        if targetINIs:
            for n in range(len(targetINIs)):
                theValue = ""
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(ini_location, targetINIs[n])
                # 1280x720
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

    def combobox_assign_value(self, each_setting) -> None:
        targetINIs = self.setting_dictionary[each_setting].get("targetINIs")

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get("tk_var")
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get("targetSections")
            theSettings = self.setting_dictionary[each_setting].get("settings")

            decimal_places = self.setting_dictionary[each_setting].get("decimal places")
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(ini_location, targetINIs[n])

                if decimal_places and this_value:
                    this_value = round(float(this_value),int(decimal_places))
                    if decimal_places == "0":
                        this_value = int(this_value)
                    this_value = str(this_value)

                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")

    def entry_assign_value(self, each_setting) -> None:
        targetINIs = self.setting_dictionary[each_setting].get("targetINIs")

        partial = self.setting_dictionary[each_setting].get("partial")
        theValueStr = ""
        if partial:
            for each_partial_setting in partial:
                if each_partial_setting == each_setting:
                    theValueStr += "{}"
                elif self.setting_dictionary[each_partial_setting]["valueSet"]:
                    theValueStr += self.setting_dictionary[each_partial_setting]["tk_var"].get()
                else:
                    return

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get("tk_var")
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get("targetSections")
            theSettings = self.setting_dictionary[each_setting].get("settings")

            formula = self.setting_dictionary[each_setting].get("formula")

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(ini_location, targetINIs[n])

                if formula:
                    formulaValue = formula.format(this_value)
                    try:
                        this_value = str(round(simple_eval(formulaValue),8))
                    except:
                        self.sme(f"Failed to evaluate formula value for {this_value}.")

                if partial:
                    this_value = theValueStr.format(this_value)
                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")

    def slider_assign_value(self, each_setting) -> None:
        targetINIs = self.setting_dictionary[each_setting].get("targetINIs")

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get("tk_var")
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get("targetSections")
            theSettings = self.setting_dictionary[each_setting].get("settings")

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(ini_location, targetINIs[n])

                try:
                    the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                    self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")
                except AttributeError as e:
                    self.sme(f"Failed to set {targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value} because the {targetINIs[n]} has an issue.", exception=e)

    def spinbox_assign_value(self, each_setting) -> None:
        targetINIs = self.setting_dictionary[each_setting].get("targetINIs")

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get("tk_var")
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get("targetSections")
            theSettings = self.setting_dictionary[each_setting].get("settings")

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(ini_location, targetINIs[n])

                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")

    def color_assign_value(self, each_setting) -> None:
        targetINIs = self.setting_dictionary[each_setting].get("targetINIs")

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get("tk_var")
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get("targetSections")
            theSettings = self.setting_dictionary[each_setting].get("settings")

            color_value_type = self.setting_dictionary[each_setting].get("colorValueType")
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(ini_location, targetINIs[n])

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

    def createTabs(self, *, from_choose_game_window: bool=False) -> None:
        # Preview Window
        global PREVIEW_WINDOW
        PREVIEW_WINDOW = ttk.Toplevel("Preview")
        global PREVIEW_FRAME
        PREVIEW_FRAME = ttk.Frame(PREVIEW_WINDOW)
        PREVIEW_FRAME.pack(padx=5, pady=5)
        preview_close_button = ttk.Button(PREVIEW_WINDOW, text="Close", command=PREVIEW_WINDOW.withdraw)
        preview_close_button.pack(anchor=tk.SE, padx=5, pady=5)
        PREVIEW_WINDOW.protocol("WM_DELETE_WINDOW", PREVIEW_WINDOW.withdraw)
        PREVIEW_WINDOW.withdraw()

        for each_tab in self.tab_dictionary:
            # each_tab is Page1, Page2, etc.
            # self.tab_dictionary[each_tab]["Name"] is the name of each tab

            self.create_tab_image(each_tab)
            if self.tab_dictionary[each_tab]["Name"] == "Setup":
                global SETUP_WINDOW
                self.tab_dictionary[each_tab]["SetupWindow"] = ttk.Toplevel("Setup")
                SETUP_WINDOW = self.tab_dictionary[each_tab]["SetupWindow"]
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(SETUP_WINDOW)
                self.tab_dictionary[each_tab]["TkFrameForTab"].pack()

                setup_ok_button = ttk.Button(SETUP_WINDOW, text="OK", command=self.withdraw_setup)
                setup_ok_button.pack(anchor=tk.SE, padx=5, pady=5)

                SETUP_WINDOW.protocol("WM_DELETE_WINDOW", self.withdraw_setup)
                if not from_choose_game_window:
                    SETUP_WINDOW.withdraw()
            elif self.tab_dictionary[each_tab]["Name"] == "Preferences":
                global preferencesWindow
                self.tab_dictionary[each_tab]["PreferencesWindow"] = ttk.Toplevel("Preferences")
                preferencesWindow = self.tab_dictionary[each_tab]["PreferencesWindow"]
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(preferencesWindow)
                self.tab_dictionary[each_tab]["TkFrameForTab"].pack()

                preferences_ok_button = ttk.Button(preferencesWindow, text="OK", command=preferencesWindow.withdraw)
                preferences_ok_button.pack(anchor=tk.SE, padx=5, pady=5)
                preferencesWindow.minsize(300, 100)

                preferencesWindow.protocol("WM_DELETE_WINDOW", preferencesWindow.withdraw)
                preferencesWindow.withdraw()

            else:
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(self.sub_container)
                self.sub_container.add(self.tab_dictionary[each_tab]["TkFrameForTab"], text=self.tab_dictionary[each_tab]["Name"], image=self.tab_dictionary[each_tab]["TkPhotoImageForTab"], compound=tk.LEFT)

            self.label_frames_for_tab(each_tab)

        self.stop_progress()
        if not from_choose_game_window:
            self.updateValues()
        self.start_progress()
        self.bindTkVars()

        self.sub_container.pack(fill=tk.BOTH, expand=True)
        self.stop_progress()
        self.sme("Loading complete.")

    def bindTkVars(self) -> None:
        for each_setting in self.setting_dictionary:
            tk_var = self.setting_dictionary[each_setting].get("tk_var")
            if tk_var:
                self.setting_dictionary[each_setting]["tk_var"].trace_add("write", lambda _var, _index, _mode, each_setting=each_setting:self.assign_value(each_setting))
            forceSelect = self.setting_dictionary[each_setting].get("forceSelect")
            if forceSelect:
                self.assign_value(each_setting)

    def updateValues(self) -> None:
        self.start_progress()
        self.sme("Updating INI values.")
        for each_setting in self.setting_dictionary:
            self.widget_type_switcher(each_setting)
        self.sme("Checking for dependent settings.")
        self.dependents()
        self.sme("Update values complete.")
        self.stop_progress()

    def dependents(self) -> None:
        for each_setting in self.dependent_settings_dictionary:
            for masterSetting in self.dependent_settings_dictionary[each_setting]:

                the_operator = self.dependent_settings_dictionary[each_setting][masterSetting].get("operator")
                set_to_off = self.dependent_settings_dictionary[each_setting][masterSetting].get("setToOff", False)
                if the_operator in {"equal", "not-equal"}:
                    value = self.dependent_settings_dictionary[each_setting][masterSetting].get("value")
                    current_value = self.widget_type_switcher(masterSetting)
                    var = "string"
                else:
                    value = float(self.dependent_settings_dictionary[each_setting][masterSetting].get("value"))
                    current_value = float(self.widget_type_switcher(masterSetting))
                    var = "float"
                the_operator = operator_dictionary[the_operator]
                second_tk_widget = self.setting_dictionary[each_setting].get("second_tk_widget")
                if the_operator(current_value, value):
                    self.setting_dictionary[each_setting]["tk_widget"].configure(state=tk.NORMAL)
                    if second_tk_widget:
                        second_tk_widget.configure(state=tk.NORMAL)
                else:
                    if set_to_off:
                        off_value = self.dependent_settings_dictionary[each_setting][masterSetting].get("offvalue")
                        self.setting_dictionary[each_setting]["tk_var"].set(off_value)
                    self.setting_dictionary[each_setting]["tk_widget"].configure(state=tk.DISABLED)
                    if second_tk_widget:
                        second_tk_widget.configure(state=tk.DISABLED)

                if not self.settings_that_settings_depend_on.get(masterSetting):
                    self.settings_that_settings_depend_on[masterSetting] = {}

                self.settings_that_settings_depend_on[masterSetting][each_setting] = {
                    "theOperator": operator_dictionary[self.dependent_settings_dictionary[each_setting][masterSetting].get("operator")],
                    "value": value,
                    "var": var,
                    "setToOff": set_to_off
                    }

    def validate(self, valueChangedTo: str, _valueWas: str, validate: Literal["integer", "whole", "counting", "float"]) -> bool:
        try:
            if validate == "integer":
                if not valueChangedTo or str(abs(int(valueChangedTo))).isdigit():
                    return True

            elif validate == "float" and (not valueChangedTo or isinstance(float(valueChangedTo), float)):
                return True

            elif validate == "whole":
                if not valueChangedTo or valueChangedTo.isdigit():
                    return True

            elif validate == "counting" and valueChangedTo != "0" and (not valueChangedTo or valueChangedTo.isdigit()):
                return True

        except ValueError:
            pass

        self.sme(f"'{valueChangedTo}' is an invalid value for this option.")
        return False

    @staticmethod
    def getINILocation(ini_name: str):
        ini_location = APP.inis(ini_name)
        return app_config.get_value("Directories", ini_location) if ini_location else ""

    def get_setting_values(self, targetINIs, targetSections, theSettings, setting_choices=None, delimiter=None):
        """Return the current values of a setting from the given INIs."""

        settingValues = []
        if targetINIs:
            ININumber = -1
            for INI in targetINIs:
                ININumber += 1
                # Get the Bethini.ini key for the location of the target INI
                ini_location = self.getINILocation(INI)
                if ini_location is not None:
                    # If the INI location is known.

                    currentSetting = theSettings[ININumber]
                    currentSection = targetSections[ININumber]

                    # This looks for a default value in the settings.json
                    defaultValue = None if my_app_config == INI else APP.setting_values[currentSetting]["default"]

                    target_ini = open_ini(str(ini_location), str(INI))
                    try:
                        value = str(target_ini.get_value(currentSection, currentSetting, default=defaultValue))
                    except AttributeError as e:
                        self.sme(f"There was a problem with the existing {target_ini} [{currentSection}] {currentSetting}, so {defaultValue} will be used.", exception=e)
                        value = defaultValue
                    settingValues.append(value)
            if settingValues != []:
                # Check to see if the settings correspond with specified each_setting choices.
                if setting_choices:
                    for choice in setting_choices:
                        if setting_choices[choice] == settingValues:
                            settingValues = [choice]

                # Check to see if there are multiple values separated by a delimiter
                if delimiter:
                    delimitedValue = ""
                    for n in range(len(settingValues)):
                        if n != len(settingValues) - 1:
                            delimitedValue += settingValues[n] + delimiter
                        else:
                            delimitedValue += settingValues[n]
                    settingValues = [delimitedValue]

        return settingValues

def on_closing(root: bethini_app) -> None:
    """Ask if the user wants to save INI files if any have been modified before quitting.

    This is bound to the main app window closing.
    """

    if messagebox.askyesno("Quit?", "Do you want to quit?"):
        if app_config.has_been_modified:
            app_config.save_ini_file(sort=True)
        root.save_ini_files()
        root.quit()

def remove_excess_directory_files(directory: Path, max_to_keep: int, files_to_remove: list[str]) -> bool:
    """Remove excess logs or backups.

    directory: The directory to remove files from.
    max_to_keep: The maximum amount of directories that will be excluded from removal.
    files_to_remove: List of files that will be removed.
    """

    try:
        subdirectories = [d for d in directory.iterdir() if d.name.lower() != "first-time-backup" and d.is_dir()]
    except OSError as e:
        logger.debug(f"Info: {directory} : {e.strerror}")
        return True
    subdirectories.sort(key=lambda d: d.name)

    if max_to_keep > -1:
        for n in range(len(subdirectories)):
            dir_path = subdirectories[n]
            if n < max_to_keep:
                logger.debug(f"{subdirectories[n]} will be kept.")
            else:
                file_delete_failed = False
                for file in files_to_remove:
                    file_path = dir_path / file
                    try:
                        file_path.unlink(missing_ok=True)
                    except OSError as e:
                        logger.error(f"{file_path}: {e.strerror}")
                        file_delete_failed = True

                if not file_delete_failed:
                    try:
                        dir_path.rmdir()
                    except OSError as e:
                        logger.error(f"{dir_path} : {e.strerror}")
                    else:
                        logger.debug(f"{dir_path} was removed.")
    return False

def open_ini(location: str, ini: str):
    """Open the INI with the given location and name and store it in open_inis."""

    open_ini = open_inis.get(ini)
    if open_ini:
        open_ini_location = open_inis[ini]["located"]
        open_ini_id = 0
        for each_location in open_ini_location:
            open_ini_id += 1
            if open_ini_location[each_location]["at"] == location:
                return open_ini_location[each_location].get("object")

        # If the location is not found, add it
        open_ini_id += 1
        open_ini_id_str = str(open_ini_id)
        open_inis[ini]["located"][open_ini_id_str] = {
            "at":location
            }
        open_inis[ini]["located"][open_ini_id_str]["object"] = ModifyINI(Path(location) / ini)
        return open_inis[ini]["located"][open_ini_id_str]["object"]

    # If the ini has not been opened before
    open_ini_id_str = "1"
    open_inis[ini] = {
        "located": {
            open_ini_id_str: {
                "at": location
                }
            }
        }
    try:
        open_inis[ini]["located"][open_ini_id_str]["object"] = ModifyINI(Path(location) / ini)
    except configparser.MissingSectionHeaderError:
        logger.error(f"Failed to open ini: {ini}", exc_info=True)
    return open_inis[ini]["located"][open_ini_id_str]["object"]

if __name__ == "__main__":

    # Get app config settings.
    my_app_config = f"{my_app_short_name}.ini"
    app_config = ModifyINI(my_app_config)
    iMaxLogs = app_config.get_value("General", "iMaxLogs", "5")
    app_config.assign_setting_value("General", "iMaxLogs", iMaxLogs)
    app_config.assign_setting_value("General", "iMaxBackups", app_config.get_value("General", "iMaxBackups", "5"))

    # Theme
    theme = app_config.get_value("General", "sTheme", default="superhero")
    if theme not in standThemes.STANDARD_THEMES:
        theme="superhero"
    app_config.assign_setting_value("General", "sTheme", theme)

    # Remove excess log files.
    remove_excess_directory_files(Path.cwd() / "logs", int(iMaxLogs), ["log.log"])

    # Initialize open_inis dictionary to store list of opened INI files in.
    open_inis = {
        my_app_config: {
            "located": {
                "1": {
                    "at": "",
                    "object": app_config
                }
            }
        }
    }

    # Get version
    try:
        with Path("changelog.txt").open(encoding="utf-8") as changelog:
            version = changelog.readline().replace("\n","")
    except FileNotFoundError:
        version = ""

    # Start the app class

    window = bethini_app(themename=theme, iconphoto=Path("Icons/Icon.png"), minsize=(400, 200))
    window.choose_game()

    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()
