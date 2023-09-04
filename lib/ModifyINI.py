"""This work is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA."""

from collections import OrderedDict
import configparser #This is allowing us to sort the INI files

from lib.customConfigParser import customConfigParser

class ModifyINI:
    """This class gives us an easy way to modify the various INI files in a more
    readable way than calling the configparser every time.
    It also modifies the configparser to work in the way that we desire.
    This by nature allows us to make the changes in how we use the confiparser
    apply to every instance of modifying the INI files."""
    def __init__(self, ini_to_manage, preserve_case=True):
        self.ini_to_manage = ini_to_manage
        self.config = customConfigParser()
        if preserve_case:
            self.config.optionxform = lambda option: option
        self.config.read(self.ini_to_manage)

        self.case_insensitive_config = customConfigParser()
        self.case_insensitive_config.read(self.ini_to_manage)

        self.has_been_modified = False

    def get_existing_section(self, section):
        """Searches for and returns an existing case version of the given section."""
        if self.config.has_section(section):
            return section

        lowercase_section = section.lower()

        for existing_section in self.get_sections():
            lowercase_existing_section = existing_section.lower()
            if lowercase_existing_section == lowercase_section:
                section = existing_section
                break
        return section

    def get_existing_setting(self, section, setting):
        """Searches for and returns an existing case version of the given setting."""

        section = self.get_existing_section(section)

        lowercase_setting = setting.lower()

        for existing_setting in self.get_settings(section, True):
            lowercase_existing_setting = existing_setting.lower()
            if lowercase_existing_setting == lowercase_setting:
                setting = existing_setting
                break
        return setting

    def get_value(self, section, setting, default='Does Not Exist'):
        """Retrieves the value of a given setting, if it exists."""
        section = self.get_existing_section(section)
        #Even though we are checking the case_insensitive_config, sections ARE case sensitive.
        if self.case_insensitive_config.has_section(section):
            return self.case_insensitive_config.get(section, setting, fallback=default)
        return default

    def get_sections(self):
        """Retrieves all sections."""
        return self.case_insensitive_config.sections()

    def get_settings(self, section, original_case=False):
        """Retrieves all settings within the given section."""
        section = self.get_existing_section(section)
        try:
            if original_case:
                settings = self.config.options(section)
            else:
                settings = self.case_insensitive_config.options(section)
        except configparser.NoSectionError:
            return []
        return settings

    def assign_setting_value(self, section, setting, value):
        """Assigns the specified value to the specified setting only if
        different. Returns true if the value was changed."""

        section = self.get_existing_section(section) #preserves existing case for section

        if not self.config.has_section(section): #if section not in self.config, make the section.
            self.config.add_section(section)
            self.case_insensitive_config.add_section(section)

        setting = self.get_existing_setting(section, setting) #preserves existing case for setting

        if self.get_value(section, setting) != value:
            self.config[section][setting] = value
            self.case_insensitive_config[section][setting] = value
            self.has_been_modified = True
            return True
        return False

    def remove_setting(self, section, setting):
        """Removes the specified setting."""
        existing_section = self.get_existing_section(section)
        existing_setting = self.get_existing_setting(existing_section, setting)
        try:
            self.config.remove_option(existing_section, existing_setting)
            self.case_insensitive_config.remove_option(existing_section, existing_setting)
            self.has_been_modified = True
        except configparser.NoSectionError:
            return f"No section: {section}"

    def remove_section(self, section):
        """Removes the specified section."""
        existing_section = self.get_existing_section(section)
        self.config.remove_section(existing_section)
        self.case_insensitive_config.remove_section(existing_section)
        self.has_been_modified = True

    def sort(self):
        """Sorts all sections and settings."""
        for section in self.config._sections:
            self.config._sections[section] = OrderedDict(sorted(self.config._sections[section].items(),
                                                                key=lambda t: t[0]))
        self.config._sections = OrderedDict(sorted(self.config._sections.items(),
                                                   key=lambda t: t[0]))
        self.has_been_modified = True

    def save_ini_file(self, sort=False):
        """Writes the file."""
        if sort:
            self.sort()
        with open(self.ini_to_manage, 'w', encoding='utf-8') as config_file:
            self.config.write(config_file, space_around_delimiters = False)
        self.has_been_modified = False

if __name__ == '__main__':
    print('This is the ModifyINI class module.')
