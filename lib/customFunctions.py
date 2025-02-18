#
#This work is licensed under the
#Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
#or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import os
import logging
import ctypes.wintypes
import tkinter as tk
import shutil
from pathlib import Path
from tkinter import filedialog
from tkinter import simpledialog
from lib.app import AppName
from lib.ModifyINI import ModifyINI

logger = logging.getLogger(__name__)

try:
    from winreg import QueryValueEx, OpenKey, ConnectRegistry, HKEY_LOCAL_MACHINE
except ModuleNotFoundError:
    logger.error('winreg module not found')

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def rgba_to_hex(rgba: tuple[int, int, int, int]) -> str:
    return '#{:02x}{:02x}{:02x}{:02x}'.format(*rgba)

def hex_to_rgb(value: str) -> tuple[int, int, int] | tuple[int, ...]:
    value = value.lstrip('#')
    lv = len(value)
    if lv == 1:
        v = int(value, 16)*17
        return v, v, v
    if lv == 3:
        return tuple(int(value[i:i + 1], 16)*17 for i in range(3))
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def hex_to_decimal(hex_) -> str:
    return str(int(str(hex_).lstrip('#'),16))

def decimal_to_rgb(decimal) -> tuple[int, int, int]:
    decimal = int(decimal)
    blue = decimal & 255
    green = (decimal >> 8) & 255
    red = (decimal >> 16) & 255
    return (red, green, blue)

def browse_to_location(choice: str, browse: tuple[str, ...], function: str, game_name) -> str:
    if choice == 'Browse...':
        if browse[2] == 'directory':
            location = Path(filedialog.askdirectory()).resolve()
        else:
            openfilename = Path(filedialog.askopenfilename(filetypes=[(browse[1], browse[1])]))
            if not openfilename.exists():
                logger.error(f'file not found: {openfilename}')
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

    if choice == 'Manual...':
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
        logger.debug(f'User documents location: {documents_directory}')

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
            logger.debug(f'{game_name} Documents/My Games/ folder is {game_documents_name}.')
        else:
            logger.error(f'{game_name} not in the list of known Documents/My Games/ folders.')
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
            logger.error(f'{game_name} not in the list of known registry locations.')

        return game_reg

class CustomFunctions:

    @staticmethod
    def restore_backup(game_name: str, choice: str) -> None:
        logger.info(f'Restoring backup from {choice}.')
        app = AppName(game_name)
        ini_files = app.what_ini_files_are_used()

        ini_files_with_location = {}

        Bethini_key = ModifyINI("Bethini.ini")

        for ini in ini_files:
            ini_files_with_location[ini] = app.inis(ini)

        files_to_replace = {}
        for ini, file_paths in ini_files_with_location.items():
            ini_location = str(Bethini_key.get_value("Directories", file_paths))
            file_to_replace = f'{ini_location}{ini}'
            backup_file = Path(ini_location) / "Bethini Pie backups" / choice / ini
            files_to_replace[ini] = {"InitialFile": file_to_replace,
                                 "NewFile": backup_file}

        if choice in {"Choose...", "None found"}:
            return

        #An example of filesToReplace
        #{
        #    'Skyrim.ini':
        #        {
        #            'InitialFile': 'S:\\Documents\\My Games\\Skyrim Special Edition\\Skyrim.ini',
        #            'NewFile': 'S:\\Documents\\My Games\\Skyrim Special Edition\\Bethini Pie backups\\First-Time-Backup\\Skyrim.ini'
        #        },
        #    'SkyrimPrefs.ini':
        #        {
        #            'InitialFile': 'S:\\Documents\\My Games\\Skyrim Special Edition\\SkyrimPrefs.ini',
        #            'NewFile': 'S:\\Documents\\My Games\\Skyrim Special Edition\\Bethini Pie backups\\First-Time-Backup\\SkyrimPrefs.ini'
        #        }
        #}
        for file_paths in files_to_replace.values():
            initial_file = file_paths.get('InitialFile')
            new_file = file_paths.get('NewFile')
            try:
                shutil.copyfile(f"{new_file}", f"{initial_file}")
                logger.debug(f'{initial_file} was replaced with backup from {new_file}.')
            except FileNotFoundError:
                logger.error(f'Restoring {new_file} to {initial_file} failed due to {new_file} not existing.')

    @staticmethod
    def getBackups(game_name: str) -> list[str]:
        gameDocumentsName = Info.game_documents_name(game_name)
        defaultINILocation = str(Info.get_documents_path() / 'My Games' / gameDocumentsName) if gameDocumentsName else ''
        INIPath = str(ModifyINI("Bethini.ini").get_value("Directories", f"s{game_name}INIPath", default=defaultINILocation))
        backup_directory = Path(INIPath) / 'Bethini Pie backups'
        try:
            backups = [b.name for b in backup_directory.iterdir()]
        except OSError:
            backups = ["None found"]
        return ['Choose...', *backups]

    @staticmethod
    def getCurrentResolution(_game_name: str) -> str:
        # _game_name is required for CustomFunction calls
        root = tk.Tk()
        root.withdraw()
        WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
        return f"{WIDTH}x{HEIGHT}"

    @staticmethod
    def getBethesdaGameFolder(game_name: str):
        game_folder = ModifyINI('Bethini.ini').get_value('Directories', f's{game_name}Path')
        if game_folder is not None:
            return game_folder

        gameReg = Info.game_reg(game_name)

        try:
            game_folder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\Bethesda Softworks\\{gameReg}'), "installed path")[0]
        except:
            logger.error('Did not find game folder in the registry (no WOW6432Node location).')

        if game_folder is None:
            try:
                game_folder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\WOW6432Node\\Bethesda Softworks\\{gameReg}'), "installed path")[0]
            except:
                logger.error('Did not find game folder in the registry.')

        return game_folder

    @staticmethod
    def getGamePath(game_name: str):
        return ModifyINI("Bethini.ini").get_value("Directories", f"s{game_name}Path")

    @staticmethod
    def getINILocations(gameName: str) -> list[str]:
        documents_path = Info.get_documents_path()
        game_documents_path = documents_path / 'My Games' / Info.game_documents_name(gameName)
        game_documents_path.mkdir(parents=True, exist_ok=True)
        app = AppName(gameName)
        ini_files = app.what_ini_files_are_used()
        for file in ini_files:
            if file == 'Ultra.ini':
                continue
            file_path = game_documents_path / file
            with file_path.open() as _fp:  # TODO this line needs refactoring, unused filehandle
                pass

        return [str(game_documents_path), 'Browse...']

if __name__ == '__main__':
    print('This is the customFunctions module.')
