#
#This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
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

from lib.app import appName
from lib.ModifyINI import ModifyINI

def copyFileNoOverwrite(src, dest):
    # Open the file and raise an exception if it exists
    try:
        fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except:
        sm(f'{dest} already exists, so it will not be overwritten.',debug=True, exception=True)
        return

    # Copy the file and automatically close files at the end
    with os.fdopen(fd) as f:
        with open(src) as sf:
            shutil.copyfileobj(sf, f)

def sm(message, debug=False, exception=False):
    if not exception:
        logging.info(message)
        print(message)
    elif exception:
        logging.debug(message, exc_info=True)
        print(message)
    return

def RGBToHex(rgb):
    return '#%02x%02x%02x' % rgb

def HexToRGB(value):
    value = value.lstrip('#')
    lv = len(value)
    if lv == 1:
        v = int(value, 16)*17
        return v, v, v
    if lv == 3:
        return tuple(int(value[i:i + 1], 16)*17 for i in range(0, 3))
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def HexToDecimal(x):
    return str(int(str(x).lstrip('#'),16))

def DecimalToRGB(decimal):
    decimal = int(decimal)
    blue = decimal & 255
    green = (decimal >> 8) & 255
    red = (decimal >> 16) & 255
    return (red, green, blue)



def browseToLocation(choice, browse, function, gameName):
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
            returnValueOfCustomFunction = getattr(customFunctions, function)(gameName,choice)
            sm(f"Return value of {function}: {returnValueOfCustomFunction}")
        return choice

class Info:
    def getDocumentsDirectory():
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        documentsDirectory = buf.value
        sm(f'User documents location: {documentsDirectory}')

        return documentsDirectory

    def getMOProfiles(gameName):
        ModOrganizerINILocation = customFunctions.getMODirectory(gameName)[0] + 'ModOrganizer.ini'
        profiles = []
        profiles_directory = ""
        if 'Not Detected' not in ModOrganizerINILocation:
            ModOrganizerINI = ModifyINI(ModOrganizerINILocation)
            base_directory = ModOrganizerINI.getValue('Settings','base_directory', default=lambda: os.path.split(ModOrganizerINILocation)[0]).replace('\\\\','\\').replace('/','\\')
            profiles_directory = ModOrganizerINI.getValue('Settings','profiles_directory', default=f'{base_directory}\\profiles').replace('\\\\','\\').replace('/','\\')
            
            profiles = os.listdir(profiles_directory)
        return [profiles_directory, profiles]

    def gameDocumentsName(gameName):
        gameNameDocumentsLocationDict = {"Skyrim Special Edition": "Skyrim Special Edition",
                                         "Skyrim": "Skyrim",
                                         "Fallout 3": "Fallout3",
                                         "Fallout New Vegas": "FalloutNV",
                                         "Fallout 4": "Fallout4",
                                         "Enderal": "Enderal",
                                         "Oblivion": "Oblivion"}
        try:
            gameDocumentsName = gameNameDocumentsLocationDict[gameName]
            sm(f'{gameName} Documents\My Games folder is {gameDocumentsName}.')
        except Exception as e:
            sm(f'{gameName} not in the list of known Documents\My Games folders.', exception=1)
            gameDocumentsName = ''
        return gameDocumentsName

    def gameReg(gameName):
        gameNameRegistryDict = {"Skyrim Special Edition": "Skyrim Special Edition",
                                "Skyrim": "skyrim",
                                "Fallout 3": "fallout3",
                                "Fallout New Vegas": "falloutnv",
                                "Fallout 4": "Fallout4",
                                "Enderal": "skyrim",
                                "Oblivion": "oblivion"}
        try:
            gameReg = gameNameRegistryDict[gameName]
        except Exception as e:
            sm(f'{gameName} not in the list of known registry locations.', exception=1)
            gameReg = ''
        return gameReg

    def nxmhandlerGameReference(gameName):
        gameNameDict = {"Skyrim Special Edition": "skyrimse",
                        "Skyrim": "skyrim",
                        "Fallout 3": "fallout3",
                        "Fallout New Vegas": "falloutnv",
                        "Fallout 4": "fallout4",
                        "Enderal": "enderal",
                        "Oblivion": "oblivion"}
        try:
            gameReg = gameNameDict[gameName]
            sm(f'{gameName} is in the gameNameDict as {gameReg}.')
        except Exception as e:
            sm(f'{gameName} not in the gameNameDict', exception=1)
            gameReg = ''
        return gameReg

