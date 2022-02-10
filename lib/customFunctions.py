#
#This work is licensed under the
#Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
#or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import os
import logging
import pathlib
import ctypes.wintypes
import tkinter as tk
import shutil
from tkinter import filedialog
from tkinter import simpledialog
from winreg import QueryValue, QueryValueEx, OpenKey, ConnectRegistry, HKEY_CLASSES_ROOT, HKEY_LOCAL_MACHINE

from lib.app import AppName
from lib.ModifyINI import ModifyINI

def sm(message, debug=False, exception=False):
    if not exception:
        logging.info(message)
        print(message)
    elif exception:
        logging.debug(message, exc_info=True)
        print(message)

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

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

    def get_mo_profiles(game_name):
        mod_organizer_ini_location = CustomFunctions.getMODirectory(game_name)[0] + 'ModOrganizer.ini'
        profiles = []
        profiles_directory = ""
        if 'Not Detected' not in mod_organizer_ini_location:
            mod_organizer_ini = ModifyINI(mod_organizer_ini_location)
            base_directory = mod_organizer_ini.get_value('Settings','base_directory',
                                                        default=lambda: os.path.split(mod_organizer_ini_location)[0]).replace('\\\\','\\').replace('/','\\')
            profiles_directory = mod_organizer_ini.get_value('Settings','profiles_directory',
                                                            default=f'{base_directory}\\profiles').replace('\\\\','\\').replace('/','\\')
            profiles = os.listdir(profiles_directory)
        return [profiles_directory, profiles]

    def game_documents_name(game_name):
        game_name_documents_location_dict = {"Skyrim Special Edition": "Skyrim Special Edition",
                                         "Skyrim": "Skyrim",
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

    def nxmhandler_game_reference(game_name):
        game_name_dict = {"Skyrim Special Edition": "skyrimse",
                        "Skyrim": "skyrim",
                        "Fallout 3": "fallout3",
                        "Fallout New Vegas": "falloutnv",
                        "Fallout 4": "fallout4",
                        "Enderal": "enderal",
                        "Oblivion": "oblivion"}
        try:
            game_reg = game_name_dict[game_name]
            sm(f'{game_name} is in the gameNameDict as {game_reg}.')
        except:
            sm(f'{game_name} not in the gameNameDict', exception=1)
            game_reg = ''
        return game_reg

class CustomFunctions:

    def restore_backup(game_name, choice):
        sm(f'Restoring backup from {choice}.')
        app = AppName(game_name)
        ini_files = app.what_ini_files_are_used()

        game_documents_name = Info.game_documents_name(game_name)
        if game_documents_name != '':
            default_ini_location = Info.get_documents_directory() + f'\\My Games\\{game_documents_name}\\'
        else:
            default_ini_location = ''
        ini_path = ModifyINI("Bethini.ini").get_value("Directories",
                                                    "s" + game_name + "INIPath",
                                                    default=default_ini_location)
        backup_directory = f'{ini_path}Bethini Pie backups\\{choice}\\'

        ini_files_with_location = {}
        for ini in ini_files:
            bethini_key = app.inis(ini)
            if bethini_key == '':
                #if the location is the working directory
                ini_location = ''
            else:
                #if the location is specified in the BethINI.ini file.
                if ini == 'theme.ini':
                    continue
                else:
                    ini_location = ModifyINI("Bethini.ini").get_value('Directories',
                                                                     bethini_key, default_ini_location)
            ini_files_with_location[ini] = ini_location

        files_to_replace = {}
        for ini in ini_files_with_location:
            file_to_replace = ini_files_with_location[ini] + ini
            backup_file = backup_directory + ini
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
                shutil.copyfile(f"{new_file}", f"{initial_file}")
                sm(f'{initial_file} was replaced with backup from {new_file}.')
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

    def getThemes(gameName):
        theme_dir = os.getcwd() + '\\theme'
        themes = os.listdir(theme_dir)
        return themes

    def getCurrentResolution(gameName):
        
        root = tk.Tk()
        root.withdraw()
        WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
        return str(WIDTH) + "x" + str(HEIGHT)

    def getBethesdaGameFolder(gameName):
        gameFolder = 'Not Detected'
        gameReg = Info.game_reg(gameName)

        try:
            gameFolder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\Bethesda Softworks\\{gameReg}'),"installed path")[0]
        except:
            sm('Did not find game folder in the registry (no WOW6432Node location).', exception=1)
        if gameFolder == 'Not Detected':
            try:
                gameFolder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\WOW6432Node\\Bethesda Softworks\\{gameReg}'),"installed path")[0]
            except:
                sm('Did not find game folder in the registry.', exception=1)

        return gameFolder

    def getINILocations(gameName):
        gameDocumentsLocation = Info.game_documents_name(gameName)
        INILocation = [Info.get_documents_directory() + f'\\My Games\\{gameDocumentsLocation}\\']
        getProfiles = Info.get_mo_profiles(gameName)
        profiles = getProfiles[1]
        profiles_directory = getProfiles[0]
        for profile in profiles:
            INILocation.append(f'{profiles_directory}\\{profile}\\')
        INILocation.append('Browse...')
        return INILocation

    def getMODirectory(gameName):
        #This custom function is used to detect the location of Mod Organizer

        ModOrganizerINILocationFromConfig = ModifyINI("Bethini.ini").get_value("Directories", "s" + gameName + "ModOrganizerINIPath", default="Not Detected")

        pathValue = "Not Detected"
        gameReg = Info.nxmhandler_game_reference(gameName)

        #Look up the nxm link (download with mod manager links on the
        #NexusMods.com sites) handler to find Mod Organizer location
        try:
            nxm = QueryValue(OpenKey(ConnectRegistry(None, HKEY_CLASSES_ROOT), r'nxm\shell\open\command'),"")
            sm(f'NXM links point to {nxm}')
            if 'nxmhandler' in nxm:
                nxmhandler = nxm.split('\"')[1]
                nxmhandlers = nxmhandler.replace("nxmhandler.exe","nxmhandlers.ini")
                if os.path.isfile(nxmhandlers):
                    nxmhandlersINI = ModifyINI(nxmhandlers)
                    sm(f'nxmhandlers.ini found here: {nxmhandlers}')
        except:
            sm('NXM links are probably not set up.', exception=1)
        
        try:
            nxmhandlersINI
        except:
            #nxmhandlers.ini not found.  Check for the AppData location.
            sm('nxmhandlers.ini not found. Checking AppData location.', exception=1)
            AppDataLocation = str(pathlib.Path.home()) + r"\AppData\Local\ModOrganizer\nxmhandler.ini"
            if os.path.isfile(AppDataLocation):
                nxmhandlers = AppDataLocation
                nxmhandlersINI = ModifyINI(nxmhandlers)
                sm(f'nxmhandler.ini found in {nxmhandlers}')
        try:
            size = int(nxmhandlersINI.get_value('handlers', 'size')) + 1
            for n in range(size):
                key = str(n) + '\\games'
                value = nxmhandlersINI.get_value('handlers', key)
                if gameReg != "skyrimse":
                    value = value.replace('skyrimse','')
                if gameReg in value:
                    pathKey = str(n) + '\\executable'
                    pathValue = os.path.split(nxmhandlersINI.get_value('handlers', pathKey).replace('\\\\','\\'))[0]
                    pathValue += '\\'
                    sm(f'Mod Organizer appears to be located at {pathValue}')
        except:
            sm('There is probably no nxmhandler.ini.', exception=1)

        ModOrganizerINILocation = 'Not Detected'
        if os.path.isfile(f'{pathValue}ModOrganizer.ini'):
            ModOrganizerINILocation = f'{pathValue}ModOrganizer.ini'
            sm(f'Found {ModOrganizerINILocation}')
        elif os.path.isfile(str(pathlib.Path.home()) + f"\\AppData\\Local\\ModOrganizer\\{gameReg}\\ModOrganizer.ini"):
            ModOrganizerINILocation = str(pathlib.Path.home()) + f"\\AppData\\Local\\ModOrganizer\\{gameReg}\\ModOrganizer.ini"
            sm(f'Found {ModOrganizerINILocation}')
        if ModOrganizerINILocation != 'Not Detected':
            ModOrganizerINILocation = os.path.split(ModOrganizerINILocation)[0]
            ModOrganizerINILocation += '\\'
        else:
            sm('Failed to locate ModOrganizer.ini')
            ModOrganizerINILocation = ModOrganizerINILocationFromConfig
            
        if ModOrganizerINILocation != ModOrganizerINILocationFromConfig and ModOrganizerINILocationFromConfig != "Not Detected":
            return [ModOrganizerINILocationFromConfig,ModOrganizerINILocation,"Browse..."]

        return [ModOrganizerINILocation,"Browse...","Manual..."]

if __name__ == '__main__':
    print('This is the customFunctions module.')