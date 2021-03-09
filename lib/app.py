"""This work is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA."""

import json

class AppName:
    """This class handles the different apps/games supported, which are placed in
    the apps folder"""
    # pylint: disable=too-many-instance-attributes
    def __init__(self, appname):
        with open('apps\\' + appname + "\\settings.json") as app_json:
            self.data = json.load(app_json)
        with open('apps\\' + appname + "\\Bethini.json") as bethini:
            self.bethini = json.load(bethini)

        ini_files = list(self.bethini["INIs"].keys())
        try:
            self.default_ini = ini_files[2]
        except IndexError:
            self.default_ini = None
        self.ini_values = self.data["iniValues"]
        self.ini_section_setting_dict = self.get_ini_section_setting_dict()
        self.setting_values = self.setting_values()
        self.settings = self.settings()
        self.sections = self.sections()

    def game_name(self):
        return self.data["gameName"]

    def presets_ignore_these_settings(self):
        return self.bethini["presetsIgnoreTheseSettings"]

    def custom(self, custom_variable):
        return self.bethini["customFunctions"][custom_variable]

    def what_ini_files_are_used(self):
        the_inis_dict = self.bethini["INIs"]
        ini_files = []
        for ini in the_inis_dict:
            if ini != "Bethini.ini":
                ini_files.append(ini)
        return ini_files

    def inis(self, ini):
        try:
            if ini == '':
                ini_location = ''
            else:
                ini_location = self.bethini["INIs"][ini]
            return ini_location
        except KeyError:
            return False
    
    def settings(self):
        ini_settings = []
        for ini_setting in self.ini_values:
            ini_settings.append(ini_setting['name'])
        return ini_settings

    def sections(self):
        ini_sections = []
        for ini_setting in self.ini_values:
            if ini_setting['section'] not in ini_sections:
                ini_sections.append(ini_setting['section'])
        ini_sections.sort()
        return ini_sections

    def setting_values(self):
        setting_values = {}
        for ini_setting in self.ini_values:
            setting_values[ini_setting['name']] = {}
            value_types = self.bethini['valueTypes']
            for value_type in value_types:
                try:
                    setting_values[ini_setting['name']][value_type] = ini_setting['value'][value_type]
                except KeyError:
                    continue
        return setting_values
    
    def get_ini_section_setting_dict(self):
        ini_section_setting_dict = {}
        for ini_setting in self.ini_values:
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
        return self.setting_values[setting][value_type]

    def does_setting_exist(self, ini, section, setting):
        section = section.lower()
        try:
            the_section_list = [x.lower() for x in self.ini_section_setting_dict[ini][section]]
            setting = setting.lower()
            if setting in the_section_list:
                return True
            else:
                return False
        except KeyError:
            return False

    def preset_values(self, preset):
        preset_dict = {}
        for ini_setting in self.ini_values:
            preset_value = ini_setting['value'].get(preset)
            if preset_value or preset_value == 0 or preset_value == '':
                ini = ini_setting.get('ini', self.default_ini)
                preset_dict[ini_setting['name']]={
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': str(preset_value)
                    }
        return preset_dict

    def always_print(self):
        always_print = {}
        for ini_setting in self.ini_values:
            always_print = ini_setting.get('alwaysPrint')
            if always_print:
                ini = ini_setting.get('ini', self.default_ini)

                the_value = str(ini_setting['value'].get('fixedDefault', ini_setting['value'].get('default')))

                always_print[ini_setting['name']]={
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': the_value
                    }
        return always_print

    def can_remove(self):
        can_remove = {}
        for ini_setting in self.ini_values:
            always_print = ini_setting.get('alwaysPrint')
            if not always_print:
                ini = ini_setting.get('ini', self.default_ini)

                the_value = str(ini_setting['value'].get('default'))

                can_remove[ini_setting['name']] = {
                    'ini': ini,
                    'section': ini_setting['section'],
                    'value': the_value
                    }
        return can_remove

    def setting_something_dictionary(self, something):
        something_somethings = []
        for ini_setting in self.ini_values:
            something_somethings.append(ini_setting[something])

        something_somethings_dictionary = {}
        iteration = -1
        for setting in self.settings:
            iteration += 1
            something_somethings_dictionary[setting] = something_somethings[iteration]
        return something_somethings_dictionary

    def settingSectionDictionary(self):
        INISections = []
        for iniSetting in self.ini_values:
            INISections.append(iniSetting['section'])

        settingSectionDictionary = {}
        iteration = -1
        for setting in self.settings:
            iteration += 1
            settingSectionDictionary[setting] = INISections[iteration]
        return settingSectionDictionary

    def getSettingSection(self, setting):
        settingSectionDictionary = self.settingSectionDictionary()
        return settingSectionDictionary[setting]

    def tabs(self):
        return self.iteritemslist(self.bethini["displayTabs"])

    def labelFramesInTab(self, tab):
        return self.iteritemslist(self.bethini['displayTabs'][tab])

    def fieldsInSetting(self, tab, labelFrame, setting):
        return self.iteritemslist(self.getAllFieldsForSetting(tab, labelFrame, setting))

    def iteritemslist(self, items):
        itemlist = []
        for item in items:
            itemlist.append(item)
        return itemlist

    def settingsInLabelFrame(self, tab, labelFrame):
        return self.iteritemslist(self.bethini['displayTabs'][tab][labelFrame]['Settings'])

    def NumberOfVerticallyStackedSettings(self, tab, labelFrame):
        return self.bethini['displayTabs'][tab][labelFrame]['NumberOfVerticallyStackedSettings']

    def settingField(self, tab, labelFrame, setting, field, default='No Default'):
        try:
            return self.bethini['displayTabs'][tab][labelFrame]['Settings'][setting][field]
        except KeyError:
            if default != 'No Default':
                return default
            return

    def getAllFieldsForSetting(self, tab, labelFrame, setting):
        return self.bethini['displayTabs'][tab][labelFrame]['Settings'][setting]

    
if __name__ == '__main__':
    print('This is the app.appName class module.')