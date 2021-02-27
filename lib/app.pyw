import json #This allows us to read the app/game json files

class appName:
    #This class handles the different apps/games supported, which are placed in
    #the apps folder
    def __init__(self, appname):
        with open('apps\\' + appname + "\\settings.json") as appJSON:
            self.data = json.load(appJSON)
        with open('apps\\' + appname + "\\Bethini.json") as Bethini:
            self.Bethini = json.load(Bethini)

        self.INIFiles = list(self.Bethini["INIs"].keys())
        self.defaultINI = self.INIFiles[2]
        self.iniValues = self.data["iniValues"]
        self.iniSectionSettingDict = self.getIniSectionSettingDict()
        self.settingValues = self.settingValues()
        self.settings = self.settings()
        self.sections = self.sections()

    def gameName(self):
        return self.data["gameName"]

    def presetsIgnoreTheseSettings(self):
        return self.Bethini["presetsIgnoreTheseSettings"]

    def custom(self, customVariable):
        return self.Bethini["customFunctions"][customVariable]

    def WhatINIFilesAreUsed(self):
        TheINIsDict = self.Bethini["INIs"]
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
                INILocation = self.Bethini["INIs"][INI]
            return INILocation
        except:
            return False
    
    def settings(self):
        INISettings = []
        for iniSetting in self.iniValues:
            INISettings.append(iniSetting['name'])
        return INISettings

    def sections(self):
        INISections = []
        for iniSetting in self.iniValues:
            if iniSetting['section'] not in INISections:
                INISections.append(iniSetting['section'])
        INISections.sort()
        return INISections

    def settingValues(self):
        settingValues = {}
        for iniSetting in self.iniValues:
            settingValues[iniSetting['name']] = {}
            valueTypes = self.Bethini['valueTypes']
            for valueType in valueTypes:
                try:
                    settingValues[iniSetting['name']][valueType] = iniSetting['value'][valueType]
                except:
                    continue
        return settingValues
    
    def getIniSectionSettingDict(self):
        iniSectionSettingDict = {}
        for iniSetting in self.iniValues:
            ini = iniSetting.get('ini', self.defaultINI)
            section = iniSetting.get('section')
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

    def getValue(self, setting, type):
        return self.settingValues[setting][type]

    def doesSettingExist(self, ini, section, setting):
        try:
            theSectionList = [x.lower() for x in self.iniSectionSettingDict[ini][section]]
            setting = setting.lower()
            if setting in theSectionList:
                return True
            else:
                return False
        except:
            return False

    def presetValues(self, preset):
        PresetDict = {}
        for iniSetting in self.iniValues:
            presetValue = iniSetting['value'].get(preset)
            if presetValue or presetValue == 0:
                ini = iniSetting.get('ini', self.defaultINI)
                PresetDict[iniSetting['name']]={
                    'ini': ini,
                    'section': iniSetting['section'],
                    'value': str(presetValue)
                    }
        return PresetDict

    def alwaysPrint(self):
        alwaysPrint = {}
        for iniSetting in self.iniValues:
            alwaysPrint = iniSetting.get('alwaysPrint')
            if alwaysPrint:
                ini = iniSetting.get('ini', self.defaultINI)

                theValue = str(iniSetting['value'].get('fixedDefault', iniSetting['value'].get('default')))

                alwaysPrint[iniSetting['name']]={
                    'ini': ini,
                    'section': iniSetting['section'],
                    'value': theValue
                    }
        return alwaysPrint

    def canRemove(self):
        canRemove = {}
        for iniSetting in self.iniValues:
            alwaysPrint = iniSetting.get('alwaysPrint')
            if not alwaysPrint:
                ini = iniSetting.get('ini', self.defaultINI)

                theValue = str(iniSetting['value'].get('default'))

                canRemove[iniSetting['name']] = {
                    'ini': ini,
                    'section': iniSetting['section'],
                    'value': theValue
                    }
        return canRemove

    def settingSomethingDictionary(self, something):
        SomethingSomethings = []
        for iniSetting in self.iniValues:
            SomethingSomethings.append(iniSetting[something])

        SomethingSomethingsDictionary = {}
        iteration = -1
        for setting in self.settings:
            iteration += 1
            SomethingSomethingDictionary[setting] = SomethingSomethings[iteration]
        return SomethingSomethingsDictionary

    def settingSectionDictionary(self):
        INISections = []
        for iniSetting in self.iniValues:
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
        return self.iteritemslist(self.Bethini["displayTabs"])

    def labelFramesInTab(self, tab):
        return self.iteritemslist(self.Bethini['displayTabs'][tab])

    def fieldsInSetting(self, tab, labelFrame, setting):
        return self.iteritemslist(self.getAllFieldsForSetting(tab, labelFrame, setting))

    def iteritemslist(self, items):
        itemlist = []
        for item in items:
            itemlist.append(item)
        return itemlist

    def settingsInLabelFrame(self, tab, labelFrame):
        return self.iteritemslist(self.Bethini['displayTabs'][tab][labelFrame]['Settings'])

    def NumberOfVerticallyStackedSettings(self, tab, labelFrame):
        return self.Bethini['displayTabs'][tab][labelFrame]['NumberOfVerticallyStackedSettings']

    def settingField(self, tab, labelFrame, setting, field, default='No Default'):
        try:
            return self.Bethini['displayTabs'][tab][labelFrame]['Settings'][setting][field]
        except:
            if default != 'No Default':
                return default
            return

    def getAllFieldsForSetting(self, tab, labelFrame, setting):
        return self.Bethini['displayTabs'][tab][labelFrame]['Settings'][setting]

    
