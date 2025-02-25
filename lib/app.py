#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import json
import sys
import tkinter as tk
from pathlib import Path
from typing import Literal, cast

from lib.type_helpers import PackSettings

if __name__ == "__main__":
    sys.exit(1)

from lib.type_helpers import *


class AppName:
    """This class handles the different apps/games supported, which are placed in the apps folder."""

    def __init__(self, appname: str) -> None:
        with (Path.cwd() / "apps" / appname / "settings.json").open(encoding="utf-8") as app_json:
            self.data: AppSettingsJSON = json.load(app_json)
        with (Path.cwd() / "apps" / appname / "Bethini.json").open(encoding="utf-8") as bethini:
            self.bethini: AppBethiniJSON = json.load(bethini)

        self.default_ini = list(self.bethini["INIs"])[1] if len(self.bethini["INIs"]) > 1 else None

        self.setting_values = self.get_setting_values()

        self.ini_section_setting_dict = self.get_ini_section_setting_dict()

    def what_ini_files_are_used(self) -> list[str]:
        """Returns a list of INI files used, with Bethini.ini removed from the list."""

        return [ini for ini in self.bethini["INIs"] if ini != "Bethini.ini"]

    def inis(self, ini: str) -> str | Literal[""]:
        """Returns the INI settings name used in Bethini.ini to store the location
        of the given ini file.
        """

        return self.bethini["INIs"].get(ini, "") if ini else ""

    def get_setting_values(self) -> dict[str, dict[str, int | float | str]]:
        """Returns a dictionary listing all the different value types for every setting."""

        setting_values: dict[str, dict[str, int | float | str]] = {}
        for ini_setting in self.data["iniValues"]:
            setting_values[ini_setting["name"]] = {}
            for value_type in self.bethini["valueTypes"]:
                try:
                    the_value_for_this_type = ini_setting["value"][value_type]
                    setting_values[ini_setting["name"]][value_type] = the_value_for_this_type
                except KeyError:
                    continue
        return setting_values

    def get_ini_section_setting_dict(self) -> dict[str, dict[str, list[str]]]:
        """Returns a dictionary listing all the INI files with their
        sections and settings as specified in settings.json
        """

        ini_section_setting_dict: dict[str, dict[str, list[str]]] = {}
        for ini_setting in self.data["iniValues"]:
            ini = ini_setting.get("ini", self.default_ini)
            if ini is None:
                raise TypeError
            section = ini_setting["section"].lower()
            setting = ini_setting["name"].lower()
            if ini not in ini_section_setting_dict:
                ini_section_setting_dict[ini] = {
                    section: [setting],
                }
            elif section not in ini_section_setting_dict[ini]:
                ini_section_setting_dict[ini][section] = [setting]
            else:
                ini_section_setting_dict[ini][section].append(setting)

        return ini_section_setting_dict

    def does_setting_exist(self, ini: str, section: str, setting: str) -> bool:
        """Checks if the given setting for the given section and ini file exists in settings.json."""

        section = section.lower()
        setting = setting.lower()
        has_section = section in self.ini_section_setting_dict[ini]
        return has_section and setting in self.ini_section_setting_dict[ini][section]

    def preset_values(self, preset: str) -> GameSettingInfo:
        """Returns a dictionary listing all the settings and values
        for a given preset specified in settings.json.
        """

        preset_dict: GameSettingInfo = {}
        for ini_setting in self.data["iniValues"]:
            preset_value = ini_setting["value"].get(preset)
            if preset_value is not None:
                # If a preset value was specified
                ini = ini_setting.get("ini", self.default_ini)
                if ini is None:
                    raise TypeError
                preset_dict[f"{ini_setting['name']}:{ini_setting['section']}"] = {
                    "ini": ini,
                    "section": ini_setting["section"],
                    "value": str(preset_value),
                }
        return preset_dict

    def can_remove(self) -> GameSettingInfo:
        """Returns a dictionary listing all the settings and default values
        NOT containing the alwaysPrint attribute as specified in settings.json.
        """

        can_remove: GameSettingInfo = {}
        for ini_setting in self.data["iniValues"]:
            if not ini_setting.get("alwaysPrint"):
                ini = ini_setting.get("ini", self.default_ini)
                if ini is None:
                    raise TypeError

                the_value = ini_setting["value"].get("default")

                can_remove[f"{ini_setting['name']}:{ini_setting['section']}"] = {
                    "ini": ini,
                    "section": ini_setting["section"],
                    "value": str(the_value),
                }
        return can_remove

    def pack_settings(self, tab_name: str, label_frame_name: str) -> PackSettings:
        """Returns the pack settings for the label frame."""

        default_pack_settings: PackSettings = {
            "Side": tk.TOP,
            "Anchor": tk.NW,
            "Fill": tk.BOTH,
            "Expand": 1,
        }
        return cast("PackSettings", self.bethini["displayTabs"][tab_name][label_frame_name].get("Pack", default_pack_settings))

    def number_of_vertically_stacked_settings(self, tab_name: str, label_frame_name: str) -> IntStr:
        """Returns the maximum number of vertically stacked settings desired for the label frame."""

        return cast("IntStr", self.bethini["displayTabs"][tab_name][label_frame_name]["NumberOfVerticallyStackedSettings"])
