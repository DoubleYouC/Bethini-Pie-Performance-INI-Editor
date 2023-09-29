"""This work is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA."""

import json

def iter_items_list(items):
    """Given a dictionary, returns a list of all items."""
    item_list = []
    for item in items:
        item_list.append(item)
    return item_list

class AppName:
    """This class handles the different apps/games supported, which are placed in
    the apps folder."""

    def __init__(self, appname):
        with open('apps\\' + appname + '\\settings.json', encoding='utf-8') as app_json:
            self.data = json.load(app_json)
        with open('apps\\' + appname + '\\Bethini.json', encoding='utf-8') as bethini:
            self.bethini = json.load(bethini)

        ini_files = list(self.bethini["INIs"].keys())
        try:
            self.default_ini = ini_files[1]
        except IndexError:
            self.default_ini = None

        self.setting_values = self.get_setting_values()

        self.ini_section_setting_dict = self.get_ini_section_setting_dict()

    def tabs(self):
        """Returns a list of tabs to be displayed."""
        return iter_items_list(self.bethini["displayTabs"])

    def custom(self, custom_variable):
        """Given a custom_variable, returns the corresponding customFunction."""
        return self.bethini["customFunctions"][custom_variable]

    def what_ini_files_are_used(self):
        """Returns a list of INI files used, with Bethini.ini removed from the list."""
        ini_files = []
        for ini in self.bethini["INIs"]:
            if ini != "Bethini.ini":
                ini_files.append(ini)
        return ini_files

    def inis(self, ini):
        """Returns the INI settings name used in Bethini.ini to store the location
        of the given ini file."""
        try:
            if ini == '':
                ini_location = ''
            else:
                ini_location = self.bethini["INIs"][ini]
            return ini_location
        except KeyError:
            return False

    def settings(self):
        """Returns a list of settings in settings.json."""
        return iter_items_list(self.data["iniValues"])

    def sections(self):
        """Returns a sorted list of sections in settings.json"""
        ini_sections = []
        for ini_setting in self.data["iniValues"]:
            if ini_setting['section'] not in ini_sections:
                ini_sections.append(ini_setting['section'])
        ini_sections.sort()
        return ini_sections

    def get_setting_values(self):
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

    def get_ini_section_setting_dict(self):
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

    def get_value(self, setting, value_type):
        """Returns the value for the given setting and value type."""
        return self.setting_values[setting][value_type]

    def does_setting_exist(self, ini, section, setting):
        """Checks if the given setting for the given
        section and ini file exists in settings.json."""
        section = section.lower()
        try:
            the_section_list = [x.lower() for x in self.ini_section_setting_dict[ini][section]]
            setting = setting.lower()
            return setting in the_section_list
        except KeyError:
            return False

    def preset_values(self, preset):
        """Returns a dictionary listing all the settings and values
        for a given preset specified in settings.json."""
        preset_dict = {}
        for ini_setting in self.data["iniValues"]:
            preset_value = ini_setting['value'].get(preset)
            if preset_value or preset_value == 0 or preset_value == '':
            #if a preset value was specified
                ini = ini_setting.get('ini', self.default_ini)
                preset_dict[ini_setting['name']+':'+ini_setting['section']]={
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': str(preset_value)
                    }
        return preset_dict

    def always_print(self):
        """Returns a dictionary listing all the settings and default values
        containing the alwaysPrint attribute as specified in settings.json."""
        always_print = {}
        for ini_setting in self.data["iniValues"]:
            always_print = ini_setting.get('alwaysPrint')
            if always_print:
                ini = ini_setting.get('ini', self.default_ini)
                the_value = str(ini_setting['value'].get('fixedDefault',
                                                         ini_setting['value'].get('default')))
                always_print[ini_setting['name']+':'+ini_setting['section']]={
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': the_value
                    }
        return always_print

    def can_remove(self):
        """Returns a dictionary listing all the settings and default values
        NOT containing the alwaysPrint attribute as specified in settings.json."""
        can_remove = {}
        for ini_setting in self.data["iniValues"]:
            always_print = ini_setting.get('alwaysPrint')
            if not always_print:
                ini = ini_setting.get('ini', self.default_ini)

                the_value = str(ini_setting['value'].get('default'))

                can_remove[ini_setting['name']+':'+ini_setting['section']] = {
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': the_value
                    }
        return can_remove

    def label_frames_in_tab(self, tab):
        """Returns a list of label frames in the given tab."""
        return iter_items_list(self.bethini['displayTabs'][tab])

    def settings_in_label_frame(self, tab, label_frame):
        """Returns a list of settings in the given lable frame."""
        return iter_items_list(self.bethini['displayTabs'][tab][label_frame]['Settings'])

    def pack_settings(self, tab, label_frame):
        """Returns the pack settings for the label frame."""
        default_pack_settings = {
            'Side': 'Top',
            'Anchor': 'NW',
            'Fill': 'Both',
            'Expand': 1
            }
        pack_settings = self.bethini['displayTabs'][tab][label_frame].get('Pack',
                                                                          default_pack_settings)
        return pack_settings

    def number_of_vertically_stacked_settings(self, tab, label_frame):
        """Returns the maximum number of vertically stacked settings desired for the label frame."""
        return self.bethini['displayTabs'][tab][label_frame]['NumberOfVerticallyStackedSettings']

    def get_all_fields_for_setting(self, tab, label_frame, setting):
        """Returns all fields for the given setting."""
        return self.bethini['displayTabs'][tab][label_frame]['Settings'][setting]

if __name__ == '__main__':
    print('This is the app.appName class module.')
