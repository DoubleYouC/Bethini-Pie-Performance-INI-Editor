#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import tkinter as tk
from typing import TYPE_CHECKING, Literal, NotRequired, TypeAlias, TypedDict

import ttkbootstrap as ttk

from lib.ModifyINI import ModifyINI

if TYPE_CHECKING:
    from lib.scalar import Scalar


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
        "BethiniSetting",
        {
            "decimal places": NotRequired[IntStr],
            "from": NotRequired[IntStr],
            "preset id": NotRequired[str],
        },
    ),
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


class Located(TypedDict):
    at: str
    object: ModifyINI


class OpenINI(TypedDict):
    located: dict[str, Located]
