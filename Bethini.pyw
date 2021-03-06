#
#This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import ast
import os
import math
import logging
import webbrowser
from shutil import copyfile
from datetime import datetime
from fractions import Fraction
from operator import gt, ge, lt, le, ne, eq
#from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR, S_IWGRP, S_IWRITE #This is for changing file read-only access via os.chmod(filename, S_IREAD,
                                                                       #S_IRGRP, #S_IROTH) Not currently used.                                                     
import tkinter as tk 
from tkinter import ttk
from tkinter import colorchooser
from tkinter import simpledialog
from tkinter import messagebox

from lib.app import appName
from lib.AutoScrollbar import AutoScrollbar
from lib.tooltips import CreateToolTip
from lib.ModifyINI import ModifyINI
from lib.customFunctions import customFunctions, sm, browseToLocation, RGBToHex, HexToRGB, HexToDecimal, DecimalToRGB

def loadTheme():
    #This loads the theme as specified in the Bethini.ini file to the relative
    #theme\<theme-name>\theme.ini file.
    global theme #theme needs to be global so it can be called later
    theme = appConfig.getValue('General', 'sTheme', default="Default") #get the theme name form the sTheme:General setting in Bethini.ini. Defaults to 'Default'          
    
    if os.path.isfile(f'{cwd}\\theme\\{theme}\\theme.ini'):
        sm(f'The theme called \"{theme}\" exists.')
    else:
        theme = 'Default'
    appConfig.assignINIValue('General', 'sTheme', theme) #if there is no value set in Bethini.ini for sTheme:General
    global ThemeConfig
    ThemeConfig = ModifyINI('theme\\' + str(theme) + '\\theme.ini') #set the theme.ini file to be the INI file to modify for the ThemeConfig variable                                                          

    defaultFontName = "Segoe UI" #set the default font name
    defaultFontSize = 10 #set the default font size

    #set the font names and sizes
    global smallFontSize
    smallFontSize = ThemeConfig.getValue('Fonts','iSmallFontSize', defaultFontSize)
    global smallFont
    smallFont = (ThemeConfig.getValue('Fonts','sSmallFontName', defaultFontName), smallFontSize)

    #set the colors
    global buttonBarColor
    buttonBarColor = ThemeConfig.getValue('Colors','sButtonBarColor','#969696')
    global containerColor
    containerColor = ThemeConfig.getValue('Colors','sContainerColor','#555555')
    global subContainerColor
    subContainerColor = ThemeConfig.getValue('Colors','sSubContainerColor','#A5A5A5')
    global dropdownColor
    dropdownColor = ThemeConfig.getValue('Colors','sDropDownColor','#BEBEBE')
    global fieldColor
    fieldColor = ThemeConfig.getValue('Colors','sFieldColor','#FFFFFF')
    global indicatorColor
    indicatorColor = ThemeConfig.getValue('Colors','sIndicatorColor','#FFFFFF')
    global textColor
    textColor = ThemeConfig.getValue('Colors','sTextColor','#000000')

    global textColorDisabled
    textColorDisabled = ThemeConfig.getValue('Colors','sTextColorDisabled','#7F7F7F')
    global textColorPressed
    textColorPressed = ThemeConfig.getValue('Colors','sTextColorPressed','#323232')
    global textColorActive
    textColorActive = ThemeConfig.getValue('Colors','sTextColorActive','#000000')

    global backgroundColorDisabled
    backgroundColorDisabled = ThemeConfig.getValue('Colors','sBackgroundColorDisabled','#E1E1E1')
    global backgroundColorPressed
    backgroundColorPressed = ThemeConfig.getValue('Colors','sBackgroundColorPressed','#828282')
    global backgroundColorActive
    backgroundColorActive = ThemeConfig.getValue('Colors','sBackgroundColorActive','#A5A5A5')

