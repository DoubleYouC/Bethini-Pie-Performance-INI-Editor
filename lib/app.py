#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import logging
import json
import sys
import tkinter as tk
from pathlib import Path
from typing import cast

if __name__ == "__main__":
    sys.exit(1)

from lib.ModifyINI import ModifyINI
from lib.type_helpers import *

logger = logging.getLogger(__name__)


class AppName:
    """This class handles the different apps/games supported, which are placed in the apps folder."""

    def __init__(self, appname: str, exedir: Path) -> None:
        with (exedir / "apps" / appname / "settings.json").open(encoding="utf-8") as app_json:
            self.data: AppSettingsJSON = json.load(app_json)
        with (exedir / "apps" / appname / "Bethini.json").open(encoding="utf-8") as bethini:
            self.bethini: AppBethiniJSON = json.load(bethini)

        self.appname = appname
        self.exedir = exedir
        self.default_ini: ININame = list(self.bethini["INIs"])[1]
        self.setting_values = self.get_setting_values()
        self.ini_section_setting_dict = self.get_ini_section_setting_dict()
        self.setting_type_dict = self.get_setting_type_dict()
        self.setting_notes_dict = self.get_setting_notes_dict()
        self.can_remove_dict = self.can_remove()
        self.preset_values_default = self.preset_values("default")
        self.preset_values_fixedDefault = self.preset_values("fixedDefault")
        self.preset_values_recommended = self.preset_values("recommended")
        self.valid_inis = cast("list[str]", self.bethini["INI_pecking_order"].keys())

    def what_ini_files_are_used(self) -> list[ININame]:
        """Returns a list of INI files used, with Bethini.ini removed from the list."""

        return [ini for ini in self.bethini["INIs"] if ini != "Bethini.ini"]

    def get_winning_ini_for_setting(self, ini: str, section:str, setting: str) -> str:
        """An application sometimes has the ability to read multiple ini files in a particular
        order of priority in which a setting can be overridden. We call this the INI_pecking_order.
        Defining the ini for the setting in settings.json, we place a dictionary in Bethini.json,
        from which we define the INI_pecking_order for that setting. This function iterates over
        those ini files and returns the current ini that is providing the value for the setting.
        """
        # If Bethini.ini
        if ini == ModifyINI.app_config_name:
            return ini
        test_inis = self.bethini["INI_pecking_order"].get(ini)
        # If not a key in the INI_pecking_order
        if not test_inis:
            return ini
        for test_ini in reversed(test_inis):
            # If test_ini is ini, then ini is the winning ini
            if test_ini == ini:
                return ini
            ini_location_setting = self.get_ini_setting_name(test_ini)
            if not ini_location_setting:
                msg = f"Unknown INI: {test_ini}\nini_location_setting: {ini_location_setting}"
                logger.error(msg)
                raise NotImplementedError(msg)
            ini_location = ModifyINI.app_config().get_value("Directories", ini_location_setting)
            # If no location exists, return the input ini
            if not ini_location:
                return ini
            the_target_ini = ModifyINI.open(test_ini, Path(ini_location))
            if the_target_ini.case_insensitive_config.has_option(section, setting):
                return test_ini
        return ini

    def get_main_ini_from_pecking_order(self, ini: str) -> str:
        """Returns the main ini file from the pecking order for the given ini file."""
        # If Bethini.ini
        if ini == ModifyINI.app_config_name:
            return ini
        pecking_orders = self.bethini["INI_pecking_order"]
        for main_ini in pecking_orders:
            if ini in pecking_orders[main_ini]:
                return main_ini
        return ini

    def get_ini_setting_name(self, ini: ININame) -> str:
        """Returns the INI settings name used in Bethini.ini to store the location
        of the given ini file.
        """

        return self.bethini["INIs"].get(ini) or ""

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

    def get_setting_type(self, setting: str, section: str) -> str:
        """Returns the setting type for the given setting."""
        return self.setting_type_dict.get(f"{setting.lower()}:{section.lower()}", "string")
            
    def get_setting_type_dict(self) -> dict[str, str]:
        """Returns a dictionary listing all the settings and their types as specified in settings.json."""
        setting_type_dict: dict[str, str] = {}
        for ini_setting in self.data["iniValues"]:
            section = ini_setting["section"].lower()
            setting = ini_setting["name"].lower()
            setting_type_dict.setdefault(
                f"{setting}:{section}", ini_setting.get("type", "string"))
        return setting_type_dict

    def get_setting_notes(self, setting: str, section: str) -> str:
        """Returns the setting notes for the given setting."""
        return self.setting_notes_dict.get(f"{setting.lower()}:{section.lower()}", "")

    def get_setting_notes_dict(self) -> dict[str, str]:
        """Returns a dictionary listing all the settings and their notes as specified in settings.json."""
        setting_notes_dict: dict[str, str] = {}
        for ini_setting in self.data["iniValues"]:
            section = ini_setting["section"].lower()
            setting = ini_setting["name"].lower()
            setting_notes_dict.setdefault(
                f"{setting}:{section}", ini_setting.get("notes", ""))
        return setting_notes_dict

    def update_setting_notes(self, setting: str, section: str, notes: str) -> bool:
        """Updates the setting notes for the given setting."""
        success = False
        self.setting_notes_dict[f"{setting.lower()}:{section.lower()}"] = notes
        for ini_setting in self.data["iniValues"]:
            if ini_setting["name"].lower() == setting.lower() and ini_setting["section"].lower() == section.lower():
                ini_setting["notes"] = notes
                success = True
                break
        return success

    def save_data(self) -> None:
        """Saves the settings.json file."""
        with open(self.exedir / "apps" / self.appname / "settings.json", "w", encoding="utf-8") as app_json:
            json.dump(self.data, app_json, indent=4, ensure_ascii=False)

    def get_ini_section_setting_dict(self) -> dict[ININame, dict[str, list[str]]]:
        """Returns a dictionary listing all the INI files with their
        sections and settings as specified in settings.json
        """

        ini_section_setting_dict: dict[ININame, dict[str, list[str]]] = {}
        for ini_setting in self.data["iniValues"]:
            ini = ini_setting.get("ini", self.default_ini)
            if ini is None:
                raise TypeError

            section = ini_setting["section"].lower()
            setting = ini_setting["name"].lower()
            ini_section_setting_dict.setdefault(ini, {}).setdefault(section, []).append(setting)
        return ini_section_setting_dict

    def does_setting_exist(self, ini: ININame, section: str, setting: str) -> bool:
        """Checks if the given setting for the given section and ini file exists in settings.json."""
        setting_exists_list: list[bool] = []
        for valid_ini in self.valid_inis:
            if ini in self.bethini["INI_pecking_order"].get(valid_ini):
                setting_exists_list.append(
                    setting.lower() in self.ini_section_setting_dict[valid_ini].get(section.lower(), ()))

        return True in setting_exists_list

    def preset_values(self, preset: PresetName) -> dict[str, GameSetting]:
        """Returns a dictionary listing all the settings and values
        for a given preset specified in settings.json.
        """

        preset_dict: dict[str, GameSetting] = {}
        for ini_setting in self.data["iniValues"]:
            preset_value = ini_setting["value"].get(preset)
            if preset_value is not None:
                ini = ini_setting.get("ini", self.default_ini)
                if ini is None:
                    raise TypeError
                preset_dict[f"{ini_setting['name']}:{ini_setting['section']}"] = {
                    "ini": ini,
                    "section": ini_setting["section"],
                    "value": str(preset_value),
                }
        return preset_dict

    def can_remove(self) -> dict[str, GameSetting]:
        """Returns a dictionary listing all the settings and default values
        NOT containing the alwaysPrint attribute as specified in settings.json.
        """

        can_remove: dict[str, GameSetting] = {}
        for ini_setting in self.data["iniValues"]:
            if not ini_setting.get("alwaysPrint"):
                can_remove[f"{ini_setting['name']}:{ini_setting['section']}"] = {
                    "ini": ini_setting.get("ini", self.default_ini),
                    "section": ini_setting["section"],
                    "value": str(ini_setting["value"].get("default", "")),
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
        return cast("SettingsLabelFrame", self.bethini["displayTabs"][tab_name][label_frame_name]).get("Pack", default_pack_settings)

    def number_of_vertically_stacked_settings(self, tab_name: str, label_frame_name: str) -> IntStr:
        """Returns the maximum number of vertically stacked settings desired for the label frame."""

        return cast("SettingsLabelFrame", self.bethini["displayTabs"][tab_name][label_frame_name])["NumberOfVerticallyStackedSettings"]
