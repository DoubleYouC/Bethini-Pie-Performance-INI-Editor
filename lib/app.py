"""This work is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA."""

import json

class app_name:
    """This class handles the different apps/games supported, which are placed in
    the apps folder"""
    def __init__(self, appname):
        with open('apps\\' + appname + "\\settings.json") as app_JSON:
            self.data = json.load(app_JSON)
        with open('apps\\' + appname + "\\Bethini.json") as bethini:
            self.bethini = json.load(bethini)

        self.ini_files = list(self.bethini["INIs"].keys())
        try:
            self.default_ini = self.ini_files[2]
        except IndexError:
            self.default_ini = None
        self.ini_values = self.data["iniValues"]
        self.ini_section_setting_dict = self.getIniSectionSettingDict()
        self.setting_values = self.setting_values()
        self.settings = self.settings()
        self.sections = self.sections()

    def gameName(self):
        return self.data["gameName"]

    def presetsIgnoreTheseSettings(self):
        return self.bethini["presetsIgnoreTheseSettings"]

    def custom(self, customVariable):
        return self.bethini["customFunctions"][customVariable]

    def WhatINIFilesAreUsed(self):
        TheINIsDict = self.bethini["INIs"]
        INIFiles = []
        for INI in TheINIsDict:
            if INI != "Bethini.ini":
                INIFiles.append(INI)
        return INIFiles

    def INIs(self, INI):
        try:
            if INI == '':
                INILocation = ''
            else:
                INILocation = self.bethini["INIs"][INI]
            return INILocation
        except KeyError:
            return False
    
    def settings(self):
        INISettings = []
        for iniSetting in self.ini_values:
            INISettings.append(iniSetting['name'])
        return INISettings

    def sections(self):
        INISections = []
        for iniSetting in self.ini_values:
            if iniSetting['section'] not in INISections:
                INISections.append(iniSetting['section'])
        INISections.sort()
        return INISections

    def setting_values(self):
        settingValues = {}
        for iniSetting in self.ini_values:
            settingValues[iniSetting['name']] = {}
            valueTypes = self.bethini['valueTypes']
            for valueType in valueTypes:
                try:
                    settingValues[iniSetting['name']][valueType] = iniSetting['value'][valueType]
                except KeyError:
                    continue
        return settingValues
    
    def getIniSectionSettingDict(self):
        iniSectionSettingDict = {}
        for iniSetting in self.ini_values:
            ini = iniSetting.get('ini', self.default_ini)
            section = iniSetting.get('section').lower()
            setting = iniSetting.get('name')
            if ini not in list(iniSectionSettingDict.keys()):
                iniSectionSettingDict[ini] = {
                    section: [setting]
                    }
            elif section not in list(iniSectionSettingDict[ini].keys()):
                iniSectionSettingDict[ini][section] = [setting]
            else:
                iniSectionSettingDict[ini][section].append(setting)
        
        return iniSectionSettingDict

    def getValue(self, setting, value_type):
        return self.setting_values[setting][value_type]

    def doesSettingExist(self, ini, section, setting):
        section = section.lower()
        try:
            theSectionList = [x.lower() for x in self.ini_section_setting_dict[ini][section]]
            setting = setting.lower()
            if setting in theSectionList:
                return True
            else:
                return False
        except KeyError:
            return False

    def presetValues(self, preset):
        PresetDict = {}
        for iniSetting in self.ini_values:
            presetValue = iniSetting['value'].get(preset)
            if presetValue or presetValue == 0 or presetValue == '':
                ini = iniSetting.get('ini', self.default_ini)
                PresetDict[iniSetting['name']]={
                    'ini': ini,
                    'section': iniSetting['section'],
                    'value': str(presetValue)
                    }
        return PresetDict

    def alwaysPrint(self):
        alwaysPrint = {}
        for iniSetting in self.ini_values:
            alwaysPrint = iniSetting.get('alwaysPrint')
            if alwaysPrint:
                ini = iniSetting.get('ini', self.default_ini)

                theValue = str(iniSetting['value'].get('fixedDefault', iniSetting['value'].get('default')))

                alwaysPrint[iniSetting['name']]={
                    'ini': ini,
                    'section': iniSetting['section'],
                    'value': theValue
                    }
        return alwaysPrint

    def canRemove(self):
        canRemove = {}
        for iniSetting in self.ini_values:
            alwaysPrint = iniSetting.get('alwaysPrint')
            if not alwaysPrint:
                ini = iniSetting.get('ini', self.default_ini)

                theValue = str(iniSetting['value'].get('default'))

                canRemove[iniSetting['name']] = {
                    'ini': ini,
                    'section': iniSetting['section'],
                    'value': theValue
                    }
        return canRemove

    def settingSomethingDictionary(self, something):
        SomethingSomethings = []
        for iniSetting in self.ini_values:
            SomethingSomethings.append(iniSetting[something])

        SomethingSomethingsDictionary = {}
        iteration = -1
        for setting in self.settings:
            iteration += 1
            SomethingSomethingsDictionary[setting] = SomethingSomethings[iteration]
        return SomethingSomethingsDictionary

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