class BethiniApp(tk.Tk):
    #This is the main app, the glue that creates the GUI.
    
    def __init__(self, *args, **kwargs):
        #You need args for lists and kwargs for dictionaries passed to tkinter
        tk.Tk.__init__(self, *args, **kwargs)

        #self.overrideredirect(True)
        tk.Tk.iconbitmap(self,default='Icon.ico') #sets the app icon

        #variables
        self.setupDictionary = {}
        self.tabDictionary = {}
        self.settingDictionary = {}
        self.dependentSettingsDictionary = {}
        self.settingsThatSettingsDependOn = {}
        self.tab = []

        self.widgetTypeFunction = {
            'Checkbutton': self.checkbox, 
            'preset': self.preset,
            'Dropdown': self.dropdown,
            'Entry': self.entry,
            'Spinbox': self.spinbox,
            'Combobox': self.combobox,
            'Color': self.color,
            'Slider': self.slider,
            'radioPreset': self.radioPreset
            }

        self.widgetTypeValue = {
            'TkCheckbutton': self.checkboxValue, 
            'TkOptionMenu': self.dropdownValue,
            'TkEntry': self.entryValue,
            'TkSpinbox': self.spinboxValue,
            'TkCombobox': self.comboboxValue,
            'TkColor': self.colorValue,
            'TkSlider': self.sliderValue,
            'TkRadioPreset': self.radioPresetValue
            }

        self.widgetTypeAssignValue = {
            'TkCheckbutton': self.checkboxAssignValue, 
            'TkOptionMenu': self.dropdownAssignValue,
            'TkEntry': self.entryAssignValue,
            'TkSpinbox': self.spinboxAssignValue,
            'TkCombobox': self.comboboxAssignValue,
            'TkColor': self.colorAssignValue,
            'TkSlider': self.sliderAssignValue
            }

        self.typesWithoutLabel = ['Checkbutton', 'preset', 'radioPreset', 'description']
        self.typesPackedLeft = ['Dropdown', 'Combobox', 'Entry', 'Spinbox', 'Slider', 'Color']

        
        theme_dir = appConfig.getValue('General', 'sTheme', 'Default')

        self.openINIs = {
            MyAppNameConfig : {
                'located': {
                    '1': {
                        'at': '',
                        'object': appConfig
                        }
                    }
                },
            'theme.ini': {
                'located': {
                    '1': {
                        'at': cwd + '\\theme\\' + theme_dir + '\\',
                        'object': ThemeConfig
                        }
                    }
                }
            }

        # ttk style overrides
        self.s = ttk.Style()
        self.s.theme_use('alt')
        self.s.configure(".", background=subContainerColor, font=smallFont, foreground=textColor, fieldbackground=fieldColor, arrowcolor=textColor)
        self.s.map('.',
                   foreground=[('disabled', textColorDisabled),
                               ('pressed', textColorPressed),
                               ('active', textColorActive)],
                   background=[('disabled', backgroundColorDisabled),
                               ('pressed', '!focus', backgroundColorPressed),
                               ('active', backgroundColorActive)])
        
        arrowSize = int(round(int(smallFontSize)*1.33,0))

        self.s.configure('TCheckbutton', indicatorcolor=indicatorColor)
        self.s.configure('TCombobox', arrowsize=arrowSize)
        self.s.configure('TSpinbox', arrowsize=arrowSize, background=dropdownColor)
        self.s.configure('TMenubutton', background=dropdownColor)
        self.s.configure('TCombobox', background=dropdownColor)
        self.s.configure('TNotebook', background=containerColor)
        self.s.configure('TRadiobutton', indicatorcolor=indicatorColor)
        self.s.configure('TNotebook.Tab', background=buttonBarColor, padding=[10,5])

        self.s.map('TNotebook.Tab',
                   background=[('!selected', backgroundColorDisabled)])

        self.option_add("*TCombobox*Font", smallFont)
        self.option_add("*TCombobox*Listbox*background", dropdownColor)
        self.option_add("*TCombobox*Listbox*foreground", textColor)
        self.option_add("*Menu*Font", smallFont)
        self.option_add("*Menu*background", dropdownColor)
        self.option_add("*Menu*foreground", textColor)

        #self.titleBar = tk.Frame(self, bg=containerColor, relief='raised', bd=2)
        #self.closeButton = ttk.Button(self.titleBar, text='✕', command=onClosing)


        
        self.theCanvas = tk.Canvas(self, borderwidth=0, background=containerColor, height=0, highlightthickness=0)
        self.hsbframeholder = ttk.Frame(self)

        self.vsb = AutoScrollbar(self, orient='vertical', command=self.theCanvas.yview)
        self.hsb = AutoScrollbar(self.hsbframeholder, orient='horizontal', command=self.theCanvas.xview)
        self.theCanvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        
        self.container = ttk.Frame(self.theCanvas)

        #self.titleBar.pack(expand=False, fill=tk.X)
        #self.closeButton.pack(side=tk.RIGHT)
        self.hsbframeholder.pack(side=tk.BOTTOM, fill=tk.X)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.theCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_frame = self.theCanvas.create_window((4,4), window=self.container, tags='self.container')
        

        self.container.bind('<Configure>', self.onFrameConfigure)


        self.subContainer = ttk.Notebook(self.container)
        self.subContainer.bind("<<NotebookTabChanged>>", self.TabChanged)
        self.subContainer.bind("<Configure>", self.subContainerConfigure)

        self.statusbarText = tk.StringVar(self)
        self.statusbar = ttk.Entry(self.hsbframeholder, textvariable=self.statusbarText)

        self.pw = ttk.Label(self.hsbframeholder, text='Loading... Please Wait... ')
        self.p = ttk.Progressbar(self.hsbframeholder, orient=tk.HORIZONTAL, mode='indeterminate')
        self.startProgress()
        self.showStatusBar()
        #upon initialization of the BethiniApp class, self.chooseGame() is
        #called first, so we select or return to the game/app we want to work with



        self.chooseGameWindow = tk.Toplevel(self)
        self.chooseGameWindow.title('Choose Game')

        self.chooseGameFrame = ttk.Frame(self.chooseGameWindow)

        self.chooseGameFrame2 = ttk.Frame(self.chooseGameFrame)

        self.chooseGameLabel = ttk.Label(self.chooseGameFrame2, text="Game/Application")

        OPTIONS = os.listdir('apps/')
        self.chooseGameVar = tk.StringVar(self)
        self.chooseGameDropdown = ttk.OptionMenu(self.chooseGameFrame2, self.chooseGameVar, "None", *OPTIONS, command= lambda g: self.chooseGameDone(g, True))
        self.chooseGameDropdown.var = self.chooseGameVar

        self.chooseGameFrame.pack(fill=tk.BOTH, expand=True)
        self.chooseGameFrame2.pack(anchor=tk.CENTER, expand=True)
        self.chooseGameLabel.pack(side=tk.LEFT, anchor=tk.CENTER, padx=5, pady=5)
        self.chooseGameDropdown.pack(anchor=tk.CENTER, padx=5, pady=5)
        self.chooseGameWindow.protocol("WM_DELETE_WINDOW", onClosing)
        self.chooseGameWindow.minsize(300,35)

        self.presetVar = tk.StringVar(self)
        self.presetVar.set('Bethini')

        self.chooseGame()

    def onFrameConfigure(self, event):
        self.theCanvas.configure(scrollregion=self.theCanvas.bbox('all'))

    def subContainerConfigure(self, event):
        theWidth = event.width + 17# + 35
        theHeight = event.height + 21# + 65
        self.geometry(f'{theWidth}x{theHeight}')

    def startProgress(self):
        self.pw.pack(side=tk.LEFT, anchor=tk.S)
        self.p.pack(expand=True, fill=tk.X, anchor=tk.S)
        self.p.start()

    def stopProgress(self):
        self.pw.destroy()
        self.p.stop()
        self.p.destroy()
        self.pw = ttk.Label(self.hsbframeholder, text='Loading... Please Wait... ')
        self.p = ttk.Progressbar(self.hsbframeholder, orient=tk.HORIZONTAL, mode='indeterminate')

    def sme(self, message, exception=False):
        sm(message, exception)
        self.statusbarText.set(message)
        self.update()

    def showSubContainer(self):
        self.subContainer.pack(fill=tk.BOTH, expand=True)

    def showStatusBar(self):
        self.statusbar.pack(anchor='w', side=tk.BOTTOM, fill=tk.X)

    def chooseColor(self, buttonToModify, colorValueType='hex'):
        #This allows us to have our very convenient tkinter colorchooser dialog
        #window modify a button
        oldColor = buttonToModify.var.get()
        if colorValueType == 'rgb':
            oldColor = RGBToHex(ast.literal_eval(oldColor))
        elif colorValueType == 'rgb 1':
            #"(1.0000, 1.0000, 1.0000)"
            #(255, 255, 255)
            oldColor = tuple(int(float(i)*255) for i in ast.literal_eval(oldColor))
        elif colorValueType == 'decimal':
            oldColor = RGBToHex(DecimalToRGB(oldColor))

        try:
            newColor = colorchooser.askcolor(color = oldColor)[1].upper()
        except:
            #self.sme('Cancelled change of color.', exception=1)
            newColor = oldColor

        RGB = HexToRGB(newColor)
        luminance = 0.299*RGB[0] + 0.587*RGB[1] + 0.114*RGB[2]
        if luminance < 128:
            textColor = '#FFFFFF'
        else:
            textColor = '#000000'
        buttonToModify.configure(bg=newColor, activebackground=newColor, fg=textColor)
        if colorValueType == 'rgb':
            buttonToModify.var.set(str(HexToRGB(newColor)).replace(' ',''))
        elif colorValueType == 'rgb 1':
            #(255, 255, 255)
            #"(1.0000, 1.0000, 1.0000)"
            theRGB = str(tuple(round(i/255,4) for i in HexToRGB(newColor)))
            buttonToModify.var.set(theRGB)
        elif colorValueType == 'decimal':
            buttonToModify.var.set(HexToDecimal(newColor))
        else:
            buttonToModify.var.set(newColor)
        preferencesWindow.lift()
        return newColor

    def tooltip(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id):
        CreateToolTip(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id],
                      self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["tooltip"])

    def chooseGame(self, forced=0):
        self.withdraw()
        # The Choose App/Game dialog window.  The window is skipped here if
        # sAppName is already set in the Bethini.ini file.
        try:
            chooseGameVar = appConfig.getValue('General','sAppName')
            if forced == 1:
                self.sme('Force choose game/application.')
                raise Exception("Forcing you to choose")
            if appConfig.getValue('General', 'bAlwaysSelectGame', '0') == '1':
                self.sme('Force choose game/application at startup.')
                gameName #By calling the global variable gameName before it has been created, we raise
                         #an exception to force the app/game to be chosen only
                                                 #at startup.
            #raise Exception("Forcing you to choose")
            self.chooseGameDone(chooseGameVar)
        except:
            self.sme('Choose game/application.', exception=1)
            self.chooseGameWindow.deiconify()

    def chooseGameDone(self, game, fromChooseGameWindow=False):
        self.chooseGameWindow.withdraw()
        
        # Once the app/game is selected, this loads it.
        try:
            self.chooseGameVar = appConfig.getValue('General','sAppName')
            if self.chooseGameVar != game:
                self.sme(f'Change of game from {self.chooseGameVar} to {game}')
                raise Exception("App/Game specified in " + MyAppNameConfig + " differs from the game chosen, so it will be changed to the one you chose.")
        except:
            self.sme('Change of game/application', exception=1)
            appConfig.assignINIValue('General','sAppName', game)
            fromChooseGameWindow = True

        tk.Tk.wm_title(self, MyAppName + " - " + game)

        ##############
        # app globals
        ##############

        global app
        app = appName(game)
        global gameName
        gameName = app.gameName()
        self.sme(f'Application/game is {gameName}')

        #######
        # Tabs
        #######

        tabs = app.tabs()

        #The self.tabDictionary lists all the tabs, which
        #is variable, based upon the tabs listed in the associated Bethini.json
        
        for tab in self.tabDictionary:
            if self.tabDictionary[tab]['Name'] == 'Setup':
                try:
                    self.tabDictionary[tab]['SetupWindow'].destroy()
                except:
                    TkFrame = self.tabDictionary[tab].get('TkFrameForTab')
                    if TkFrame:
                        TkFrame.destroy()
            else:
                TkFrame = self.tabDictionary[tab].get('TkFrameForTab')
                if TkFrame:
                    TkFrame.destroy()

        self.tabDictionary = {}
        tabNumber = 0
        for tab in tabs:
            tabNumber += 1
            self.tabDictionary["Page" + str(tabNumber)] = {"Name":tab}

        
        self.setupDictionary = {}
        self.settingDictionary = {}
        self.dependentSettingsDictionary = {}
        self.settingsThatSettingsDependOn = {}
        self.tab = []

        self.menu()
        if not fromChooseGameWindow:
            self.deiconify()
        self.createTabs(fromChooseGameWindow)

    def menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command = self.SaveINIFiles)
        filemenu.add_separator()
        filemenu.add_command(label="Choose game", command = lambda: self.chooseGame(forced=1))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=onClosing)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Preferences", command = self.showPreferences)
        editmenu.add_command(label="Setup", command = self.showSetup)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Visit Web Page", command = lambda: webbrowser.open_new_tab('http://www.nexusmods.com/skyrimspecialedition/mods/4875/'))
        helpmenu.add_command(label="Get Support", command = lambda: webbrowser.open_new_tab('https://stepmodifications.org/forum/forum/200-Bethini-support/'))
        helpmenu.add_command(label="About", command = self.About)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Help", menu=helpmenu)
        tk.Tk.config(self, menu=menubar)

    def showPreferences(self):
        preferencesWindow.deiconify()

    def withdrawPreferences(self):
        preferencesWindow.withdraw()

    def About(self):
        AboutWindow = tk.Toplevel(self)
        AboutWindow.title('About')

        AboutFrame = ttk.Frame(AboutWindow)
        AboutFrameReal = ttk.Frame(AboutFrame)

        AboutLabel = ttk.Label(AboutFrameReal, text=f'About {MyAppName}\n\n{MyAppName} was created by DoubleYou.\n\nLicensing is CC by-NC-SA.', justify=tk.CENTER)

        AboutFrame.pack(fill=tk.BOTH, expand=True)
        AboutFrameReal.pack(anchor=tk.CENTER, expand=True)
        AboutLabel.pack(anchor=tk.CENTER, padx='10', pady='10')

    def showSetup(self):
        self.withdraw()
        setupWindow.deiconify()

    def withdrawSetup(self):
        setupWindow.withdraw()
        self.deiconify()
        self.updateValues()

    def SaveINIFiles(self):
        #self.openINIs = {
        #    MyAppNameConfig : {
        #        'located': {
        #            '1': {
        #                'at': '',
        #                'object': appConfig
        #                }
        #            }
        #        }
        #    }
        firstTimeBackup = False
        filesSaved = False
        self.removeInvalidSettings()
        TheOpenedINIs = self.openINIs
        INIList = list(TheOpenedINIs.keys())
        filesToRemove = INIList[2:]
        filesToRemove.append('log.log')
        for INI in TheOpenedINIs:
            locationList = list(TheOpenedINIs[INI]['located'].keys())
            for n in range(len(locationList)):
                thisLocation = TheOpenedINIs[INI]['located'][str(n+1)].get('at')
                thisINIObject = TheOpenedINIs[INI]['located'][str(n+1)].get('object')
                if INI == MyAppNameConfig:
                    continue
                if not thisINIObject.HasBeenModified:
                    self.sme(f'{INI} has not been modified, so there is no reason to resave it.')
                    continue
                if messagebox.askyesno(f"Save {INI}", f"Do you want to save {thisLocation}{INI}?"):
                    #we need to make a backup of each save before actually saving.
                    if INI != 'theme.ini':
                        firstTimeBackupTrigger = removeExcessDirFiles(f'{thisLocation}{MyAppName} backups', int(appConfig.getValue('General', 'iMaxBackups', '-1')), filesToRemove)
                        if firstTimeBackupTrigger:
                            firstTimeBackup = True
                        if firstTimeBackup:
                            theBackupDirectory = f'{thisLocation}\\{MyAppName} backups\\First-Time-Backup\\'
                            if not os.path.isdir(theBackupDirectory):
                                os.makedirs(theBackupDirectory)
                            if os.path.exists(f"{theBackupDirectory}{INI}"):
                                self.sme(f'{theBackupDirectory}{INI} exists, so it will not be overwritten.')
                            else:
                                copyfile(f"{thisLocation}{INI}", f"{theBackupDirectory}{INI}")
                            copyfile(MyAppNameLog, f"{theBackupDirectory}log.log")
                        theBackupDirectory = f'{thisLocation}\\{MyAppName} backups\\{logDirectoryDate}\\'
                        if not os.path.isdir(theBackupDirectory):
                            os.makedirs(theBackupDirectory)
                        if os.path.exists(f"{theBackupDirectory}{INI}"):
                            self.sme(f'{theBackupDirectory}{INI} exists, so it will not be overwritten.')
                        else:
                            copyfile(f"{thisLocation}{INI}", f"{theBackupDirectory}{INI}")
                        copyfile(MyAppNameLog, f"{theBackupDirectory}log.log")
                    thisINIObject.writeINI(1)
                    filesSaved = True
                    self.sme(f"{thisLocation}{INI} saved.")
        if not filesSaved:
            self.sme('No files were modified.')
                        
    def setPreset(self, presetid):
        self.startProgress()
        if presetid == "Default":
            self.applyINIDict(app.presetValues('default'))
            self.removeINIDict(app.canRemove())
            self.applyINIDict(app.presetValues('fixedDefault'))
            presetVar = ""
        elif presetid == "recommended":
            presetDict = app.presetValues(f'{presetid}')
            self.applyINIDict(presetDict)
            presetVar = ""
        else:
            presetVar = self.presetVar.get()
            presetDict = app.presetValues(f'{presetVar} {presetid}')
            self.applyINIDict(presetDict)
        self.stopProgress()
        self.updateValues()
        self.sme(f"Preset {presetVar} {presetid} applied.")

    def removeInvalidSettings(self):
        TheOpenedINIs = self.openINIs
        
        for INI in TheOpenedINIs:
            if INI == MyAppNameConfig or INI == 'theme.ini':
                continue
            elif app.INIs(INI):
                locationList = list(TheOpenedINIs[INI]['located'].keys())
                for n in range(len(locationList)):
                    thisLocation = TheOpenedINIs[INI]['located'][str(n+1)].get('at')
                    thisINIObject = TheOpenedINIs[INI]['located'][str(n+1)].get('object')

                    sections = thisINIObject.getSections()

                    for section in sections:
                        settings = thisINIObject.getSettings(section)
                        if settings == []:
                            thisINIObject.removeSection(section)
                            self.sme(f'{section} was removed because it was empty.')
                        else:
                            for setting in settings:
                                if ';' in setting:
                                    self.sme(f'{setting}:{section} will be preserved, as it is a comment.')
                                elif not app.doesSettingExist(INI, section, setting):
                                    thisINIObject.removeSetting(section, setting)
                                    self.sme(f'{setting}:{section} was removed because it is not recognized.')                       

    def applyINIDict(self, INIDict):
        presetsIgnoreTheseSettings = app.presetsIgnoreTheseSettings()
        for eachSetting in INIDict:
            if eachSetting in presetsIgnoreTheseSettings:
                continue
            targetINI = INIDict[eachSetting]['ini']
            targetSection = INIDict[eachSetting]['section']
            thisValue = str(INIDict[eachSetting]['value'])

            INILocation = app.INIs(targetINI)
            if INILocation != '':
                INILocation = appConfig.getValue('Directories', INILocation)
            theTargetINI = self.openINI(str(INILocation), str(targetINI))

            theTargetINI.assignINIValue(targetSection, eachSetting, thisValue)
            self.sme(targetINI + " [" + targetSection + "] " + eachSetting + "=" + thisValue)

    def removeINIDict(self, INIDict):
        for eachSetting in INIDict:
            targetINI = INIDict[eachSetting]['ini']
            targetSection = INIDict[eachSetting]['section']
            thisValue = str(INIDict[eachSetting]['value'])

            INILocation = app.INIs(targetINI)
            if INILocation != '':
                INILocation = appConfig.getValue('Directories', INILocation)
            theTargetINI = self.openINI(str(INILocation), str(targetINI))

            currentValue = theTargetINI.getValue(targetSection, eachSetting, thisValue)

            if currentValue == thisValue:
                theTargetINI.removeSetting(targetSection, eachSetting)
                self.sme(f"{targetINI} [{targetSection}] {eachSetting}={thisValue}, which is the default value, and since it is not set to alwaysPrint, it will be removed")

    def createTabImage(self, eachTab):
        try:
            self.tabDictionary[eachTab]["TkPhotoImageForTab"] = tk.PhotoImage(file = "theme\\" + theme + "\\" + self.tabDictionary[eachTab]["Name"] + ".png")
        except:
            self.sme('No theme image for tab.', exception=1)
            self.tabDictionary[eachTab]["TkPhotoImageForTab"] = tk.PhotoImage(file = "theme\\" + theme + "\\Blank.png")

    def labelFramesForTab(self, eachTab):
        theDict = self.tabDictionary[eachTab]
        theDict["LabelFrames"] = {}
        labelFrameNumber=0
        for labelFrame in app.labelFramesInTab(theDict["Name"]):
            labelFrameNumber += 1
            TheLabelFrame="LabelFrame"+str(labelFrameNumber)
            theDict["LabelFrames"][TheLabelFrame] = {"Name":labelFrame}
            if "NoLabelFrame" not in labelFrame:
                theDict["LabelFrames"][TheLabelFrame]["TkLabelFrame"] = ttk.LabelFrame(theDict["TkFrameForTab"], text=labelFrame, width=200)
            else:
                theDict["LabelFrames"][TheLabelFrame]["TkLabelFrame"] = ttk.Frame(theDict["TkFrameForTab"])
            if (labelFrameNumber) % 2 == 0:
                theDict["LabelFrames"][TheLabelFrame]["TkLabelFrame"].pack(anchor=tk.CENTER, side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                theDict["LabelFrames"][TheLabelFrame]["TkLabelFrame"].pack(anchor=tk.CENTER, side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.settingFramesForLabelFrame(eachTab, labelFrame, TheLabelFrame)

    def settingFramesForLabelFrame(self, eachTab, labelFrame, TheLabelFrame):
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"] = {}
        NumberOfVerticallyStackedSettings = int(app.NumberOfVerticallyStackedSettings(self.tabDictionary[eachTab]["Name"], labelFrame))
        settingNumber = 0
        for setting in app.settingsInLabelFrame(self.tabDictionary[eachTab]["Name"], labelFrame):
            settingNumber += 1
            onFrame = "SettingFrame" + str(math.ceil(settingNumber / NumberOfVerticallyStackedSettings) - 1)
            if onFrame not in self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"]:
                self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame] = {}
                self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame]["TkSettingFrame"] = ttk.Frame(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["TkLabelFrame"])
                self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame]["TkSettingFrame"].pack(side=tk.LEFT, anchor='nw')
            TheSetting = "Setting" + str(settingNumber)
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting] = {"Name":setting}
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"] = ttk.Frame(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame]["TkSettingFrame"])
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"].pack(anchor='w', padx='5', pady='2')
            if 'Placeholder' not in setting:
                self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].update(app.getAllFieldsForSetting(self.tabDictionary[eachTab]["Name"], labelFrame, setting))
                self.settingLabel(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting)

    def settingLabel(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        settingType = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("type")
        if settingType not in self.typesWithoutLabel:
            if settingType:
                settingLabel = setting
            else:
                settingLabel = ''
            settingLabelWidth = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("customWidth")
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkLabel"] = ttk.Label(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                                   text=settingLabel, font=smallFont, width=settingLabelWidth, anchor=tk.E)
            if settingType in self.typesPackedLeft:
                self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkLabel"].pack(anchor=tk.CENTER, side=tk.LEFT, padx=5, pady=5)
            else:
                self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkLabel"].pack(anchor=tk.CENTER, padx=5, pady=5)
        settingDescription = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("Description")
        if settingDescription:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkDescriptionLabel"] = ttk.Label(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                                              text=settingDescription, font=smallFont, justify="left", wraplength=900)
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkDescriptionLabel"].pack(anchor=tk.N)
        self.settingTypeSwitcher(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, settingType)

    def settingTypeSwitcher(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, settingType):
        func = self.widgetTypeFunction.get(settingType, "Invalid")
        if func != "Invalid":
            func(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting)

    def widgetTypeSwitcher(self, setting):
        id = self.settingDictionary[setting].get('id')
        func = self.widgetTypeValue.get(id, "Invalid")
        if func != "Invalid":
            return func(setting)

    def addToSettingDictionary(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id):
        stuffToAddToSettingDictionary = {
            setting : {
                'eachTab': eachTab,
                'labelFrame': labelFrame,
                'TheLabelFrame': TheLabelFrame,
                'onFrame': onFrame,
                'TheSetting': TheSetting,
                'id': id,
                'TkWidget': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id],
                'targetINIs': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('targetINIs'),
                'settings': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('settings'),
                'targetSections': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('targetSections')
                }
            }

        self.settingDictionary.update(stuffToAddToSettingDictionary)

        dependentSettings = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('dependentSettings')
        if dependentSettings:
            self.dependentSettingsDictionary[setting] = dependentSettings

    def checkbox(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the Checkbutton widget
        id = "TkCheckbutton"
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        onValue = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("Onvalue")
        offValue = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("Offvalue")
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Checkbutton(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                              text=setting, variable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                              onvalue=onValue, offvalue=offValue)
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].var = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor='w', padx=5, pady=3.5)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'onvalue': onValue,
            'offvalue': offValue
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def preset(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates a preset button
        id = "TkPresetButton"

        presetid = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("preset id")
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Button(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                         text=setting, command=lambda: self.setPreset(presetid))
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=2)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)

    def radioPreset(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the radio preset button
        id = 'TkRadioPreset'
        value = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('value')
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Radiobutton(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                              text=setting,
                                                                                                                              variable=self.presetVar, value=value)
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=4)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.presetVar
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def dropdown(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the OptionMenu widget
        id = "TkOptionMenu"

        OPTIONS = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("choices")
                        
        #custom functions allow us to auto-detect certain
        #predefined options that can then easily be selected.

        if type(OPTIONS) == str:
            if 'FUNC' in OPTIONS:
                OptionString = app.custom(OPTIONS)
                if '{}' in OptionString:
                    customFunction = app.custom(f'{OPTIONS}Format')
                    valueToInsert = getattr(customFunctions, customFunction)(gameName)
                    OPTIONS = valueToInsert
        else:
            optionNumber = -1
            for option in OPTIONS:
                optionNumber += 1
                if 'FUNC' in OPTIONS[optionNumber]:
                    OptionString = app.custom(OPTIONS[optionNumber])
                    if '{}' in OptionString:
                        customFunction = app.custom(str(OPTIONS[optionNumber]) + 'Format')
                        valueToInsert = getattr(customFunctions, customFunction)(gameName)
                        OPTIONS[optionNumber] = OptionString.format(valueToInsert)

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.OptionMenu(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                             self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                             OPTIONS[0], *OPTIONS,
                                                                                                                             command=lambda c,var=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                             browse=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("browse"),
                                                                                                                             function=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("customFunction"):
                                                                                                                             var.set(browseToLocation(c, browse, function, gameName)))
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].var = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'OPTIONS': OPTIONS,
            'settingChoices': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('settingChoices'),
            'delimiter': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('delimiter'),
            'decimal places': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('decimal places'),
            'fileFormat': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('fileFormat'),
            'forceSelect': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('forceSelect'),
            'partial': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('partial')
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def combobox(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        id = 'TkCombobox'
        OPTIONS = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("choices")
        width = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("width")
        validate = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        
        if validate:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Combobox(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                           textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                           width=width, values=OPTIONS, validate='key', validatecommand=(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate))
        else:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Combobox(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                           textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                           width=width, values=OPTIONS)
        
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'OPTIONS': OPTIONS,
            'decimal places': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('decimal places')
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def entry(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the Entry widget
        id = "TkEntry"
        entryWidth = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("entryWidth")
        validate = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)

        if validate:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Entry(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=entryWidth, validate='key', font=smallFont,
                                                                                                                        validatecommand=(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        else:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Entry(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=entryWidth, font=smallFont,
                                                                                                                        textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'formula': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("formula"),
            'decimal places': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("decimal places"),
            'partial': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("partial"),
            'fileFormat': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("fileFormat")
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def slider(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        id = "TkSlider"
        fromV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("from")
        toV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("to")
        resolutionV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("resolution")
        digitsV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("digits")
        lengthV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("length")

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = tk.Scale(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        from_=fromV, to=toV, resolution=resolutionV, showvalue=0, digits=digitsV, orient=tk.HORIZONTAL, relief=tk.FLAT,
                                                                                                                        highlightthickness=0, bg=subContainerColor, length=lengthV, font=smallFont, activebackground=backgroundColorActive,
                                                                                                                        troughcolor=fieldColor,
                                                                                                                        variable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])

        width = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("width")
        validate = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")
        incrementV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("increment")

        reversed = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("reversed")
        if reversed:
            fromV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("to")
            toV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("from")

        if validate:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"] = ttk.Spinbox(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=width, validate='key', increment=incrementV, from_=fromV, to=toV, font=smallFont,
                                                                                                                        validatecommand=(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        else:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"] = ttk.Spinbox(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=width, increment=incrementV, from_=fromV, to=toV, font=smallFont,
                                                                                                                        textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, "TkWidgetTwo")
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'decimal places': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("decimal places"),
            'TkWidgetTwo': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"]
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def spinbox(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        id = "TkSpinbox"
        fromV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("from")
        toV = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("to")
        increment = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("increment")
        width = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("width")
        validate = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)

        if validate:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Spinbox(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        from_=fromV, to=toV, increment=increment, width=width, validate='key', font=smallFont,
                                                                                                                        validatecommand=(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        else:
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = ttk.Spinbox(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        from_=fromV, to=toV, increment=increment, width=width, font=smallFont,
                                                                                                                        textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def color(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #chooseColor(colorToChange, buttonToModify)
        id = "TkColor"

        colorValueType = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("colorValueType")

        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        if colorValueType == 'hex':
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('#FFFFFF')
        elif colorValueType == 'rgb':
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('(255, 255, 255)')
        elif colorValueType == 'rgb 1':
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('(1.0000, 1.0000, 1.0000)')
        elif colorValueType == 'decimal':
            self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('16777215')
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id] = tk.Button(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        textvariable=self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                        font=smallFont,
                                                                                                                        command=lambda: self.chooseColor(self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id],
                                                                                                                                                         colorValueType))
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].var = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
        self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'colorValueType': colorValueType,
            'rgbType': self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("rgbType")
            }
        self.settingDictionary[setting].update(stuffToAddToSettingDictionary)

    def radioPresetValue(self, setting):
        return self.presetVar.get()

    def checkboxValue(self, setting):
        settingValue = self.getSettingValues(self.settingDictionary[setting].get('targetINIs'),
                                             self.settingDictionary[setting].get('targetSections'),
                                             self.settingDictionary[setting].get('settings'))
        
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            onvalue = self.settingDictionary[setting].get('onvalue')
            offvalue = self.settingDictionary[setting].get('offvalue')
            if settingValue == onvalue:
                thisValue = onvalue
                self.settingDictionary[setting]["TkVar"].set(thisValue)
            elif settingValue == offvalue:
                thisValue = offvalue
                self.settingDictionary[setting]["TkVar"].set(thisValue)
            else:
                thisValue = []
                for n in range(len(settingValue)):
                    if settingValue[n] in onvalue[n]:
                        thisValue.append(1)
                    else:
                        thisValue.append(0)

                if all(thisValue):
                    thisValue = onvalue
                else:
                    thisValue = offvalue
                self.settingDictionary[setting]["TkVar"].set(thisValue)
            try:
                self.sme(f"{setting} = {thisValue}")
                self.settingDictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'No value set for checkbox {setting}.')

    def dropdownValue(self, setting):
        settingValue = self.getSettingValues(self.settingDictionary[setting].get('targetINIs'),
                                             self.settingDictionary[setting].get('targetSections'),
                                             self.settingDictionary[setting].get('settings'),
                                             self.settingDictionary[setting].get('settingChoices'), 
                                             self.settingDictionary[setting].get('delimiter'))

        if settingValue != [] and 'Does Not Exist' not in settingValue:
            decimalPlaces = self.settingDictionary[setting].get("decimal places")
            if decimalPlaces:
                decimalPlaces = int(decimalPlaces)
                thisValue = round(float(settingValue[0]), decimalPlaces)
                if decimalPlaces == 0:
                    thisValue = int(thisValue)
                self.settingDictionary[setting]["TkVar"].set(thisValue)
            else:
                fileFormat = self.settingDictionary[setting].get("fileFormat")
                if fileFormat:
                    thisValue = os.path.split(settingValue[0])
                    if fileFormat == "directory":
                        if thisValue[0] != '':
                            thisValue = thisValue[0]
                            if thisValue[-1] != '\\':
                                thisValue += '\\'
                        else:
                            thisValue = thisValue[0]
                    if fileFormat == "file":
                        thisValue = thisValue[1]
                    self.settingDictionary[setting]["TkVar"].set(thisValue)
                else:
                    settingChoices = self.settingDictionary[setting].get("settingChoices")
                    if settingChoices and settingValue[0] not in settingChoices:
                        thisValue = "Custom"
                        self.settingDictionary[setting]["TkVar"].set(thisValue)
                    else:
                        thisValue = settingValue[0]
                        self.settingDictionary[setting]["TkVar"].set(thisValue)
            self.sme(f"{setting} = {thisValue}")
            self.settingDictionary[setting]['valueSet'] = True
            return thisValue

    def comboboxValue(self, setting):
        settingValue = self.getSettingValues(self.settingDictionary[setting].get('targetINIs'),
                                             self.settingDictionary[setting].get('targetSections'),
                                             self.settingDictionary[setting].get('settings'))
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            thisValue = settingValue[0]

            decimalPlaces = self.settingDictionary[setting].get("decimal places")
            if decimalPlaces:
                decimalPlaces = int(decimalPlaces)
                thisValue = round(float(thisValue), decimalPlaces)
                if decimalPlaces == 0:
                    thisValue = int(thisValue)
            
            self.settingDictionary[setting]["TkVar"].set(thisValue)
            self.sme(f"{setting} = {thisValue}")
            self.settingDictionary[setting]['valueSet'] = True
            return thisValue

    def entryValue(self, setting):
        settingValue = self.getSettingValues(self.settingDictionary[setting].get('targetINIs'),
                                             self.settingDictionary[setting].get('targetSections'),
                                             self.settingDictionary[setting].get('settings'))
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            formula = self.settingDictionary[setting].get("formula")
            fileFormat = self.settingDictionary[setting].get("fileFormat")
            if formula:
                decimalPlaces = int(self.settingDictionary[setting].get("decimal places"))
                thisValue = round(eval(formula.format(settingValue[0])), decimalPlaces)
                if decimalPlaces == 0:
                    thisValue = int(thisValue)
            elif fileFormat:
                thisValue = settingValue[0]
                if fileFormat == "file":
                    thisValue = os.path.split(thisValue)
                    thisValue = thisValue[1]
            else:
                thisValue = settingValue[0]
            try:
                self.settingDictionary[setting]['TkVar'].set(thisValue)
                self.sme(f"{setting} = {thisValue}")
                self.settingDictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'No value set for entry {setting}.')

    def sliderValue(self, setting):
        settingValue = self.getSettingValues(self.settingDictionary[setting].get('targetINIs'),
                                             self.settingDictionary[setting].get('targetSections'),
                                             self.settingDictionary[setting].get('settings'))

        if settingValue != [] and 'Does Not Exist' not in settingValue:
            thisValue = settingValue[0]

            decimalPlaces = self.settingDictionary[setting].get("decimal places")
            if decimalPlaces:
                decimalPlaces = int(decimalPlaces)
                thisValue = round(float(thisValue), decimalPlaces)
                if decimalPlaces == 0:
                    thisValue = int(thisValue)
            
            try:
                self.settingDictionary[setting]['TkVar'].set(thisValue)
                self.sme(f'{setting} = {thisValue}')
                self.settingDictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'no value set for slider {setting}')

    def spinboxValue(self, setting):
        settingValue = self.getSettingValues(self.settingDictionary[setting].get('targetINIs'),
                                             self.settingDictionary[setting].get('targetSections'),
                                             self.settingDictionary[setting].get('settings'))
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            thisValue = settingValue[0]
            try:
                self.settingDictionary[setting]['TkVar'].set(thisValue)
                self.sme(f'{setting} = {thisValue}')
                self.settingDictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'no value set for spinbox {setting}')

    def colorValue(self, setting):
        settingValue = self.getSettingValues(self.settingDictionary[setting].get('targetINIs'),
                                             self.settingDictionary[setting].get('targetSections'),
                                             self.settingDictionary[setting].get('settings'))
        
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            colorValueType = self.settingDictionary[setting].get("colorValueType")
            if colorValueType == 'hex':
                thisValue = settingValue[0]
                newColor = thisValue
            elif colorValueType == 'decimal':
                thisValue = settingValue[0]
                #convert decimal value to hex
                newColor = RGBToHex(DecimalToRGB(settingValue[0]))
            elif colorValueType == 'rgb':
                rgbType = self.settingDictionary[setting].get("rgbType")
                if rgbType == 'multiple settings':
                    thisValue = tuple(int(i) for i in settingValue)
                    newColor = RGBToHex(thisValue)
                    thisValue = str(thisValue)
                else:
                    thisValue = '('
                    for n in range(len(settingValue)):
                        thisValue += settingValue[n]
                    thisValue += ')'
                    print(thisValue)
                    newColor = RGBToHex(ast.literal_eval(thisValue))
            elif colorValueType == 'rgb 1':
                rgbType = self.settingDictionary[setting].get("rgbType")
                if rgbType == 'multiple settings':
                    thisValue = tuple(round(float(i),4) for i in settingValue)
                    newColor = RGBToHex(tuple(int(float(i)*255) for i in settingValue))
                    thisValue = str(thisValue)
            self.settingDictionary[setting]['TkVar'].set(thisValue)
            TkWidget = self.settingDictionary[setting].get("TkWidget")
            RGB = HexToRGB(newColor)
            luminance = 0.299*RGB[0] + 0.587*RGB[1] + 0.114*RGB[2]
            if luminance < 128:
                textColor = '#FFFFFF'
            else:
                textColor = '#000000'
            TkWidget.configure(bg=newColor, activebackground=newColor, fg=textColor)
            self.sme(f"{setting} = {thisValue}")
            self.settingDictionary[setting]['valueSet'] = True
            return thisValue

    def checkDependents(self, setting):
        for dependentSetting in self.settingsThatSettingsDependOn[setting]:
            var = self.settingsThatSettingsDependOn[setting][dependentSetting].get('var')
            
            theOperator = self.settingsThatSettingsDependOn[setting][dependentSetting].get('theOperator')
            value = self.settingsThatSettingsDependOn[setting][dependentSetting].get('value')
            currentValue = self.widgetTypeSwitcher(setting)
            TkWidgetTwo = self.settingDictionary[dependentSetting].get('TkWidgetTwo')
            if var == 'float':
                value = float(value)
                currentValue = float(currentValue)
            if theOperator(currentValue, value):
                self.settingDictionary[dependentSetting]['TkWidget'].configure(state='normal')
                if TkWidgetTwo:
                    TkWidgetTwo.configure(state='normal')
            else:
                setToOff = self.settingsThatSettingsDependOn[setting][dependentSetting].get('setToOff')
                if setToOff:
                    offvalue = self.settingDictionary[dependentSetting].get('offvalue')

                    self.settingDictionary[dependentSetting]['TkVar'].set(offvalue)
                self.settingDictionary[dependentSetting]['TkWidget'].configure(state='disabled')
                if TkWidgetTwo:
                    TkWidgetTwo.configure(state='disabled')

    def assignValue(self, var, indx, mode, setting):
        id = self.settingDictionary[setting].get('id')
        func = self.widgetTypeAssignValue.get(id, "Invalid")
        if func != "Invalid":
            func(setting)
        
        if setting in list(self.settingsThatSettingsDependOn.keys()):
            self.checkDependents(setting)

    def checkboxAssignValue(self, setting):
        TkVar = self.settingDictionary[setting].get('TkVar')
        
        thisValue = TkVar.get()
        #thisValue is whatever the state of the onvalue/offvalue is... not a simple boolean


        targetINIs = self.settingDictionary[setting].get('targetINIs')
        targetSections = self.settingDictionary[setting].get('targetSections')
        theSettings = self.settingDictionary[setting].get('settings')
        
        onvalue = self.settingDictionary[setting].get('onvalue')
        offvalue = self.settingDictionary[setting].get('offvalue')

        settingValue = self.getSettingValues(targetINIs, targetSections, theSettings)

        try:
            thisValue = list(eval(thisValue))
            for n in range(len(thisValue)):
                if type(thisValue[n]) is tuple:
                    thisValue[n] = list(thisValue[n])
        except:
            self.sme(f'{thisValue} .... Make sure that the {setting} checkbutton Onvalue and Offvalue are lists within lists in the json.', exception=1)

        #print(thisValue, onvalue, offvalue)

        if targetINIs:
            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))
                #1
                if thisValue == onvalue or thisValue == offvalue:
                    if type(thisValue[n]) is list:
                        if settingValue[n] in thisValue[n]:
                            theValue = settingValue[n]
                        elif thisValue[n][0] in self.settingDictionary:
                            self.assignValue(1,2,3, thisValue[n][0])
                            continue
                        else:
                            theValue = thisValue[n][0]
                            theTargetINI.assignINIValue(targetSections[n], theSettings[n], theValue)
                            self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                        theTargetINI.assignINIValue(targetSections[n], theSettings[n], theValue)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                    else:
                        theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue[n])
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue[n])

    def dropdownAssignValue(self, setting):
        TkVar = self.settingDictionary[setting].get('TkVar')
        thisValue = TkVar.get()
        #print(thisValue)
        targetINIs = self.settingDictionary[setting].get('targetINIs')
        targetSections = self.settingDictionary[setting].get('targetSections')
        theSettings = self.settingDictionary[setting].get('settings')

        settingChoices = self.settingDictionary[setting].get('settingChoices')
        delimiter = self.settingDictionary[setting].get('delimiter')
        fileFormat = self.settingDictionary[setting].get('fileFormat')
        decimalPlaces = self.settingDictionary[setting].get('decimal places')
        partial = self.settingDictionary[setting].get('partial')
        theValueStr = ''
        if partial:
            for eachSetting in partial:
                if eachSetting == setting:
                    theValueStr += '{}'
                else:
                    try:
                        if self.settingDictionary[eachSetting]['valueSet']:
                            theValueStr += self.settingDictionary[eachSetting]['TkVar'].get()
                        else:
                            self.sme(f'{eachSetting} is not set yet.')
                            return
                    except:
                        self.sme(f'{eachSetting} is not set yet.', exception=True)
                        return

        
        if targetINIs:
            for n in range(len(targetINIs)):
                theValue = ''
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))
                #1280x720
                if delimiter:
                    listOfValues = thisValue.split(delimiter)
                    theValue = listOfValues[n]
                elif settingChoices:
                    if thisValue not in settingChoices:
                        return
                    else:
                        theValue = settingChoices[thisValue][n]
                elif fileFormat:
                    if fileFormat == 'directory':
                        if thisValue == '\\':
                            thisValue = thisValue[:-1]
                    theValue = thisValue
                else:
                    theValue = thisValue

                if partial:
                    theValue = theValueStr.format(thisValue)
                theTargetINI.assignINIValue(targetSections[n], theSettings[n], theValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)

    def comboboxAssignValue(self, setting):
        targetINIs = self.settingDictionary[setting].get('targetINIs')

        if targetINIs:
            TkVar = self.settingDictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.settingDictionary[setting].get('targetSections')
            theSettings = self.settingDictionary[setting].get('settings')

            decimalPlaces = self.settingDictionary[setting].get('decimal places')
            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                if decimalPlaces and thisValue != '':
                    thisValue = round(float(thisValue),int(decimalPlaces))
                    if decimalPlaces == "0":
                        thisValue = int(thisValue)
                    thisValue = str(thisValue)

                theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)

    def entryAssignValue(self, setting):
        targetINIs = self.settingDictionary[setting].get('targetINIs')
       
        partial = self.settingDictionary[setting].get('partial')
        theValueStr = ''
        if partial:
            for eachSetting in partial:
                if eachSetting == setting:
                    theValueStr += '{}'
                else:
                    #self.widgetTypeSwitcher(eachSetting)
                    if self.settingDictionary[eachSetting]['valueSet']:
                        theValueStr += self.settingDictionary[eachSetting]['TkVar'].get()
                    else:
                        return

        if targetINIs:
            TkVar = self.settingDictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.settingDictionary[setting].get('targetSections')
            theSettings = self.settingDictionary[setting].get('settings')

            formula = self.settingDictionary[setting].get('formula')
            #decimalPlaces = self.settingDictionary[setting].get('decimal places')

            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                if formula:
                    formulaValue = formula.format(thisValue)
                    try:
                        thisValue = str(round(float(sum(Fraction(s) for s in formulaValue.split())),8))
                    except:
                        thisValue = thisValue
                #if decimalPlaces:
                #    thisValue = round(thisValue,int(decimalPlaces))

                if partial:
                    thisValue = theValueStr.format(thisValue)
                theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)

    def sliderAssignValue(self, setting):
        targetINIs = self.settingDictionary[setting].get('targetINIs')

        if targetINIs:
            TkVar = self.settingDictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.settingDictionary[setting].get('targetSections')
            theSettings = self.settingDictionary[setting].get('settings')

            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)

    def spinboxAssignValue(self, setting):
        targetINIs = self.settingDictionary[setting].get('targetINIs')
        
        if targetINIs:
            TkVar = self.settingDictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.settingDictionary[setting].get('targetSections')
            theSettings = self.settingDictionary[setting].get('settings')

            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)

    def colorAssignValue(self, setting):
        targetINIs = self.settingDictionary[setting].get('targetINIs')
        
        if targetINIs:
            TkVar = self.settingDictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.settingDictionary[setting].get('targetSections')
            theSettings = self.settingDictionary[setting].get('settings')

            colorValueType = self.settingDictionary[setting].get("colorValueType")
            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                if colorValueType == 'hex':
                    theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                    self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)
                elif colorValueType == 'decimal':
                    theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                    self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)
                elif colorValueType == 'rgb' or colorValueType == 'rgb 1':
                    if len(theSettings) > 1:
                        theValue = str(ast.literal_eval(thisValue)[n])
                        theTargetINI.assignINIValue(targetSections[n], theSettings[n], theValue)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                    else:
                        thisValue = thisValue.lstrip('(').rstrip(')')
                        theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)
                
    def createTabs(self, fromChooseGameWindow=False):
        
        for eachTab in self.tabDictionary:
            #eachTab is Page1, Page2, etc.
            #self.tabDictionary[eachTab]["Name"] is the name of each tab

            self.createTabImage(eachTab)
            if self.tabDictionary[eachTab]['Name'] == 'Setup':
                global setupWindow
                self.tabDictionary[eachTab]['SetupWindow'] = tk.Toplevel(self)
                setupWindow = self.tabDictionary[eachTab]['SetupWindow']
                setupWindow.title('Setup')
                self.tabDictionary[eachTab]["TkFrameForTab"] = ttk.Frame(setupWindow)
                self.tabDictionary[eachTab]["TkFrameForTab"].pack()
                setupWindow.protocol("WM_DELETE_WINDOW", self.withdrawSetup)
                if not fromChooseGameWindow:
                    setupWindow.withdraw()
            elif self.tabDictionary[eachTab]['Name'] == 'Preferences':
                global preferencesWindow
                self.tabDictionary[eachTab]['PreferencesWindow'] = tk.Toplevel(self)
                preferencesWindow = self.tabDictionary[eachTab]['PreferencesWindow']
                preferencesWindow.title('Preferences')
                self.tabDictionary[eachTab]["TkFrameForTab"] = ttk.Frame(preferencesWindow)
                self.tabDictionary[eachTab]["TkFrameForTab"].pack()
                preferencesWindow.protocol("WM_DELETE_WINDOW", self.withdrawPreferences)
                preferencesWindow.withdraw()
            else:
                self.tabDictionary[eachTab]["TkFrameForTab"] = ttk.Frame(self.subContainer)
                self.subContainer.add(self.tabDictionary[eachTab]["TkFrameForTab"], text=self.tabDictionary[eachTab]["Name"], image=self.tabDictionary[eachTab]["TkPhotoImageForTab"], compound=tk.TOP)

            #self.tabDictionary[eachTab]["TkFrameForTab"] = ttk.Frame(self.subContainer)
            #self.subContainer.add(self.tabDictionary[eachTab]["TkFrameForTab"], text=self.tabDictionary[eachTab]["Name"], image=self.tabDictionary[eachTab]["TkPhotoImageForTab"], compound=tk.TOP)
            
            self.labelFramesForTab(eachTab)
            
        self.stopProgress()
        if not fromChooseGameWindow:
            self.updateValues()
        self.startProgress()
        self.bindTkVars()
        
        #self.theCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.showSubContainer()
        #self.showStatusBar()
        self.stopProgress()
        self.sme('Loading complete.')
        
    def bindTkVars(self):
        for eachSetting in self.settingDictionary:
            TkVar = self.settingDictionary[eachSetting].get('TkVar')
            if TkVar:
                self.settingDictionary[eachSetting]["TkVar"].trace_add('write', lambda var, indx, mode, setting=eachSetting:self.assignValue(var, indx, mode, setting))
            forceSelect = self.settingDictionary[eachSetting].get('forceSelect')
            if forceSelect:
                self.assignValue(1, 2, 3, eachSetting)

    def updateValues(self):
        self.startProgress()
        self.sme('Updating INI values.')
        for eachSetting in self.settingDictionary:
            self.widgetTypeSwitcher(eachSetting)
        self.sme('Checking for dependent settings.')
        self.dependents()
        self.sme('Update values complete.')
        self.stopProgress()

    def dependents(self):
        #self.dependentSettingsDictionary
        for setting in self.dependentSettingsDictionary:
            for masterSetting in self.dependentSettingsDictionary[setting]:
                
                theOperator = self.dependentSettingsDictionary[setting][masterSetting].get('operator')
                setToOff = self.dependentSettingsDictionary[setting][masterSetting].get('setToOff', False)
                if theOperator == 'equal' or theOperator == 'not-equal':
                    value = self.dependentSettingsDictionary[setting][masterSetting].get('value')
                    currentValue = self.widgetTypeSwitcher(masterSetting)
                    var = 'string'
                else:
                    value = float(self.dependentSettingsDictionary[setting][masterSetting].get('value'))
                    currentValue = float(self.widgetTypeSwitcher(masterSetting))
                    var = 'float'
                theOperator = operatorDict[theOperator]
                TkWidgetTwo = self.settingDictionary[setting].get('TkWidgetTwo')
                if theOperator(currentValue, value):
                    self.settingDictionary[setting]['TkWidget'].configure(state='normal')
                    if TkWidgetTwo:
                        TkWidgetTwo.configure(state='normal')
                else:
                    if setToOff:
                        offvalue = self.dependentSettingsDictionary[setting][masterSetting].get('offvalue')
                        self.settingDictionary[setting]['TkVar'].set(offvalue)
                    self.settingDictionary[setting]['TkWidget'].configure(state='disabled')
                    if TkWidgetTwo:
                        TkWidgetTwo.configure(state='disabled')

                if not self.settingsThatSettingsDependOn.get(masterSetting):
                    self.settingsThatSettingsDependOn[masterSetting] = {}

                self.settingsThatSettingsDependOn[masterSetting][setting] = {
                    'theOperator': operatorDict[self.dependentSettingsDictionary[setting][masterSetting].get('operator')],
                    'value': value,
                    'var': var,
                    'setToOff': setToOff
                    }

    def validate(self, valueChangedTo, valueWas, validate):
        badValue = f"\"{valueChangedTo}\" is an invalid value for this option."
        if validate == 'integer':
            try:
                if valueChangedTo == '':
                    return True
                elif str(abs(int(valueChangedTo))).isdigit():
                    return True
                else:
                    self.sme(badValue)
                    return False
            except:
                self.sme(badValue)
                return False
        elif validate == 'whole':
            if valueChangedTo == '':
                return True
            elif valueChangedTo.isdigit():
                return True
            else:
                self.sme(badValue)
                return False
        elif validate == 'counting':
            if valueChangedTo == '':
                return True
            elif valueChangedTo == '0':
                self.sme(badValue)
                return False
            elif valueChangedTo.isdigit():
                return True
            else:
                self.sme(badValue)
                return False
        elif validate == 'float':
            if valueChangedTo == '':
                return True
            try:
                float(valueChangedTo)
                return True
            except:
                self.sme(badValue)
                return False
        else:
            return True

    def getINILocation(self, ini):
        INILocation = app.INIs(ini)
        if INILocation == '':
            INILocation == ''
        elif INILocation == 'sTheme':
            theme_dir = appConfig.getValue('General', 'sTheme', 'Default')
            INILocation = f'{cwd}\\theme\\{theme_dir}\\'
        else:
            INILocation = appConfig.getValue('Directories', INILocation)
        return INILocation

    def getSettingValues(self, targetINIs, targetSections, theSettings, settingChoices=None, delimiter=None):
        #This function returns the current value of the setting.

        #What it needs:
        #targetINIs
        #settings
        #targetSections
        #settingChoices
        #delimiter

        settingValues = []
        #targetINIs = self.tabDictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("targetINIs")
        if targetINIs:
            ININumber = -1
            for INI in targetINIs:
                ININumber += 1
                #Get the Bethini.ini key for the location of the target INI
                INILocation = self.getINILocation(INI)
                if INILocation != "Does Not Exist":
                    #If the INI location is known.

                    currentSetting = theSettings[ININumber]
                    currentSection = targetSections[ININumber]

                    # This looks for a default value in the settings.json
                    if INI == MyAppNameConfig or INI == 'theme.ini':
                        defaultValue = "Does Not Exist"
                    else:
                        defaultValue = app.getValue(currentSetting, "default")

                    #targetINI = ModifyINI(str(INILocation) + str(INI))

                    targetINI = self.openINI(str(INILocation), str(INI))
                    value = str(targetINI.getValue(currentSection, currentSetting, default=defaultValue))
                    settingValues.append(value)
            if settingValues != []:
                 #Check to see if the settings correspond with specified
                 #setting choices.
                 if settingChoices:
                     for choice in settingChoices:
                         if settingChoices[choice] == settingValues:
                             settingValues = [choice]

                 #Check to see if there are multiple values separated by a
                 #delimiter
                 if delimiter:
                     delimitedValue = ''
                     for n in range(len(settingValues)):
                        if n != len(settingValues) - 1:
                            delimitedValue += settingValues[n] + delimiter
                        else:
                            delimitedValue += settingValues[n]
                     settingValues = [delimitedValue]

        return settingValues

    def openINI(self, location, INI):
        openINI = self.openINIs.get(INI)
        if openINI:
            openINIlocation = self.openINIs[INI]['located']
            id = 0
            for eachLocation in openINIlocation:
                id += 1
                if openINIlocation[eachLocation]['at'] == location:
                    return openINIlocation[eachLocation].get('object')
            #if the location is not found, add it
            id += 1
            id = str(id)
            self.openINIs[INI]['located'][id] = {
                'at':location
                }
            self.openINIs[INI]['located'][id]['object'] = ModifyINI(location + INI)
            return self.openINIs[INI]['located'][id]['object']
        else:
            id = "1"
            self.openINIs[INI] = {
                'located': {
                    id: {
                        'at': location
                        }
                    }
                }
            self.openINIs[INI]['located'][id]['object'] = ModifyINI(location + INI)
            return self.openINIs[INI]['located'][id]['object']

    def TabChanged(self, event):
        return
        #selectedTab = event.widget.select()
        #tabName = event.widget.tab(selectedTab, "text")
        #if len(self.tab) == 0:
        #    self.tab.insert(0, tabName)
        #elif len(self.tab) == 1:
        #    self.tab.insert(1, tabName)
        #else:
        #    self.tab[0] = self.tab[1]
        #    self.tab[1] = tabName
        #if len(self.tab) > 1 and self.tab[1] != self.tab[0] and self.tab[0] == 'Setup':
        #    self.updateValues()

