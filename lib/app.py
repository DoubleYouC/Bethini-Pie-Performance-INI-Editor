"""This work is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA."""

import json
import os
from typing import Any, Literal


class AppName:
    """This class handles the different apps/games supported, which are placed in
    the apps folder."""

    def __init__(self, appname: str) -> None:
        with open(os.path.join('apps', appname, 'settings.json'), encoding='utf-8') as app_json:
            self.data: dict = json.load(app_json)
        with open(os.path.join('apps', appname, 'Bethini.json'), encoding='utf-8') as bethini:
            self.bethini: dict = json.load(bethini)

        self.default_ini = self.bethini['INIs'].keys()[1] if len(self.bethini['INIs']) > 1 else None

        self.setting_values = self.get_setting_values()

        self.ini_section_setting_dict = self.get_ini_section_setting_dict()

    def what_ini_files_are_used(self) -> list[Any]:
        """Returns a list of INI files used, with Bethini.ini removed from the list."""
        ini_files = []
        for ini in self.bethini["INIs"]:
            if ini != "Bethini.ini":
                ini_files.append(ini)
        return ini_files

    def inis(self, ini) -> Literal['', False] | Any:
        """Returns the INI settings name used in Bethini.ini to store the location
        of the given ini file."""
        try:
            return '' if not ini else self.bethini["INIs"][ini]
        except KeyError:
            return False

    def get_setting_values(self) -> dict[Any, Any]:
        """Returns a dictionary listing all the different value types for every setting."""
        setting_values = {}
        for ini_setting in self.data["iniValues"]:
            setting_values[ini_setting['name']] = {}
            for value_type in self.bethini['valueTypes']:
                try:
                    the_value_for_this_type = ini_setting['value'][value_type]
                    setting_values[ini_setting['name']][value_type] = the_value_for_this_type
                except KeyError:
                    continue
        return setting_values

    def get_ini_section_setting_dict(self) -> dict[Any, Any]:
        """Returns a dictionary listing all the INI files with their
        sections and settings as specified in settings.json"""
        ini_section_setting_dict = {}
        for ini_setting in self.data["iniValues"]:
            ini = ini_setting.get('ini', self.default_ini)
            section = ini_setting.get('section').lower()
            setting = ini_setting.get('name')
            if ini not in list(ini_section_setting_dict.keys()):
                ini_section_setting_dict[ini] = {
                    section: [setting]
                    }
            elif section not in list(ini_section_setting_dict[ini].keys()):
                ini_section_setting_dict[ini][section] = [setting]
            else:
                ini_section_setting_dict[ini][section].append(setting)

        return ini_section_setting_dict

    def does_setting_exist(self, ini, section, setting) -> bool:
        """Checks if the given setting for the given
        section and ini file exists in settings.json."""
        section = section.lower()
        try:
            the_section_list = [x.lower() for x in self.ini_section_setting_dict[ini][section]]
            setting = setting.lower()
        except KeyError:
            return False
        return setting in the_section_list

    def preset_values(self, preset) -> dict[Any, Any]:
        """Returns a dictionary listing all the settings and values
        for a given preset specified in settings.json."""
        preset_dict = {}
        for ini_setting in self.data["iniValues"]:
            preset_value = ini_setting['value'].get(preset)
            if preset_value or preset_value in {0, ''}:
                #if a preset value was specified
                ini = ini_setting.get('ini', self.default_ini)
                preset_dict[ini_setting['name']+':'+ini_setting['section']]={
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': str(preset_value)
                    }
        return preset_dict

    def can_remove(self) -> dict[Any, Any]:
        """Returns a dictionary listing all the settings and default values
        NOT containing the alwaysPrint attribute as specified in settings.json."""
        can_remove = {}
        for ini_setting in self.data["iniValues"]:
            if not ini_setting.get('alwaysPrint'):
                ini = ini_setting.get('ini', self.default_ini)

                the_value = str(ini_setting['value'].get('default'))

                can_remove[ini_setting['name']+':'+ini_setting['section']] = {
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': the_value
                    }
        return can_remove

    def pack_settings(self, tab, label_frame) -> Any:
        """Returns the pack settings for the label frame."""
        default_pack_settings = {
            'Side': 'Top',
            'Anchor': 'NW',
            'Fill': 'Both',
            'Expand': 1
            }
        return self.bethini['displayTabs'][tab][label_frame].get('Pack', default_pack_settings)

    def number_of_vertically_stacked_settings(self, tab, label_frame) -> Any:
        """Returns the maximum number of vertically stacked settings desired for the label frame."""
        return self.bethini['displayTabs'][tab][label_frame]['NumberOfVerticallyStackedSettings']

if __name__ == '__main__':
    print('This is the app.appName class module.')
