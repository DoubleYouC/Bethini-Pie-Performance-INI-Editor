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
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, simpledialog

if __name__ == "__main__":
    sys.exit(1)

from lib.app import AppName
from lib.ModifyINI import ModifyINI

logger = logging.getLogger(__name__)

try:
    from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKey, QueryValueEx
except ModuleNotFoundError:
    logger.error("winreg module not found")

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def rgba_to_hex(rgba: tuple[int, int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}{:02x}".format(*rgba)

def hex_to_rgb(value: str) -> tuple[int, int, int] | tuple[int, ...]:
    value = value.lstrip("#")
    lv = len(value)
    if lv == 1:
        v = int(value, 16)*17
        return v, v, v
    if lv == 3:
        return tuple(int(value[i:i + 1], 16)*17 for i in range(3))
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def hex_to_decimal(hex_) -> str:
    return str(int(str(hex_).lstrip("#"),16))

def decimal_to_rgb(decimal) -> tuple[int, int, int]:
    decimal = int(decimal)
    blue = decimal & 255
    green = (decimal >> 8) & 255
    red = (decimal >> 16) & 255
    return (red, green, blue)

def browse_to_location(choice: str, browse: tuple[str, ...], function: str, game_name) -> str:
    if choice == "Browse...":
        if browse[2] == "directory":
            location = Path(filedialog.askdirectory()).resolve()
        else:
            openfilename = Path(filedialog.askopenfilename(filetypes=[(browse[1], browse[1])]))
            if not openfilename.exists():
                logger.error(f"file not found: {openfilename}")
                return choice
            try:
                with openfilename.open() as _fp:
                    pass
            except OSError:
                logger.error(f"failed to open file: {openfilename}")
                return choice
            location = openfilename.resolve()
            if browse[0] == "directory":
                location = Path(os.path.join(os.path.split(str(location))[0], ""))
        logger.debug(f"location set to '{location}'")
        return str(location)

    if choice == "Manual...":
        manual = simpledialog.askstring("Manual entry", "Custom Value:")
        logger.debug(f"Manually entered a value of {manual}")
        if manual:
            return manual
        return choice

    if function:
        return_value_of_custom_function = getattr(CustomFunctions, function)(game_name,choice)
        logger.debug(f"Return value of {function}: {return_value_of_custom_function}")
    return choice

class Info:
    @staticmethod
    def get_documents_path() -> Path:
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        documents_directory = Path(buf.value)
        logger.debug(f"User documents location: {documents_directory}")

        return documents_directory

    @staticmethod
    def game_documents_name(game_name: str) -> str:
        game_name_documents_location_dict = {"Skyrim Special Edition": "Skyrim Special Edition",
                                         "Skyrim": "Skyrim",
                                         "Starfield": "Starfield",
                                         "Fallout 3": "Fallout3",
                                         "Fallout New Vegas": "FalloutNV",
                                         "Fallout 4": "Fallout4",
                                         "Enderal": "Enderal",
                                         "Oblivion": "Oblivion"}

        game_documents_name = game_name_documents_location_dict.get(game_name, "")
        if game_documents_name:
            logger.debug(f"{game_name} Documents/My Games/ folder is {game_documents_name}.")
        else:
            logger.error(f"{game_name} not in the list of known Documents/My Games/ folders.")
        return game_documents_name

    @staticmethod
    def game_reg(game_name: str) -> str:
        game_name_registry_dict = {"Skyrim Special Edition": "Skyrim Special Edition",
                                "Skyrim": "skyrim",
                                "Fallout 3": "fallout3",
                                "Fallout New Vegas": "falloutnv",
                                "Fallout 4": "Fallout4",
                                "Enderal": "skyrim",
                                "Oblivion": "oblivion"}

        game_reg = game_name_registry_dict.get(game_name, "")
        if not game_reg:
            logger.error(f"{game_name} not in the list of known registry locations.")

        return game_reg

class CustomFunctions:

    # Placeholders to be set when bethini_app initializes
    screenwidth = 0
    screenheight = 0

    @staticmethod
    def restore_backup(game_name: str, choice: str) -> None:
        if choice in {"Choose...", "None found"}:
            return

        logger.info(f"Restoring backup from {choice}.")
        app = AppName(game_name)
        Bethini_key = ModifyINI("Bethini.ini")

        for ini in app.what_ini_files_are_used():
            ini_location = Path(Bethini_key.get_value("Directories", app.inis(ini)))
            initial_file = ini_location / ini
            new_file = ini_location / "Bethini Pie backups" / choice / ini
            try:
                shutil.copyfile(new_file, initial_file)
            except FileNotFoundError:
                logger.error(f"Restoring {new_file} to {initial_file} failed due to {new_file} not existing.")
            else:
                logger.debug(f"{initial_file} was replaced with backup from {new_file}.")

    @staticmethod
    def getBackups(game_name: str) -> list[str]:
        gameDocumentsName = Info.game_documents_name(game_name)
        defaultINILocation = str(Info.get_documents_path() / "My Games" / gameDocumentsName) if gameDocumentsName else ""
        INIPath = ModifyINI("Bethini.ini").get_value("Directories", f"s{game_name}INIPath", default=defaultINILocation)
        backup_directory = Path(INIPath) / "Bethini Pie backups"
        try:
            backups = [b.name for b in backup_directory.iterdir()]
        except OSError:
            backups = ["None found"]
        return ["Choose...", *backups]

    @staticmethod
    def getCurrentResolution(_game_name: str) -> str:
        # _game_name is required for CustomFunction calls

        return f"{CustomFunctions.screenwidth}x{CustomFunctions.screenheight}"

    @staticmethod
    def getBethesdaGameFolder(game_name: str):
        game_folder = ModifyINI("Bethini.ini").get_value("Directories", f"s{game_name}Path")
        if game_folder is not None:
            return game_folder

        gameReg = Info.game_reg(game_name)

        try:
            game_folder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f"SOFTWARE\\Bethesda Softworks\\{gameReg}"), "installed path")[0]
        except:
            logger.error("Did not find game folder in the registry (no WOW6432Node location).")

        if game_folder is None:
            try:
                game_folder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f"SOFTWARE\\WOW6432Node\\Bethesda Softworks\\{gameReg}"), "installed path")[0]
            except:
                logger.error("Did not find game folder in the registry.")

        return game_folder

    @staticmethod
    def getGamePath(game_name: str):
        return ModifyINI("Bethini.ini").get_value("Directories", f"s{game_name}Path")

    @staticmethod
    def getINILocations(gameName: str) -> list[str]:
        documents_path = Info.get_documents_path()
        game_documents_path = documents_path / "My Games" / Info.game_documents_name(gameName)
        game_documents_path.mkdir(parents=True, exist_ok=True)
        app = AppName(gameName)
        ini_files = app.what_ini_files_are_used()
        for file in ini_files:
            if file == "Ultra.ini":
                continue
            file_path = game_documents_path / file
            with file_path.open() as _fp:
                pass

        return [str(game_documents_path), "Browse..."]