def onClosing():
    if messagebox.askyesno("Quit?", "Do you want to quit?"):
        if appConfig.HasBeenModified:
            appConfig.writeINI(1)
        window.SaveINIFiles()
        window.quit()

def removeExcessDirFiles(dir, maxToKeep, filesToRemove):
    try:
        sub = os.listdir(dir)
    except OSError as e:
        sm("Error: %s : %s" % (dir, e.strerror))
        return True
    sub.sort(reverse=True)
    if 'First-Time-Backup' in sub:
        sub.remove('First-Time-Backup')
    if maxToKeep > -1:
        for n in range(len(sub)):
            if n < maxToKeep:
                sm(sub[n] + ' will be kept.')
            else:
                dir_path = f'{dir}\\' + sub[n]
                try:
                    for file in filesToRemove:
                        try:
                            os.remove(f'{dir_path}\\{file}')
                        except OSError as e:
                            sm(f'Error: {dir_path}\\{file} : {e.strerror}')
                    os.rmdir(dir_path)
                    sm(sub[n] + ' was removed.')
                except OSError as e:
                    sm("Error: %s : %s" % (dir_path, e.strerror))
    return False



cwd = os.getcwd()

operatorDict = {
    'greater-than': gt,
    'greater-or-equal-than': ge,
    'less-than': lt,
    'less-or-equal-than': le,
    'not-equal': ne,
    'equal': eq
    }

MyAppName = "Bethini Pie"
MyAppShortName = "Bethini"

today = datetime.now()
logDirectoryDate = today.strftime("%Y %b %d %a - %H.%M.%S")
MyAppNameLogDirectory = f'logs\\{logDirectoryDate}'
MyAppNameLog = f'{MyAppNameLogDirectory}\\log.log'
MyAppNameConfig = f'{MyAppShortName}.ini'



if __name__ == '__main__':
    os.makedirs(MyAppNameLogDirectory)

    logging.basicConfig(filename=MyAppNameLog, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    appConfig = ModifyINI(MyAppNameConfig)
    iMaxLogs = appConfig.getValue('General', 'iMaxLogs', '5')
    appConfig.assignINIValue('General', 'iMaxLogs', iMaxLogs)
    removeExcessDirFiles(f'{cwd}\\logs', int(iMaxLogs), ['log.log'])

    appConfig.assignINIValue('General', 'iMaxBackups', appConfig.getValue('General', 'iMaxBackups', '5'))

    #get the initial values and then add to it by assignment upon changing.
    loadTheme()

    window = BethiniApp()
    #window.geometry('980x720')
    #window.minsize(400,35)
    window.protocol("WM_DELETE_WINDOW", onClosing)
    window.mainloop()

