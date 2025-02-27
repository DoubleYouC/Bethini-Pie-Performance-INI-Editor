#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import configparser
import logging
import sys
from pathlib import Path
from typing import ClassVar

if __name__ == "__main__":
    sys.exit(1)

from lib.customConfigParser import customConfigParser
from lib.type_helpers import *

logger = logging.getLogger(__name__)


class ModifyINI:
    """This class gives us an easy way to modify the various INI files in a more
    readable way than calling the configparser every time.
    It also modifies the configparser to work in the way that we desire.
    This by nature allows us to make the changes in how we use the confiparser
    apply to every instance of modifying the INI files.
    """

    app_config_name: ClassVar[ININame] = "Bethini.ini"
    open_inis: ClassVar[dict[ININame, dict[Path, "ModifyINI"]]] = {}
    _open_app_config: ClassVar["ModifyINI | None"] = None

    @staticmethod
    def app_config() -> "ModifyINI":
        """Access Bethini's config INI."""

        if not ModifyINI._open_app_config:
            ModifyINI._open_app_config = ModifyINI.open(ModifyINI.app_config_name, Path.cwd())
        return ModifyINI._open_app_config

    @staticmethod
    def open(name: ININame, location: Path, *, preserve_case: bool = True) -> "ModifyINI":
        """Open an INI file.

        If the file is already open, the existing ModifyINI instance will be returned.
        """

        existing_object = ModifyINI.open_inis.setdefault(name, {}).get(location)
        if existing_object:
            if preserve_case != existing_object.preserve_case:
                msg = f"{location.name} opened twice with different settings."
                raise NotImplementedError(msg)
            return existing_object

        new_object = ModifyINI(name, location, preserve_case=preserve_case)
        ModifyINI.open_inis.setdefault(name, {})[location] = new_object
        return new_object

    def __init__(self, name: ININame, location: Path, *, preserve_case: bool = True) -> None:
        self.ini_path = Path(location, name)
        self.preserve_case = preserve_case

        self.config = customConfigParser()
        if preserve_case:
            self.config.optionxform = lambda optionstr: optionstr
        logger.info(f"Successfully read {self.config.read(self.ini_path)}")

        self.case_insensitive_config = customConfigParser()
        logger.info(f"Successfully read {self.case_insensitive_config.read(self.ini_path)} (case insensitive)")

        self.has_been_modified = False

    def get_existing_section(self, section: str) -> str:
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

    def get_existing_setting(self, section: str, setting: str) -> str:
        """Searches for and returns an existing case version of the given setting."""

        section = self.get_existing_section(section)

        lowercase_setting = setting.lower()

        for existing_setting in self.get_settings(section, original_case=True):
            lowercase_existing_setting = existing_setting.lower()
            if lowercase_existing_setting == lowercase_setting:
                setting = existing_setting
                break
        return setting

    def get_value(self, section: str, setting: str, default: str | None = None) -> str | None:
        """Retrieves the value of a given setting, if it exists."""

        section = self.get_existing_section(section)
        # Even though we are checking the case_insensitive_config, sections ARE case sensitive.
        if self.case_insensitive_config.has_section(section):
            return self.case_insensitive_config.get(section, setting, fallback=default)
        return default

    def get_sections(self) -> list[str]:
        """Retrieves all sections."""

        return self.case_insensitive_config.sections()

    def get_settings(self, section: str, *, original_case: bool = False) -> list[str]:
        """Retrieves all settings within the given section."""

        section = self.get_existing_section(section)
        try:
            settings = self.config.options(section) if original_case else self.case_insensitive_config.options(section)
        except configparser.NoSectionError:
            settings = []
        return settings

    def assign_setting_value(self, section: str, setting: str, value: str) -> bool:
        """Assigns the specified value to the specified setting only if
        different. Returns true if the value was changed.
        """

        # Preserves existing case for section
        section = self.get_existing_section(section)

        # If section not in self.config, make the section.
        if not self.config.has_section(section):
            self.config.add_section(section)
            self.case_insensitive_config.add_section(section)

        # Preserves existing case for setting
        setting = self.get_existing_setting(section, setting)

        current_value = self.get_value(section, setting)
        if current_value != value:
            self.config[section][setting] = value
            self.case_insensitive_config[section][setting] = value
            self.has_been_modified = True
            return True
        return False

    def remove_setting(self, section: str, setting: str) -> bool:
        """Remove the specified setting.

        Returns True if the section exists, False otherwise.
        """

        existing_section = self.get_existing_section(section)
        existing_setting = self.get_existing_setting(existing_section, setting)
        try:
            self.config.remove_option(existing_section, existing_setting)
            self.case_insensitive_config.remove_option(existing_section, existing_setting)
            self.has_been_modified = True
        except configparser.NoSectionError:
            return False
        return True

    def remove_section(self, section: str) -> None:
        """Removes the specified section."""

        existing_section = self.get_existing_section(section)
        self.config.remove_section(existing_section)
        self.case_insensitive_config.remove_section(existing_section)
        self.has_been_modified = True

    def sort(self) -> None:
        """Sorts all sections and settings."""

        for section in self.config._sections:  # noqa: SLF001
            self.config._sections[section] = dict(sorted(self.config._sections[section].items()))  # noqa: SLF001
        self.config._sections = dict(sorted(self.config._sections.items()))  # noqa: SLF001
        self.has_been_modified = True

    def save_ini_file(self, *, sort: bool = False) -> None:
        """Writes the file."""

        if sort:
            self.sort()
        with self.ini_path.open("w", encoding="utf-8") as config_file:
            self.config.write(config_file, space_around_delimiters=False)
        self.has_been_modified = False