class customFunctions:

    def RestoreBackup(gameName, choice):
        app = appName(gameName)
        INIFiles = app.WhatINIFilesAreUsed()

        gameDocumentsName = Info.gameDocumentsName(gameName)
        if gameDocumentsName != '':
            defaultINILocation = Info.getDocumentsDirectory() + f'\\My Games\\{gameDocumentsName}\\'
        else:
            defaultINILocation = ''
        INIPath = ModifyINI("Bethini.ini").getValue("Directories", "s" + gameName + "INIPath", default=defaultINILocation)
        instance = os.path.split(os.path.split(INIPath)[0])[1]
        #backup_directory = f"cache\\{gameName}\\{instance}\\{choice}\\"
        backup_directory = f'{INIPath}Bethini Pie backups\\{choice}\\'

        INIFilesWithLocation = {}
        for INI in INIFiles:
            BethINIKey = app.INIs(INI)
            if BethINIKey == '':
                #if the location is the working directory
                INILocation = ''
            else:
                #if the location is specified in the BethINI.ini file.
                if INI == 'theme.ini':
                    continue
                else:
                    INILocation = ModifyINI("Bethini.ini").getValue('Directories', BethINIKey, defaultINILocation)
            INIFilesWithLocation[INI] = INILocation

        filesToReplace = {}
        for INI in INIFilesWithLocation:
            fileToReplace = INIFilesWithLocation[INI] + INI
            backupFile = backup_directory + INI
            filesToReplace[INI] = {"InitialFile": fileToReplace,
                                 "NewFile": backupFile}

        if choice == "Choose..." or "None found":
            return
        else:
            print(filesToReplace)
            #TODO: This will need to be programmed to actually restore the
            #backup.  We need to program the creation of backups first!
            
        
        return filesToReplace

    def getBackups(gameName):
        gameDocumentsName = Info.gameDocumentsName(gameName)
        if gameDocumentsName != '':
            defaultINILocation = Info.getDocumentsDirectory() + f'\\My Games\\{gameDocumentsName}\\'
        else:
            defaultINILocation = ''
        INIPath = ModifyINI("Bethini.ini").getValue("Directories", "s" + gameName + "INIPath", default=defaultINILocation)
        #instance = os.path.split(os.path.split(INIPath)[0])[1]
        
        backup_directory = f'{INIPath}/Bethini Pie backups'

        #backup_directory = f"cache/{gameName}/{instance}/"

        #working_directory = os.getcwd()
        #print(backup_directory)
        #backups = os.listdir(backup_directory)
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
        gameReg = Info.gameReg(gameName)

        try:
            gameFolder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\Bethesda Softworks\\{gameReg}'),"installed path")[0]
        except Exception as e:
            sm('Did not find game folder in the registry (no WOW6432Node location).', exception=1)
        if gameFolder == 'Not Detected':
            try:
                gameFolder = QueryValueEx(OpenKey(ConnectRegistry(None, HKEY_LOCAL_MACHINE), f'SOFTWARE\\WOW6432Node\\Bethesda Softworks\\{gameReg}'),"installed path")[0]
            except Exception as e:
                sm('Did not find game folder in the registry.', exception=1)

        return gameFolder

    def getINILocations(gameName):
        gameDocumentsLocation = Info.gameDocumentsName(gameName)
        INILocation = [Info.getDocumentsDirectory() + f'\\My Games\\{gameDocumentsLocation}\\']
        getProfiles = Info.getMOProfiles(gameName)
        profiles = getProfiles[1]
        profiles_directory = getProfiles[0]
        for profile in profiles:
            INILocation.append(f'{profiles_directory}\\{profile}\\')
        INILocation.append('Browse...')
        return INILocation

    def getMODirectory(gameName):
        #This custom function is used to detect the location of Mod Organizer

        ModOrganizerINILocationFromConfig = ModifyINI("Bethini.ini").getValue("Directories", "s" + gameName + "ModOrganizerINIPath", default="Not Detected")

        pathValue = "Not Detected"
        gameReg = Info.nxmhandlerGameReference(gameName)

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
        except Exception as e:
            sm('NXM links are probably not set up.', exception=1)
        
        try:
            nxmhandlersINI
        except Exception as e:
            #nxmhandlers.ini not found.  Check for the AppData location.
            sm('nxmhandlers.ini not found. Checking AppData location.', exception=1)
            AppDataLocation = str(pathlib.Path.home()) + r"\AppData\Local\ModOrganizer\nxmhandler.ini"
            if os.path.isfile(AppDataLocation):
                nxmhandlers = AppDataLocation
                nxmhandlersINI = ModifyINI(nxmhandlers)
                sm(f'nxmhandler.ini found in {nxmhandlers}')
        try:
            size = int(nxmhandlersINI.getValue('handlers', 'size')) + 1
            for n in range(size):
                key = str(n) + '\\games'
                value = nxmhandlersINI.getValue('handlers', key)
                if gameReg != "skyrimse":
                    value = value.replace('skyrimse','')
                if gameReg in value:
                    pathKey = str(n) + '\\executable'
                    pathValue = os.path.split(nxmhandlersINI.getValue('handlers', pathKey).replace('\\\\','\\'))[0]
                    pathValue += '\\'
                    sm(f'Mod Organizer appears to be located at {pathValue}')
        except Exception as e:
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