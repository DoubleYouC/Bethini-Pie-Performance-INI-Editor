#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import tkinter as tk
from typing import TYPE_CHECKING, Any, Literal, NotRequired, TypeAlias, TypedDict

import ttkbootstrap as ttk

if TYPE_CHECKING:
    from collections.abc import Callable

    from lib.scalar import Scalar

ININame: TypeAlias = Literal[
    "Bethini.ini",
    "Fallout4.ini",
    "Fallout4Prefs.ini",
    # "Fallout4Custom.ini",
    "Fallout.ini",
    "FalloutPrefs.ini",
    # "FalloutCustom.ini",
    "Skyrim.ini",
    "SkyrimPrefs.ini",
    # "SkyrimCustom.ini",
    "StarfieldCustom.ini",
    "StarfieldPrefs.ini",
    "Ultra.ini",
]

IntStr: TypeAlias = str
"""A string representing an integer."""

FloatStr: TypeAlias = str
"""A string representing an float."""

ValidationType: TypeAlias = Literal["integer", "whole", "counting", "float"]

Browse: TypeAlias = tuple[Literal["directory"], Literal["directory"] | str, Literal["directory", "file"]]

ColorType: TypeAlias = Literal["rgb", "rgb 1", "rgba", "decimal", "hex"]
ColorValue: TypeAlias = str | tuple[int, ...]

TabId: TypeAlias = str
"""A string in the format Page1, Page2, etc."""

SettingId: TypeAlias = str
"""A string in the format Setting1, Setting2, etc."""

SettingFrameId: TypeAlias = str
"""A string in the format SettingFrame1, SettingFrame2, etc."""

LabelFrameId: TypeAlias = str
"""A string in the format LabelFrame1, LabelFrame2, etc."""

ValueType: TypeAlias = Literal["boolean", "float", "number", "string"]

ValueList: TypeAlias = list[list[Literal[""] | IntStr | FloatStr | str]]

TkAnchor: TypeAlias = Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]
TkFill: TypeAlias = Literal["none", "x", "y", "both"]
TkSide: TypeAlias = Literal["left", "right", "top", "bottom"]

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

WidgetId: TypeAlias = Literal[
    "second_tk_widget",
    "TkCheckbutton",
    "TkColor",
    "TkCombobox",
    "TkEntry",
    "TkOptionMenu",
    "TkPresetButton",
    "TkRadioPreset",
    "TkSlider",
    "TkSpinbox",
]


class GameSetting(TypedDict):
    ini: ININame | None
    section: str
    value: str


class GameSettingInfo(TypedDict, total=False):
    alwaysPrint: bool
    ini: ININame | None
    name: str
    section: str
    type: ValueType
    value: dict[Literal["default", "recommended"] | str, int | float | str]


class DependentSetting(TypedDict, total=False):
    operator: Literal["greater-than", "greater-or-equal-than", "less-than", "less-or-equal-than", "not-equal", "equal"]
    operator_func: "Callable[[Any], Any] | None"
    value: str | list[list[str]] | float

    var: Literal["string", "float"]
    setToOff: bool

    Offvalue: ValueList | None
    Onvalue: ValueList | None


class BethiniSetting(
    TypedDict(
        "BethiniSetting",
        {
            "decimal places": NotRequired[IntStr | None],
            "from": NotRequired[IntStr],
            "preset id": NotRequired[str],
        },
    ),
    total=False,
):
    """Type annotations for setting dictionary values.

    :Usage:
    setting: Setting = self.tab_dictionary[tab_id]["LabelFrames"][label_frame_id]["SettingFrames"][frame_id][setting_id]
    """

    browse: Browse
    choices: str | list[Literal["Browse...", "Manual..."] | str]
    colorValueType: ColorType
    custom_function: str
    customWidth: IntStr
    delimiter: Literal["x"] | None
    dependentSettings: dict[str, DependentSetting]
    entry_width: IntStr
    fileFormat: Literal["directory", "file"] | None
    forceSelect: IntStr | None
    formula: str | None
    increment: IntStr
    label_frame_id: LabelFrameId
    label_frame_name: str
    length: IntStr
    Name: str
    Offvalue: ValueList
    Onvalue: ValueList
    partial: list[str] | None
    rgbType: Literal["multiple settings"] | None
    second_tk_widget: ttk.Spinbox | None
    setting_frame_id: SettingFrameId
    setting_id: SettingId
    settingChoices: dict[str, list[str]] | None
    settings: list[str]
    tab_id: TabId
    targetINIs: list[ININame]
    targetSections: list[str]
    tk_var: tk.StringVar
    tk_widget: "ttk.Checkbutton | tk.Button | ttk.Button | ttk.Combobox | ttk.Entry | ttk.OptionMenu | ttk.Radiobutton | Scalar | ttk.Spinbox"
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
    valueSet: bool
    widget_id: WidgetId
    width: IntStr


class PackSettings(TypedDict):
    Anchor: TkAnchor
    Expand: Literal[0, 1] | bool
    Fill: TkFill
    Side: TkSide


class SettingsLabelFrame(TypedDict, total=False):
    Name: str
    NumberOfVerticallyStackedSettings: IntStr
    Pack: PackSettings
    Settings: dict[SettingId, BethiniSetting]
    SettingFrames: dict[SettingFrameId, dict[SettingId, BethiniSetting]]
    TkLabelFrame: ttk.Labelframe | ttk.Frame


class DisplayTab(TypedDict, total=False):
    Name: (
        Literal[
            "Setup",
            "Preferences",
            "Basic",
            "General",
            "Gameplay",
            "Interface",
            "Environment",
            "Shadows",
            "Visuals",
            "View Distance",
        ]
        | str
    )
    SetupWindow: tk.BaseWidget
    TkFrameForTab: ttk.Frame
    TkPhotoImageForTab: tk.PhotoImage
    LabelFrames: dict[LabelFrameId, SettingsLabelFrame]
    PreferencesWindow: ttk.Toplevel
    NoLabelFrame: SettingsLabelFrame


class AppBethiniJSON(TypedDict):
    customFunctions: dict[str, str]
    Default: Literal[""]
    displayTabs: dict[str, DisplayTab]
    INIs: dict[ININame, str]
    presetsIgnoreTheseSettings: list[str]
    valueTypes: list[
        Literal[
            "default",
            "fixedDefault",
            "Vanilla Low",
            "Vanilla Medium",
            "Vanilla High",
            "Vanilla Ultra",
            "Bethini Poor",
            "Bethini Low",
            "Bethini Medium",
            "Bethini High",
            "Bethini Ultra",
        ]
    ]


class AppSettingsJSON(TypedDict):
    gameId: str
    gameName: str
    iniPaths: list[str]
    iniValues: list[GameSettingInfo]
    presetPaths: list[str]
