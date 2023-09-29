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
from tkinter import filedialog
from tkinter import simpledialog

from lib.app import AppName
from lib.ModifyINI import ModifyINI

def sm(message, debug=False, exception=False):
    if not exception:
        logging.info(message)
        print(message)
    elif exception:
        logging.debug(message, exc_info=True)
        print(message)
        
try:
    from winreg import QueryValueEx, OpenKey, ConnectRegistry, HKEY_LOCAL_MACHINE
except ModuleNotFoundError:
    sm('winreg module not found')

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def rgba_to_hex(rgba):
    return '#%02x%02x%02x%02x' % rgba

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    if lv == 1:
        v = int(value, 16)*17
        return v, v, v
    if lv == 3:
        return tuple(int(value[i:i + 1], 16)*17 for i in range(0, 3))
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def hex_to_decimal(hex_):
    return str(int(str(hex_).lstrip('#'),16))

def decimal_to_rgb(decimal):
    decimal = int(decimal)
    blue = decimal & 255
    green = (decimal >> 8) & 255
    red = (decimal >> 16) & 255
    return (red, green, blue)



def browse_to_location(choice, browse, function, game_name):
    if choice == 'Browse...':
        if browse[2] == 'directory':
            location = filedialog.askdirectory()
            location = location.replace('/','\\')
            if location != '' and location[-1] != '\\':
                location += '\\'
        else:
            openfilename = filedialog.askopenfilename(filetypes=[(browse[1], browse[1])])
            try:
                fp = open(openfilename,"r")
                fp.close()
            except:
                sm('Not Found', exception=1)
                return choice
            location = openfilename.replace('/','\\')
            if browse[0] == "directory":
                location = os.path.split(location)[0] + '\\'
        return location
    elif choice == 'Manual...':
        manual = simpledialog.askstring("Manual entry", "Custom Value:")
        sm(f"Manually entered a value of {manual}")
        if manual:
            return manual
        return choice
    else:
        if function:
            return_value_of_custom_function = getattr(CustomFunctions, function)(game_name,choice)
            sm(f"Return value of {function}: {return_value_of_custom_function}")
        return choice

class Info:
    def get_documents_directory():
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        documents_directory = buf.value
        sm(f'User documents location: {documents_directory}')

        return documents_directory

    def game_documents_name(game_name):
        game_name_documents_location_dict = {"Skyrim Special Edition": "Skyrim Special Edition",
                                         "Skyrim": "Skyrim",
                                         "Starfield": "Starfield",
                                         "Fallout 3": "Fallout3",
                                         "Fallout New Vegas": "FalloutNV",
                                         "Fallout 4": "Fallout4",
                                         "Enderal": "Enderal",
                                         "Oblivion": "Oblivion"}
        try:
            game_documents_name = game_name_documents_location_dict[game_name]
            sm(f'{game_name} Documents\\My Games folder is {game_documents_name}.')
        except:
            sm(f'{game_name} not in the list of known Documents\\My Games folders.', exception=1)
            game_documents_name = ''
        return game_documents_name

    def game_reg(game_name):
        game_name_registry_dict = {"Skyrim Special Edition": "Skyrim Special Edition",
                                "Skyrim": "skyrim",
                                "Fallout 3": "fallout3",
                                "Fallout New Vegas": "falloutnv",
                                "Fallout 4": "Fallout4",
                                "Enderal": "skyrim",
                                "Oblivion": "oblivion"}
        try:
            game_reg = game_name_registry_dict[game_name]
        except:
            sm(f'{game_name} not in the list of known registry locations.', exception=1)
            game_reg = ''
        return game_reg

class CustomFunctions:

    def restore_backup(game_name, choice):
        sm(f'Restoring backup from {choice}.')
        app = AppName(game_name)
        ini_files = app.what_ini_files_are_used()
        
        ini_files_with_location = {}
        
        Bethini_key = ModifyINI("Bethini.ini")
        
        for ini in ini_files:
            ini_files_with_location[ini] = app.inis(ini)

        files_to_replace = {}
        for ini in ini_files_with_location:
            ini_location = Bethini_key.get_value("Directories", ini_files_with_location[ini])
            file_to_replace = f'{ini_location}{ini}'
            backup_file = f'{ini_location}Bethini Pie backups\\{choice}\\{ini}'
            files_to_replace[ini] = {"InitialFile": file_to_replace,
                                 "NewFile": backup_file}

        if choice == "Choose..." or choice == "None found":
            return
        else:
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
            for file in files_to_replace:
                initial_file = files_to_replace[file].get('InitialFile')
                new_file = files_to_replace[file].get('NewFile')
                try:
                    shutil.copyfile(f"{new_file}", f"{initial_file}")
                    sm(f'{initial_file} was replaced with backup from {new_file}.')
                except FileNotFoundError:
                    sm(f'Restoring {new_file} to {initial_file} failed due to {new_file} not existing.', True, True)
        return

    def getBackups(game_name):
        gameDocumentsName = Info.game_documents_name(game_name)
        if gameDocumentsName != '':
            defaultINILocation = Info.get_documents_directory() + f'\\My Games\\{gameDocumentsName}\\'
        else:
            defaultINILocation = ''
        INIPath = ModifyINI("Bethini.ini").get_value("Directories", "s" + game_name + "INIPath", default=defaultINILocation)
        backup_directory = f'{INIPath}/Bethini Pie backups'
        try:
            backups = os.listdir(backup_directory)
        except:
            backups = ["None found"]
        return ['Choose...', *backups]

    def getCurrentResolution(gameName):
        root = tk.Tk()
        root.withdraw()
        WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
        return str(WIDTH) + "x" + str(HEIGHT)

    def getBethesdaGameFolder(game_name):
        game_folder = ModifyINI("Bethini.ini").get_value("Directories", "s" + game_name + "Path", default='Not Detected')
        if game_folder != 'Not Detected':
            return game_folder
        gameReg = Info.game_reg(game_name)

        try:
            game_folder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\Bethesda Softworks\\{gameReg}'),"installed path")[0]
        except:
            sm('Did not find game folder in the registry (no WOW6432Node location).', exception=1)
        if game_folder == 'Not Detected':
            try:
                game_folder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\WOW6432Node\\Bethesda Softworks\\{gameReg}'),"installed path")[0]
            except:
                sm('Did not find game folder in the registry.', exception=1)

        return game_folder
    
    def getGamePath(game_name):
        return ModifyINI("Bethini.ini").get_value("Directories", "s" + game_name + "Path", default='Not Detected')

    def getINILocations(gameName):
        gameDocumentsLocation = Info.game_documents_name(gameName)
        documents_directory = Info.get_documents_directory()
        INILocation = [f'{documents_directory}\\My Games\\{gameDocumentsLocation}\\']
        if not os.path.exists(f'{documents_directory}\\My Games\\{gameDocumentsLocation}\\'):
            os.mkdir(f'{documents_directory}\\My Games\\{gameDocumentsLocation}\\')
        app = AppName(gameName)
        ini_files = app.what_ini_files_are_used()                 
        for file in ini_files:
            if file == 'Ultra.ini':
                continue
            if not os.path.exists(f'{documents_directory}\\My Games\\{gameDocumentsLocation}\\{file}'):
                open(f'{documents_directory}\\My Games\\{gameDocumentsLocation}\\{file}', 'w')
        INILocation.append('Browse...')
        return INILocation

if __name__ == '__main__':
    print('This is the customFunctions module.')