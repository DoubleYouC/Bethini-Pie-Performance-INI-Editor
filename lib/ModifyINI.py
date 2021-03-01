#
#This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

from collections import OrderedDict #This is allowing us to sort the INI files

from lib.customConfigParser import customConfigParser

class ModifyINI:
    #This class gives us an easy way to modify the various INI files in a more
    #readable way than calling the configparser every time.
    #It also modifies the configparser to work in the way that we desire.
    #This by nature allows us to make the changes in how we use the confiparser
    #apply to every instance of modifying the INI files.
    def __init__(self, INItoModify, preserveCase=True):
        self.INItoModify = INItoModify
        self.config = customConfigParser()
        if preserveCase:
            self.config.optionxform = lambda option: option
        self.config.read(self.INItoModify)

        self.caseInsensitiveConfig = customConfigParser()
        self.caseInsensitiveConfig.read(self.INItoModify)

        self.HasBeenModified = False

    def getValue(self, section, setting, default='Does Not Exist'):
        if section in self.caseInsensitiveConfig:
            return self.caseInsensitiveConfig[section].get(setting, default)
        return default

    def getSections(self):
        return self.caseInsensitiveConfig.sections()

    def getSettings(self, section):
        settings = []
        for item in self.config.items(section):
            settings.append(item[0])
        return settings

    def assignINIValue(self, section, setting, value):
        #assigns the specified value to the specified setting only if
        #different.  Case sensitive.  Returns true if the value was changed.

        if section not in self.config:
            self.config[section] = {}
            self.caseInsensitiveConfig[section] = {}
        if self.getValue(section, setting) != value:
            for eachSetting in self.config[section]:
                #This beautiful for loop prevents duplicate settings if they
                #happen to be there in some messed up capitalized
                #non-capitalized state!!!  Oh how I cried and cried trying to
                #figure this one out!
                if eachSetting.lower() == setting.lower():
                    self.config.remove_option(section, eachSetting)
            self.config[section][setting] = value
            self.caseInsensitiveConfig[section][setting] = value
            self.HasBeenModified = True
            return True
        else:
            return False

    def removeSetting(self, section, setting):
        self.config.remove_option(section, setting)
        self.HasBeenModified = True

    def removeSection(self, section):
        self.config.remove_section(section)
        self.HasBeenModified = True

    def writeValue(self, section, setting, value):
        #writes the specified value to the specified setting only if the value
        #is different from what is already there.
        if self.assignINIValue(section, setting, value):
            self.writeINI()
            self.HasBeenModified = False

    def doesSettingExist(self, section, setting):
        #returns boolean for if the setting exists.
        if setting in self.caseInsensitiveConfig[section]:
            return True
        return False

    def sort(self):
        #sorts all sections and settings.
        for section in self.config._sections:
            self.config._sections[section] = OrderedDict(sorted(self.config._sections[section].items(), key=lambda t: t[0]))
        self.config._sections = OrderedDict(sorted(self.config._sections.items(), key=lambda t: t[0]))
        self.HasBeenModified = True

    def writeINI(self, sort=False):
        #writes the file.
        if sort:
            self.sort()
        with open(self.INItoModify, 'w') as configfile:
            self.config.write(configfile, space_around_delimiters = False)
        self.HasBeenModified = False

if __name__ == '__main__':
    print('This is the ModifyINI class module.')

    