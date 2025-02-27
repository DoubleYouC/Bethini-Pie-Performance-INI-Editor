#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import ctypes.wintypes
import logging
import os
import shutil
import sys
import winreg
from pathlib import Path
from tkinter import filedialog, simpledialog
from typing import cast

if __name__ == "__main__":
    sys.exit(1)

from lib.app import AppName
from lib.ModifyINI import ModifyINI
from lib.type_helpers import *

logger = logging.getLogger(__name__)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def rgba_to_hex(rgba: tuple[int, int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}{:02x}".format(*rgba)


def hex_to_rgb(value: str) -> tuple[int, int, int] | tuple[int, ...]:
    value = value.lstrip("#")
    lv = len(value)
    if lv == 1:
        v = int(value, 16) * 17
        return v, v, v
    if lv == 3:
        return tuple(int(value[i : i + 1], 16) * 17 for i in range(3))
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def hex_to_decimal(hex_: str) -> str:
    return str(int(hex_.lstrip("#"), 16))


def decimal_to_rgb(decimal_string: str) -> tuple[int, int, int]:
    decimal = int(decimal_string)
    blue = decimal & 255
    green = (decimal >> 8) & 255
    red = (decimal >> 16) & 255
    return (red, green, blue)


def browse_to_location(choice: str, browse: BrowseSettings) -> str | None:
    if choice == "Browse...":
        if browse[2] == "directory":
            response = filedialog.askdirectory()
            if not response:
                return None

            location = Path(response).resolve()

        else:
            response = filedialog.askopenfilename(filetypes=[(browse[1], browse[1])])
            if not response:
                return None

            location = Path(response).resolve()
            try:
                with location.open() as _fp:
                    pass

            except OSError:
                logger.exception("Failed to open file")
                return None

            if browse[0] == "directory" and location.is_file():
                location = location.parent

        logger.debug(f"Location set to '{location}'")
        return str(location)

    if choice == "Manual...":
        response = simpledialog.askstring("Manual Entry", "Custom Value:") or ""
        logger.debug(f"Manually entered a value of '{response}'")
        return response or None
    return None


class Info:
    @staticmethod
    def get_documents_path() -> Path:
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        documents_directory = Path(buf.value)
        logger.debug(f"User documents location: {documents_directory}")

        return documents_directory

    @staticmethod
    def game_documents_name(game_name: str) -> str:
        game_name_documents_location_dict = {
            "Skyrim Special Edition": "Skyrim Special Edition",
            "Skyrim": "Skyrim",
            "Starfield": "Starfield",
            "Fallout 3": "Fallout3",
            "Fallout New Vegas": "FalloutNV",
            "Fallout 4": "Fallout4",
            "Enderal": "Enderal",
            "Oblivion": "Oblivion",
        }

        game_documents_name = game_name_documents_location_dict.get(game_name, "")
        if game_documents_name:
            logger.debug(f"{game_name} Documents/My Games/ folder is {game_documents_name}.")
        else:
            logger.error(f"{game_name} not in the list of known Documents/My Games/ folders.")
        return game_documents_name

    @staticmethod
    def game_reg(game_name: str) -> str:
        game_name_registry_dict = {
            "Skyrim Special Edition": "Skyrim Special Edition",
            "Skyrim": "skyrim",
            "Fallout 3": "fallout3",
            "Fallout New Vegas": "falloutnv",
            "Fallout 4": "Fallout4",
            "Enderal": "skyrim",
            "Oblivion": "oblivion",
        }

        game_reg = game_name_registry_dict.get(game_name, "")
        if not game_reg:
            logger.error(f"{game_name} not in the list of known registry locations.")

        return game_reg


class CustomFunctions:
    # Placeholders to be set when bethini_app initializes
    screenwidth = 0
    screenheight = 0

    @staticmethod
    def restore_backup(_game_name: str, choice: str, _new_value: str) -> None:
        if choice in {"Choose...", "None found"}:
            return

        logger.info(f"Restoring backup from {choice}.")

        if not AppName.app_instance:
            return
        app = AppName.app_instance

        for ini_name in app.what_ini_files_are_used():
            ini_setting_name = app.get_ini_setting_name(ini_name)
            if not ini_setting_name:
                msg = f"Unknown INI: {ini_name}"
                raise NotImplementedError(msg)
            ini_location = ModifyINI.app_config().get_value("Directories", ini_setting_name) or ""

            ini_path = Path(ini_location)
            initial_file = ini_path / ini_name
            new_file = ini_path / "Bethini Pie backups" / choice / ini_name
            try:
                shutil.copyfile(new_file, initial_file)
            except FileNotFoundError:
                logger.exception(f"Restoring {new_file} to {initial_file} failed due to {new_file} not existing.")
            else:
                logger.debug(f"{initial_file} was replaced with backup from {new_file}.")

    @staticmethod
    def refresh_backups(game_name: str, _choice: str, new_value: str | None) -> None:
        # _choice is unused as it will be "Browse..."
        if not AppName.app_instance:
            return

        tab_dictionary = cast("dict[TabId, DisplayTab]", AppName.app_instance.bethini_instance.tab_dictionary)  # type: ignore[reportAttributeAccessIssue]
        setting_frame = tab_dictionary["Page1"]["LabelFrames"]["LabelFrame1"]["SettingFrames"]["SettingFrame0"]
        option_menu = setting_frame["Setting3"]["TkOptionMenu"]
        backups = CustomFunctions.getBackups(game_name, new_value)
        option_menu.set_menu(backups[0], *backups)

    @staticmethod
    def getBackups(game_name: str, location: str | None = None) -> list[str]:
        gameDocumentsName = Info.game_documents_name(game_name)
        if location is None:
            defaultINILocation = str(Info.get_documents_path() / "My Games" / gameDocumentsName) if gameDocumentsName else ""
            location = cast("str", ModifyINI.app_config().get_value("Directories", f"s{game_name}INIPath", defaultINILocation))
        backup_directory = Path(location, "Bethini Pie backups")
        try:
            backups = [b.name for b in sorted(backup_directory.iterdir(), key=os.path.getctime, reverse=True)]
        except OSError:
            backups = ["None found"]
        return ["Choose...", *backups]

    @staticmethod
    def getCurrentResolution(_game_name: str) -> str:
        # _game_name is required for CustomFunction calls

        return f"{CustomFunctions.screenwidth}x{CustomFunctions.screenheight}"

    @staticmethod
    def getBethesdaGameFolder(game_name: str) -> str:
        game_folder = ModifyINI.app_config().get_value("Directories", f"s{game_name}Path")
        if game_folder is not None:
            return game_folder

        key_name = Info.game_reg(game_name)

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, Rf"SOFTWARE\WOW6432Node\Bethesda Softworks\{key_name}") as reg_handle:
                value, value_type = winreg.QueryValueEx(reg_handle, "Installed Path")

            if value and value_type == winreg.REG_SZ and isinstance(value, str):
                return value

        except OSError:
            logger.exception("Game path not found in the registry. Run the game launcher to set it.")
            # TODO: Handle what happens next
        raise NotImplementedError

    @staticmethod
    def getGamePath(game_name: str) -> str | None:
        return ModifyINI.app_config().get_value("Directories", f"s{game_name}Path")

    @staticmethod
    def getINILocations(gameName: str) -> list[str]:
        documents_path = Info.get_documents_path()
        game_documents_path = documents_path / "My Games" / Info.game_documents_name(gameName)
        game_documents_path.mkdir(parents=True, exist_ok=True)
        if not AppName.app_instance:
            return []
        app = AppName.app_instance
        ini_files = app.what_ini_files_are_used()
        for file in ini_files:
            if file == "Ultra.ini":
                continue
            file_path = game_documents_path / file
            with file_path.open() as _fp:
                pass

        return [f"{game_documents_path}{os.sep}", "Browse..."]
