#
#This work is licensed under the
#Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
#or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import ast
import os
import math
import logging
import webbrowser
from shutil import copyfile
from datetime import datetime
from operator import gt, ge, lt, le, ne, eq
#from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR, S_IWGRP, S_IWRITE
#This is for changing file read-only access via os.chmod(filename, S_IREAD,
#S_IRGRP, #S_IROTH) Not currently used.

import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from tkinter import messagebox

from simpleeval import simple_eval

from lib.app import AppName
from lib.AutoScrollbar import AutoScrollbar
from lib.tooltips import CreateToolTip
from lib.ModifyINI import ModifyINI
from lib.customFunctions import CustomFunctions, sm, browse_to_location, rgb_to_hex, hex_to_rgb, hex_to_decimal, decimal_to_rgb

class BethiniApp(tk.Tk):
    #This is the main app, the glue that creates the GUI.

    def __init__(self, *args, **kwargs):
        #You need args for lists and kwargs for dictionaries passed to tkinter
        tk.Tk.__init__(self, *args, **kwargs)

        #self.overrideredirect(True)
        tk.Tk.iconbitmap(self,default='Icon.ico') #sets the app icon

        #variables
        self.setup_dictionary = {}
        self.tab_dictionary = {}
        self.setting_dictionary = {}
        self.dependent_settings_dictionary = {}
        self.settings_that_settings_depend_on = {}
        self.tab = []

        self.widget_type_function = {
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

        self.widget_type_value = {
            'TkCheckbutton': self.checkboxValue,
            'TkOptionMenu': self.dropdownValue,
            'TkEntry': self.entryValue,
            'TkSpinbox': self.spinboxValue,
            'TkCombobox': self.comboboxValue,
            'TkColor': self.colorValue,
            'TkSlider': self.sliderValue,
            'TkRadioPreset': self.radioPresetValue
            }

        self.widget_type_assign_value = {
            'TkCheckbutton': self.checkboxAssignValue,
            'TkOptionMenu': self.dropdownAssignValue,
            'TkEntry': self.entryAssignValue,
            'TkSpinbox': self.spinboxAssignValue,
            'TkCombobox': self.comboboxAssignValue,
            'TkColor': self.colorAssignValue,
            'TkSlider': self.sliderAssignValue
            }

        self.types_without_label = ['Checkbutton', 'preset', 'radioPreset', 'description']
        self.types_packed_left = ['Dropdown', 'Combobox', 'Entry', 'Spinbox', 'Slider', 'Color']


        theme_dir = appConfig.getValue('General', 'sTheme', 'Default')

        self.open_inis = {
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
        self.s.configure(".", background=subContainerColor, font=smallFont,
                         foreground=textColor, fieldbackground=fieldColor, arrowcolor=textColor)
        self.s.map('.',
                   foreground=[('disabled', textColorDisabled),
                               ('pressed', textColorPressed),
                               ('active', textColorActive)],
                   background=[('disabled', backgroundColorDisabled),
                               ('pressed', '!focus', backgroundColorPressed),
                               ('active', backgroundColorActive)])

        arrow_size = int(round(int(smallFontSize)*1.33,0))

        self.s.configure('TCheckbutton', indicatorcolor=indicatorColor)
        self.s.configure('TCombobox', arrowsize=arrow_size)
        self.s.configure('TSpinbox', arrowsize=arrow_size, background=dropdownColor)
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

        self.the_canvas = tk.Canvas(self, borderwidth=0, background=containerColor,
                                   height=0, highlightthickness=0)
        self.hsbframeholder = ttk.Frame(self)

        self.vsb = AutoScrollbar(self, orient='vertical',
                                 command=self.the_canvas.yview)
        self.hsb = AutoScrollbar(self.hsbframeholder, orient='horizontal',
                                 command=self.the_canvas.xview)
        self.the_canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.container = ttk.Frame(self.the_canvas)

        #self.titleBar.pack(expand=False, fill=tk.X)
        #self.closeButton.pack(side=tk.RIGHT)
        self.hsbframeholder.pack(side=tk.BOTTOM, fill=tk.X)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.the_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_frame = self.the_canvas.create_window((4,4),
                                                          window=self.container,
                                                          tags='self.container')
        self.container.bind('<Configure>', self.on_frame_configure)
        self.sub_container = ttk.Notebook(self.container)
        self.sub_container.bind("<Configure>", self.sub_container_configure)

        self.statusbar_text = tk.StringVar(self)
        self.statusbar = ttk.Entry(self.hsbframeholder, textvariable=self.statusbar_text)

        self.pw = ttk.Label(self.hsbframeholder, text='Loading... Please Wait... ')
        self.p = ttk.Progressbar(self.hsbframeholder, orient=tk.HORIZONTAL, mode='indeterminate')
        self.start_progress()
        self.show_status_bar()
        #upon initialization of the BethiniApp class, self.chooseGame() is
        #called first, so we select or return to the game/app we want to work with

        self.choose_game_window = tk.Toplevel(self)
        self.choose_game_window.title('Choose Game')

        self.choose_game_frame = ttk.Frame(self.choose_game_window)

        self.choose_game_frame_2 = ttk.Frame(self.choose_game_frame)

        self.choose_game_label = ttk.Label(self.choose_game_frame_2, text="Game/Application")

        options = os.listdir('apps/')
        self.choose_game_var = tk.StringVar(self)
        self.choose_game_dropdown = ttk.OptionMenu(self.choose_game_frame_2,
                                                 self.choose_game_var, "None", *options,
                                                 command= lambda g: self.choose_game_done(g, True))
        self.choose_game_dropdown.var = self.choose_game_var

        self.choose_game_frame.pack(fill=tk.BOTH, expand=True)
        self.choose_game_frame_2.pack(anchor=tk.CENTER, expand=True)
        self.choose_game_label.pack(side=tk.LEFT, anchor=tk.CENTER, padx=5, pady=5)
        self.choose_game_dropdown.pack(anchor=tk.CENTER, padx=5, pady=5)
        self.choose_game_window.protocol("WM_DELETE_WINDOW", onClosing)
        self.choose_game_window.minsize(300,35)

        self.preset_var = tk.StringVar(self)
        self.preset_var.set('Bethini')

        self.choose_game()

    def on_frame_configure(self, event):
        self.the_canvas.configure(scrollregion=self.the_canvas.bbox('all'))

    def sub_container_configure(self, event):
        the_width = event.width + 17# + 35
        the_height = event.height + 21# + 65
        self.geometry(f'{the_width}x{the_height}')

    def start_progress(self):
        self.pw.pack(side=tk.LEFT, anchor=tk.S)
        self.p.pack(expand=True, fill=tk.X, anchor=tk.S)
        self.p.start()

    def stop_progress(self):
        self.pw.destroy()
        self.p.stop()
        self.p.destroy()
        self.pw = ttk.Label(self.hsbframeholder, text='Loading... Please Wait... ')
        self.p = ttk.Progressbar(self.hsbframeholder, orient=tk.HORIZONTAL, mode='indeterminate')

    def sme(self, message, exception=False):
        sm(message, exception)
        self.statusbar_text.set(message)
        self.update()

    def show_sub_container(self):
        self.sub_container.pack(fill=tk.BOTH, expand=True)

    def show_status_bar(self):
        self.statusbar.pack(anchor='w', side=tk.BOTTOM, fill=tk.X)

    def choose_color(self, button_to_modify, color_value_type='hex'):
        #This allows us to have our very convenient tkinter colorchooser dialog
        #window modify a button
        old_color = button_to_modify.var.get()
        if color_value_type == 'rgb':
            old_color = rgb_to_hex(ast.literal_eval(old_color))
        elif color_value_type == 'rgb 1':
            #"(1.0000, 1.0000, 1.0000)"
            #(255, 255, 255)
            old_color = tuple(int(float(i)*255) for i in ast.literal_eval(old_color))
        elif color_value_type == 'decimal':
            old_color = rgb_to_hex(decimal_to_rgb(old_color))

        try:
            new_color = colorchooser.askcolor(color = old_color)[1].upper()
        except:
            #self.sme('Cancelled change of color.', exception=1)
            new_color = old_color

        rgb = hex_to_rgb(new_color)
        luminance = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
        if luminance < 128:
            the_text_color = '#FFFFFF'
        else:
            the_text_color = '#000000'
        button_to_modify.configure(bg=new_color, activebackground=new_color, fg=the_text_color)
        if color_value_type == 'rgb':
            button_to_modify.var.set(str(hex_to_rgb(new_color)).replace(' ',''))
        elif color_value_type == 'rgb 1':
            #(255, 255, 255)
            #"(1.0000, 1.0000, 1.0000)"
            the_rgb = str(tuple(round(i/255,4) for i in hex_to_rgb(new_color)))
            button_to_modify.var.set(the_rgb)
        elif color_value_type == 'decimal':
            button_to_modify.var.set(hex_to_decimal(new_color))
        else:
            button_to_modify.var.set(new_color)
        preferencesWindow.lift()
        return new_color

    def tooltip(self, each_tab, label_frame, the_label_frame, on_frame, setting, the_setting, id_):
        CreateToolTip(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_],
                      self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tooltip"])

    def choose_game(self, forced=0):
        self.withdraw()
        # The Choose App/Game dialog window.  The window is skipped here if
        # sAppName is already set in the Bethini.ini file.
        try:
            choose_game_var = appConfig.getValue('General','sAppName')
            if forced == 1:
                self.sme('Force choose game/application.')
                raise Exception("Forcing you to choose")
            if appConfig.getValue('General', 'bAlwaysSelectGame', '0') == '1':
                self.sme('Force choose game/application at startup.')
                GAME_NAME #By calling the global variable GAME_NAME before it has been created,
                         #we raise
                         #an exception to force the app/game to be chosen only
                         #at startup.
            #raise Exception("Forcing you to choose")
            self.choose_game_done(choose_game_var)
        except:
            self.sme('Choose game/application.', exception=1)
            self.choose_game_window.deiconify()

    def choose_game_done(self, game, from_choose_game_window=False):
        self.choose_game_window.withdraw()

        # Once the app/game is selected, this loads it.
        try:
            self.choose_game_var = appConfig.getValue('General','sAppName')
            if self.choose_game_var != game:
                self.sme(f'Change of game from {self.chooseGameVar} to {game}')
                raise Exception("App/Game specified in " + MyAppNameConfig + " differs from the game chosen, so it will be changed to the one you chose.")
        except:
            self.sme('Change of game/application', exception=1)
            appConfig.assignINIValue('General','sAppName', game)
            from_choose_game_window = True

        tk.Tk.wm_title(self, MyAppName + " - " + game)

        ##############
        # app globals
        ##############

        global APP
        APP = AppName(game)
        global GAME_NAME
        GAME_NAME = APP.game_name()
        self.sme(f'Application/game is {GAME_NAME}')

        #######
        # Tabs
        #######

        tabs = APP.tabs()
        #The self.tab_dictionary lists all the tabs, which
        #is variable, based upon the tabs listed in the associated Bethini.json

        for tab in self.tab_dictionary:
            if self.tab_dictionary[tab]['Name'] == 'Setup':
                try:
                    self.tab_dictionary[tab]['SetupWindow'].destroy()
                except:
                    tk_frame = self.tab_dictionary[tab].get('TkFrameForTab')
                    if tk_frame:
                        tk_frame.destroy()
            else:
                tk_frame = self.tab_dictionary[tab].get('TkFrameForTab')
                if tk_frame:
                    tk_frame.destroy()

        self.tab_dictionary = {}
        tab_number = 0
        for tab in tabs:
            tab_number += 1
            self.tab_dictionary["Page" + str(tab_number)] = {"Name":tab}

        self.setup_dictionary = {}
        self.setting_dictionary = {}
        self.dependent_settings_dictionary = {}
        self.settings_that_settings_depend_on = {}
        self.tab = []

        self.menu()
        if not from_choose_game_window:
            self.deiconify()
        self.createTabs(from_choose_game_window)

    def menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command = self.save_ini_files)
        filemenu.add_separator()
        filemenu.add_command(label="Choose game", command = lambda: self.choose_game(forced=1))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=onClosing)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Preferences", command = self.show_preferences)
        editmenu.add_command(label="Setup", command = self.show_setup)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Visit Web Page",
                             command = lambda: webbrowser.open_new_tab('http://www.nexusmods.com/skyrimspecialedition/mods/4875/'))
        helpmenu.add_command(label="Get Support",
                             command = lambda: webbrowser.open_new_tab('https://stepmodifications.org/forum/forum/200-Bethini-support/'))
        helpmenu.add_command(label="About", command = self.about)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Help", menu=helpmenu)
        tk.Tk.config(self, menu=menubar)

    def show_preferences(self):
        preferencesWindow.deiconify()

    def withdraw_preferences(self):
        preferencesWindow.withdraw()

    def about(self):
        about_window = tk.Toplevel(self)
        about_window.title('About')

        about_frame = ttk.Frame(about_window)
        about_frame_real = ttk.Frame(about_frame)

        about_label = ttk.Label(about_frame_real,
                               text=f'About {MyAppName}\n\n{MyAppName} was created by DoubleYou.\n\nLicensing is CC by-NC-SA.',
                               justify=tk.CENTER)

        about_frame.pack(fill=tk.BOTH, expand=True)
        about_frame_real.pack(anchor=tk.CENTER, expand=True)
        about_label.pack(anchor=tk.CENTER, padx='10', pady='10')

    def show_setup(self):
        self.withdraw()
        setupWindow.deiconify()

    def withdraw_setup(self):
        setupWindow.withdraw()
        self.deiconify()
        self.updateValues()

    def save_ini_files(self):
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
        first_time_backup = False
        files_saved = False
        self.remove_invalid_settings()
        the_opened_inis = self.open_inis
        ini_list = list(the_opened_inis.keys())
        files_to_remove = ini_list[2:]
        files_to_remove.append('log.log')
        for each_ini in the_opened_inis:
            location_list = list(the_opened_inis[each_ini]['located'].keys())
            for n in range(len(location_list)):
                this_location = the_opened_inis[each_ini]['located'][str(n+1)].get('at')
                this_ini_object = the_opened_inis[each_ini]['located'][str(n+1)].get('object')
                if each_ini == MyAppNameConfig:
                    continue
                if not this_ini_object.HasBeenModified:
                    self.sme(f'{each_ini} has not been modified, so there is no reason to resave it.')
                    continue
                if messagebox.askyesno(f"Save {each_ini}", f"Do you want to save {this_location}{each_ini}?"):
                    #we need to make a backup of each save before actually saving.
                    if each_ini != 'theme.ini':
                        first_time_backup_trigger = removeExcessDirFiles(f'{this_location}{MyAppName} backups',
                                                                      int(appConfig.getValue('General', 'iMaxBackups', '-1')),
                                                                      files_to_remove)
                        if first_time_backup_trigger:
                            first_time_backup = True
                        if first_time_backup:
                            the_backup_directory = f'{this_location}\\{MyAppName} backups\\First-Time-Backup\\'
                            if not os.path.isdir(the_backup_directory):
                                os.makedirs(the_backup_directory)
                            if os.path.exists(f"{the_backup_directory}{each_ini}"):
                                self.sme(f'{the_backup_directory}{each_ini} exists, so it will not be overwritten.')
                            else:
                                copyfile(f"{this_location}{each_ini}", f"{the_backup_directory}{each_ini}")
                            copyfile(MyAppNameLog, f"{the_backup_directory}log.log")
                        the_backup_directory = f'{this_location}\\{MyAppName} backups\\{logDirectoryDate}\\'
                        if not os.path.isdir(the_backup_directory):
                            os.makedirs(the_backup_directory)
                        if os.path.exists(f"{the_backup_directory}{each_ini}"):
                            self.sme(f'{the_backup_directory}{each_ini} exists, so it will not be overwritten.')
                        else:
                            copyfile(f"{this_location}{each_ini}", f"{the_backup_directory}{each_ini}")
                        copyfile(MyAppNameLog, f"{the_backup_directory}log.log")
                    this_ini_object.writeINI(1)
                    files_saved = True
                    self.sme(f"{this_location}{each_ini} saved.")
        if not files_saved:
            self.sme('No files were modified.')

    def set_preset(self, preset_id):
        self.start_progress()
        if preset_id == "Default":
            self.apply_ini_dict(APP.preset_values('default'))
            self.remove_ini_dict(APP.can_remove())
            self.apply_ini_dict(APP.preset_values('fixedDefault'))
            preset_var = ""
        elif preset_id == "recommended":
            preset_dict = APP.preset_values(f'{preset_id}')
            self.apply_ini_dict(preset_dict)
            preset_var = ""
        else:
            preset_var = self.preset_var.get()
            preset_dict = APP.preset_values(f'{preset_var} {preset_id}')
            self.apply_ini_dict(preset_dict)
        self.stop_progress()
        self.updateValues()
        self.sme(f"Preset {preset_var} {preset_id} applied.")

    def remove_invalid_settings(self):
        the_opened_inis = self.open_inis

        for each_ini in the_opened_inis:
            if each_ini == MyAppNameConfig or each_ini == 'theme.ini':
                continue
            elif APP.inis(each_ini):
                location_list = list(the_opened_inis[each_ini]['located'].keys())
                for n in range(len(location_list)):
                    #thisLocation = the_opened_inis[each_ini]['located'][str(n+1)].get('at')
                    this_ini_object = the_opened_inis[each_ini]['located'][str(n+1)].get('object')

                    sections = this_ini_object.getSections()

                    for section in sections:
                        settings = this_ini_object.getSettings(section)
                        if settings == []:
                            this_ini_object.removeSection(section)
                            self.sme(f'{section} was removed because it was empty.')
                        else:
                            for setting in settings:
                                if ';' in setting:
                                    self.sme(f'{setting}:{section} will be preserved, as it is a comment.')
                                elif not APP.does_setting_exist(each_ini, section, setting):
                                    this_ini_object.removeSetting(section, setting)
                                    self.sme(f'{setting}:{section} was removed because it is not recognized.')

    def apply_ini_dict(self, ini_dict):
        presets_ignore_these_settings = APP.presets_ignore_these_settings()
        for each_setting in ini_dict:
            if each_setting in presets_ignore_these_settings:
                continue
            target_ini = ini_dict[each_setting]['ini']
            target_section = ini_dict[each_setting]['section']
            this_value = str(ini_dict[each_setting]['value'])

            ini_location = APP.inis(target_ini)
            if ini_location != '':
                ini_location = appConfig.getValue('Directories', ini_location)
            the_target_ini = self.openINI(str(ini_location), str(target_ini))

            the_target_ini.assignINIValue(target_section, each_setting, this_value)
            self.sme(target_ini + " [" + target_section + "] " + each_setting + "=" + this_value)

    def remove_ini_dict(self, ini_dict):
        for eachSetting in ini_dict:
            targetINI = ini_dict[eachSetting]['ini']
            targetSection = ini_dict[eachSetting]['section']
            thisValue = str(ini_dict[eachSetting]['value'])

            INILocation = APP.inis(targetINI)
            if INILocation != '':
                INILocation = appConfig.getValue('Directories', INILocation)
            theTargetINI = self.openINI(str(INILocation), str(targetINI))

            currentValue = theTargetINI.getValue(targetSection, eachSetting, thisValue)

            if currentValue == thisValue:
                theTargetINI.removeSetting(targetSection, eachSetting)
                self.sme(f"{targetINI} [{targetSection}] {eachSetting}={thisValue}, which is the default value, and since it is not set to alwaysPrint, it will be removed")

    def createTabImage(self, eachTab):
        try:
            self.tab_dictionary[eachTab]["TkPhotoImageForTab"] = tk.PhotoImage(file = "theme\\" + theme + "\\" + self.tab_dictionary[eachTab]["Name"] + ".png")
        except:
            self.sme('No theme image for tab.', exception=1)
            self.tab_dictionary[eachTab]["TkPhotoImageForTab"] = tk.PhotoImage(file = "theme\\" + theme + "\\Blank.png")

    def labelFramesForTab(self, eachTab):
        theDict = self.tab_dictionary[eachTab]
        theDict["LabelFrames"] = {}
        labelFrameNumber=0
        for labelFrame in APP.label_frames_in_tab(theDict["Name"]):
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
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"] = {}
        NumberOfVerticallyStackedSettings = int(APP.number_of_vertically_stacked_settings(self.tab_dictionary[eachTab]["Name"], labelFrame))
        settingNumber = 0
        for setting in APP.settings_in_label_frame(self.tab_dictionary[eachTab]["Name"], labelFrame):
            settingNumber += 1
            onFrame = "SettingFrame" + str(math.ceil(settingNumber / NumberOfVerticallyStackedSettings) - 1)
            if onFrame not in self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"]:
                self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame] = {}
                self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame]["TkSettingFrame"] = ttk.Frame(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["TkLabelFrame"])
                self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame]["TkSettingFrame"].pack(side=tk.LEFT, anchor='nw')
            TheSetting = "Setting" + str(settingNumber)
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting] = {"Name":setting}
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"] = ttk.Frame(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame]["TkSettingFrame"])
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"].pack(anchor='w', padx='5', pady='2')
            if 'Placeholder' not in setting:
                self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].update(APP.get_all_fields_for_setting(self.tab_dictionary[eachTab]["Name"], labelFrame, setting))
                self.settingLabel(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting)

    def settingLabel(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        settingType = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("type")
        if settingType not in self.types_without_label:
            if settingType:
                settingLabel = setting
            else:
                settingLabel = ''
            settingLabelWidth = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("customWidth")
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkLabel"] = ttk.Label(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                                   text=settingLabel, font=smallFont, width=settingLabelWidth, anchor=tk.E)
            if settingType in self.types_packed_left:
                self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkLabel"].pack(anchor=tk.CENTER, side=tk.LEFT, padx=5, pady=5)
            else:
                self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkLabel"].pack(anchor=tk.CENTER, padx=5, pady=5)
        settingDescription = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("Description")
        if settingDescription:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkDescriptionLabel"] = ttk.Label(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                                              text=settingDescription, font=smallFont, justify="left", wraplength=900)
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkDescriptionLabel"].pack(anchor=tk.N)
        self.settingTypeSwitcher(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, settingType)

    def settingTypeSwitcher(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, settingType):
        func = self.widget_type_function.get(settingType, "Invalid")
        if func != "Invalid":
            func(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting)

    def widgetTypeSwitcher(self, setting):
        id_ = self.setting_dictionary[setting].get('id')
        func = self.widget_type_value.get(id_, "Invalid")
        if func != "Invalid":
            return func(setting)

    def addToSettingDictionary(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_):
        stuffToAddToSettingDictionary = {
            setting : {
                'eachTab': eachTab,
                'labelFrame': labelFrame,
                'TheLabelFrame': TheLabelFrame,
                'onFrame': onFrame,
                'TheSetting': TheSetting,
                'id': id_,
                'TkWidget': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_],
                'targetINIs': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('targetINIs'),
                'settings': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('settings'),
                'targetSections': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('targetSections')
                }
            }

        self.setting_dictionary.update(stuffToAddToSettingDictionary)

        dependentSettings = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('dependentSettings')
        if dependentSettings:
            self.dependent_settings_dictionary[setting] = dependentSettings

    def checkbox(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the Checkbutton widget
        id_ = "TkCheckbutton"
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        onValue = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("Onvalue")
        offValue = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("Offvalue")
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Checkbutton(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                              text=setting, variable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                              onvalue=onValue, offvalue=offValue)
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].var = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor='w', padx=5, pady=3.5)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'onvalue': onValue,
            'offvalue': offValue
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def preset(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates a preset button
        id_ = "TkPresetButton"

        presetid = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("preset id")
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Button(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                         text=setting, command=lambda: self.set_preset(presetid))
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=2)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)

    def radioPreset(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the radio preset button
        id_ = 'TkRadioPreset'
        value = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('value')
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Radiobutton(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                              text=setting,
                                                                                                                              variable=self.preset_var, value=value)
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=4)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.preset_var
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def dropdown(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the OptionMenu widget
        id_ = "TkOptionMenu"

        OPTIONS = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("choices")
                        
        #custom functions allow us to auto-detect certain
        #predefined options that can then easily be selected.

        if type(OPTIONS) == str:
            if 'FUNC' in OPTIONS:
                OptionString = APP.custom(OPTIONS)
                if '{}' in OptionString:
                    customFunction = APP.custom(f'{OPTIONS}Format')
                    valueToInsert = getattr(CustomFunctions, customFunction)(GAME_NAME)
                    OPTIONS = valueToInsert
        else:
            for n in range(len(OPTIONS)):
                if 'FUNC' in OPTIONS[n]:
                    OptionString = APP.custom(OPTIONS[n])
                    if '{}' in OptionString:
                        customFunction = APP.custom(str(OPTIONS[n]) + 'Format')
                        valueToInsert = getattr(CustomFunctions, customFunction)(GAME_NAME)
                        OPTIONS[n] = OptionString.format(valueToInsert)

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.OptionMenu(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                             self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                             OPTIONS[0], *OPTIONS,
                                                                                                                             command=lambda c,var=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                             browse=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("browse"),
                                                                                                                             function=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("customFunction"):
                                                                                                                             var.set(browse_to_location(c, browse, function, GAME_NAME)))
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].var = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'OPTIONS': OPTIONS,
            'settingChoices': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('settingChoices'),
            'delimiter': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('delimiter'),
            'decimal places': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('decimal places'),
            'fileFormat': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('fileFormat'),
            'forceSelect': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('forceSelect'),
            'partial': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('partial')
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def combobox(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        id_ = 'TkCombobox'
        OPTIONS = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("choices")
        width = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("width")
        validate = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        
        if validate:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Combobox(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                           textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                           width=width, values=OPTIONS, validate='key', validatecommand=(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate))
        else:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Combobox(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                           textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                           width=width, values=OPTIONS)
        
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'OPTIONS': OPTIONS,
            'decimal places': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get('decimal places')
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def entry(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #creates the Entry widget
        id_ = "TkEntry"
        entryWidth = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("entryWidth")
        validate = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)

        if validate:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Entry(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=entryWidth, validate='key', font=smallFont,
                                                                                                                        validatecommand=(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        else:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Entry(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=entryWidth, font=smallFont,
                                                                                                                        textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'formula': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("formula"),
            'decimal places': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("decimal places"),
            'partial': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("partial"),
            'fileFormat': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("fileFormat")
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def slider(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        id_ = "TkSlider"
        fromV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("from")
        toV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("to")
        resolutionV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("resolution")
        digitsV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("digits")
        lengthV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("length")

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = tk.Scale(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        from_=fromV, to=toV, resolution=resolutionV, showvalue=0, digits=digitsV, orient=tk.HORIZONTAL, relief=tk.FLAT,
                                                                                                                        highlightthickness=0, bg=subContainerColor, length=lengthV, font=smallFont, activebackground=backgroundColorActive,
                                                                                                                        troughcolor=fieldColor,
                                                                                                                        variable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])

        width = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("width")
        validate = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")
        incrementV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("increment")

        reversed_ = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("reversed")
        if reversed_:
            fromV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("to")
            toV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("from")

        if validate:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"] = ttk.Spinbox(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=width, validate='key', increment=incrementV, from_=fromV, to=toV, font=smallFont,
                                                                                                                        validatecommand=(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        else:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"] = ttk.Spinbox(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        width=width, increment=incrementV, from_=fromV, to=toV, font=smallFont,
                                                                                                                        textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, "TkWidgetTwo")
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'decimal places': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("decimal places"),
            'TkWidgetTwo': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkWidgetTwo"]
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def spinbox(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        id_ = "TkSpinbox"
        fromV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("from")
        toV = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("to")
        increment = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("increment")
        width = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("width")
        validate = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("validate")

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)

        if validate:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"] = self.register(self.validate)
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Spinbox(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        from_=fromV, to=toV, increment=increment, width=width, validate='key', font=smallFont,
                                                                                                                        validatecommand=(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        else:
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = ttk.Spinbox(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        from_=fromV, to=toV, increment=increment, width=width, font=smallFont,
                                                                                                                        textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"])
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def color(self, eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting):
        #chooseColor(colorToChange, buttonToModify)
        id_ = "TkColor"

        colorValueType = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("colorValueType")

        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"] = tk.StringVar(self)
        if colorValueType == 'hex':
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('#FFFFFF')
        elif colorValueType == 'rgb':
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('(255, 255, 255)')
        elif colorValueType == 'rgb 1':
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('(1.0000, 1.0000, 1.0000)')
        elif colorValueType == 'decimal':
            self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"].set('16777215')
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_] = tk.Button(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkFinalSettingFrame"],
                                                                                                                        textvariable=self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
                                                                                                                        font=smallFont,
                                                                                                                        command=lambda: self.choose_color(self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_],
                                                                                                                                                         colorValueType))
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].var = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"]
        self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)

        self.addToSettingDictionary(eachTab, labelFrame, TheLabelFrame, onFrame, setting, TheSetting, id_)
        stuffToAddToSettingDictionary = {
            'TkVar': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting]["TkVar"],
            'colorValueType': colorValueType,
            'rgbType': self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("rgbType")
            }
        self.setting_dictionary[setting].update(stuffToAddToSettingDictionary)

    def radioPresetValue(self, setting):
        return self.preset_var.get()

    def checkboxValue(self, setting):
        settingValue = self.getSettingValues(self.setting_dictionary[setting].get('targetINIs'),
                                             self.setting_dictionary[setting].get('targetSections'),
                                             self.setting_dictionary[setting].get('settings'))
        
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            onvalue = self.setting_dictionary[setting].get('onvalue')
            offvalue = self.setting_dictionary[setting].get('offvalue')
            if settingValue == onvalue:
                thisValue = onvalue
                self.setting_dictionary[setting]["TkVar"].set(thisValue)
            elif settingValue == offvalue:
                thisValue = offvalue
                self.setting_dictionary[setting]["TkVar"].set(thisValue)
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
                self.setting_dictionary[setting]["TkVar"].set(thisValue)
            try:
                self.sme(f"{setting} = {thisValue}")
                self.setting_dictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'No value set for checkbox {setting}.')

    def dropdownValue(self, setting):
        settingValue = self.getSettingValues(self.setting_dictionary[setting].get('targetINIs'),
                                             self.setting_dictionary[setting].get('targetSections'),
                                             self.setting_dictionary[setting].get('settings'),
                                             self.setting_dictionary[setting].get('settingChoices'), 
                                             self.setting_dictionary[setting].get('delimiter'))

        if settingValue != [] and 'Does Not Exist' not in settingValue:
            decimalPlaces = self.setting_dictionary[setting].get("decimal places")
            if decimalPlaces:
                decimalPlaces = int(decimalPlaces)
                thisValue = round(float(settingValue[0]), decimalPlaces)
                if decimalPlaces == 0:
                    thisValue = int(thisValue)
                self.setting_dictionary[setting]["TkVar"].set(thisValue)
            else:
                fileFormat = self.setting_dictionary[setting].get("fileFormat")
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
                    self.setting_dictionary[setting]["TkVar"].set(thisValue)
                else:
                    settingChoices = self.setting_dictionary[setting].get("settingChoices")
                    if settingChoices and settingValue[0] not in settingChoices:
                        thisValue = "Custom"
                        self.setting_dictionary[setting]["TkVar"].set(thisValue)
                    else:
                        thisValue = settingValue[0]
                        self.setting_dictionary[setting]["TkVar"].set(thisValue)
            self.sme(f"{setting} = {thisValue}")
            self.setting_dictionary[setting]['valueSet'] = True
            return thisValue

    def comboboxValue(self, setting):
        settingValue = self.getSettingValues(self.setting_dictionary[setting].get('targetINIs'),
                                             self.setting_dictionary[setting].get('targetSections'),
                                             self.setting_dictionary[setting].get('settings'))
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            thisValue = settingValue[0]

            decimalPlaces = self.setting_dictionary[setting].get("decimal places")
            if decimalPlaces:
                decimalPlaces = int(decimalPlaces)
                thisValue = round(float(thisValue), decimalPlaces)
                if decimalPlaces == 0:
                    thisValue = int(thisValue)
            
            self.setting_dictionary[setting]["TkVar"].set(thisValue)
            self.sme(f"{setting} = {thisValue}")
            self.setting_dictionary[setting]['valueSet'] = True
            return thisValue

    def entryValue(self, setting):
        settingValue = self.getSettingValues(self.setting_dictionary[setting].get('targetINIs'),
                                             self.setting_dictionary[setting].get('targetSections'),
                                             self.setting_dictionary[setting].get('settings'))
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            formula = self.setting_dictionary[setting].get("formula")
            fileFormat = self.setting_dictionary[setting].get("fileFormat")
            if formula:
                decimalPlaces = int(self.setting_dictionary[setting].get("decimal places"))
                thisValue = round(simple_eval(formula.format(settingValue[0])), decimalPlaces)
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
                self.setting_dictionary[setting]['TkVar'].set(thisValue)
                self.sme(f"{setting} = {thisValue}")
                self.setting_dictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'No value set for entry {setting}.')

    def sliderValue(self, setting):
        settingValue = self.getSettingValues(self.setting_dictionary[setting].get('targetINIs'),
                                             self.setting_dictionary[setting].get('targetSections'),
                                             self.setting_dictionary[setting].get('settings'))

        if settingValue != [] and 'Does Not Exist' not in settingValue:
            thisValue = settingValue[0]

            decimalPlaces = self.setting_dictionary[setting].get("decimal places")
            if decimalPlaces:
                decimalPlaces = int(decimalPlaces)
                thisValue = round(float(thisValue), decimalPlaces)
                if decimalPlaces == 0:
                    thisValue = int(thisValue)
            
            try:
                self.setting_dictionary[setting]['TkVar'].set(thisValue)
                self.sme(f'{setting} = {thisValue}')
                self.setting_dictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'no value set for slider {setting}')

    def spinboxValue(self, setting):
        settingValue = self.getSettingValues(self.setting_dictionary[setting].get('targetINIs'),
                                             self.setting_dictionary[setting].get('targetSections'),
                                             self.setting_dictionary[setting].get('settings'))
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            thisValue = settingValue[0]
            try:
                self.setting_dictionary[setting]['TkVar'].set(thisValue)
                self.sme(f'{setting} = {thisValue}')
                self.setting_dictionary[setting]['valueSet'] = True
                return thisValue
            except:
                self.sme(f'no value set for spinbox {setting}')

    def colorValue(self, setting):
        settingValue = self.getSettingValues(self.setting_dictionary[setting].get('targetINIs'),
                                             self.setting_dictionary[setting].get('targetSections'),
                                             self.setting_dictionary[setting].get('settings'))
        
        if settingValue != [] and 'Does Not Exist' not in settingValue:
            colorValueType = self.setting_dictionary[setting].get("colorValueType")
            if colorValueType == 'hex':
                thisValue = settingValue[0]
                newColor = thisValue
            elif colorValueType == 'decimal':
                thisValue = settingValue[0]
                #convert decimal value to hex
                newColor = rgb_to_hex(decimal_to_rgb(settingValue[0]))
            elif colorValueType == 'rgb':
                rgbType = self.setting_dictionary[setting].get("rgbType")
                if rgbType == 'multiple settings':
                    thisValue = tuple(int(i) for i in settingValue)
                    newColor = rgb_to_hex(thisValue)
                    thisValue = str(thisValue)
                else:
                    thisValue = '('
                    for n in range(len(settingValue)):
                        thisValue += settingValue[n]
                    thisValue += ')'
                    print(thisValue)
                    newColor = rgb_to_hex(ast.literal_eval(thisValue))
            elif colorValueType == 'rgb 1':
                rgbType = self.setting_dictionary[setting].get("rgbType")
                if rgbType == 'multiple settings':
                    thisValue = tuple(round(float(i),4) for i in settingValue)
                    newColor = rgb_to_hex(tuple(int(float(i)*255) for i in settingValue))
                    thisValue = str(thisValue)
            self.setting_dictionary[setting]['TkVar'].set(thisValue)
            TkWidget = self.setting_dictionary[setting].get("TkWidget")
            RGB = hex_to_rgb(newColor)
            luminance = 0.299*RGB[0] + 0.587*RGB[1] + 0.114*RGB[2]
            if luminance < 128:
                theTextColor = '#FFFFFF'
            else:
                theTextColor = '#000000'
            TkWidget.configure(bg=newColor, activebackground=newColor, fg=theTextColor)
            self.sme(f"{setting} = {thisValue}")
            self.setting_dictionary[setting]['valueSet'] = True
            return thisValue

    def checkDependents(self, setting):
        for dependentSetting in self.settings_that_settings_depend_on[setting]:
            var = self.settings_that_settings_depend_on[setting][dependentSetting].get('var')
            
            theOperator = self.settings_that_settings_depend_on[setting][dependentSetting].get('theOperator')
            value = self.settings_that_settings_depend_on[setting][dependentSetting].get('value')
            currentValue = self.widgetTypeSwitcher(setting)
            TkWidgetTwo = self.setting_dictionary[dependentSetting].get('TkWidgetTwo')
            if var == 'float':
                value = float(value)
                currentValue = float(currentValue)
            if theOperator(currentValue, value):
                self.setting_dictionary[dependentSetting]['TkWidget'].configure(state='normal')
                if TkWidgetTwo:
                    TkWidgetTwo.configure(state='normal')
            else:
                setToOff = self.settings_that_settings_depend_on[setting][dependentSetting].get('setToOff')
                if setToOff:
                    offvalue = self.setting_dictionary[dependentSetting].get('offvalue')

                    self.setting_dictionary[dependentSetting]['TkVar'].set(offvalue)
                self.setting_dictionary[dependentSetting]['TkWidget'].configure(state='disabled')
                if TkWidgetTwo:
                    TkWidgetTwo.configure(state='disabled')

    def assignValue(self, var, indx, mode, setting):
        id_ = self.setting_dictionary[setting].get('id')
        func = self.widget_type_assign_value.get(id_, "Invalid")
        if func != "Invalid":
            func(setting)
        
        if setting in list(self.settings_that_settings_depend_on.keys()):
            self.checkDependents(setting)

    def checkboxAssignValue(self, setting):
        TkVar = self.setting_dictionary[setting].get('TkVar')
        
        thisValue = TkVar.get()
        #thisValue is whatever the state of the onvalue/offvalue is... not a simple boolean


        targetINIs = self.setting_dictionary[setting].get('targetINIs')
        targetSections = self.setting_dictionary[setting].get('targetSections')
        theSettings = self.setting_dictionary[setting].get('settings')
        
        onvalue = self.setting_dictionary[setting].get('onvalue')
        offvalue = self.setting_dictionary[setting].get('offvalue')

        settingValue = self.getSettingValues(targetINIs, targetSections, theSettings)
        
        try:
            thisValue = list(ast.literal_eval(thisValue))
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
                        elif thisValue[n][0] in self.setting_dictionary:
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
        TkVar = self.setting_dictionary[setting].get('TkVar')
        thisValue = TkVar.get()
        #print(thisValue)
        targetINIs = self.setting_dictionary[setting].get('targetINIs')
        targetSections = self.setting_dictionary[setting].get('targetSections')
        theSettings = self.setting_dictionary[setting].get('settings')

        settingChoices = self.setting_dictionary[setting].get('settingChoices')
        delimiter = self.setting_dictionary[setting].get('delimiter')
        fileFormat = self.setting_dictionary[setting].get('fileFormat')
        #decimalPlaces = self.setting_dictionary[setting].get('decimal places')
        partial = self.setting_dictionary[setting].get('partial')
        theValueStr = ''
        if partial:
            for eachSetting in partial:
                if eachSetting == setting:
                    theValueStr += '{}'
                else:
                    try:
                        if self.setting_dictionary[eachSetting]['valueSet']:
                            theValueStr += self.setting_dictionary[eachSetting]['TkVar'].get()
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
                if thisValue == 'Manual...' or thisValue == 'Browse...':
                    theValue = ''
                elif delimiter:
                    listOfValues = thisValue.split(delimiter)
                    try:
                        theValue = listOfValues[n]
                    except IndexError:
                        theValue = ''
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
                self.sme(f'{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}')

    def comboboxAssignValue(self, setting):
        targetINIs = self.setting_dictionary[setting].get('targetINIs')

        if targetINIs:
            TkVar = self.setting_dictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.setting_dictionary[setting].get('targetSections')
            theSettings = self.setting_dictionary[setting].get('settings')

            decimalPlaces = self.setting_dictionary[setting].get('decimal places')
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
        targetINIs = self.setting_dictionary[setting].get('targetINIs')
       
        partial = self.setting_dictionary[setting].get('partial')
        theValueStr = ''
        if partial:
            for eachSetting in partial:
                if eachSetting == setting:
                    theValueStr += '{}'
                else:
                    #self.widgetTypeSwitcher(eachSetting)
                    if self.setting_dictionary[eachSetting]['valueSet']:
                        theValueStr += self.setting_dictionary[eachSetting]['TkVar'].get()
                    else:
                        return

        if targetINIs:
            TkVar = self.setting_dictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.setting_dictionary[setting].get('targetSections')
            theSettings = self.setting_dictionary[setting].get('settings')

            formula = self.setting_dictionary[setting].get('formula')
            #decimalPlaces = self.setting_dictionary[setting].get('decimal places')

            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                if formula:
                    formulaValue = formula.format(thisValue)
                    try:
                        thisValue = str(round(simple_eval(formulaValue),8))
                    except:
                        self.sme('Failed to evaluate formula value for {thisValue}.')
                #if decimalPlaces:
                #    thisValue = round(thisValue,int(decimalPlaces))

                if partial:
                    thisValue = theValueStr.format(thisValue)
                theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)

    def sliderAssignValue(self, setting):
        targetINIs = self.setting_dictionary[setting].get('targetINIs')

        if targetINIs:
            TkVar = self.setting_dictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.setting_dictionary[setting].get('targetSections')
            theSettings = self.setting_dictionary[setting].get('settings')

            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)

    def spinboxAssignValue(self, setting):
        targetINIs = self.setting_dictionary[setting].get('targetINIs')
        
        if targetINIs:
            TkVar = self.setting_dictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.setting_dictionary[setting].get('targetSections')
            theSettings = self.setting_dictionary[setting].get('settings')

            for n in range(len(targetINIs)):
                INILocation = self.getINILocation(targetINIs[n])
                theTargetINI = self.openINI(str(INILocation), str(targetINIs[n]))

                theTargetINI.assignINIValue(targetSections[n], theSettings[n], thisValue)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + thisValue)

    def colorAssignValue(self, setting):
        targetINIs = self.setting_dictionary[setting].get('targetINIs')
        
        if targetINIs:
            TkVar = self.setting_dictionary[setting].get('TkVar')
            thisValue = TkVar.get()

            targetSections = self.setting_dictionary[setting].get('targetSections')
            theSettings = self.setting_dictionary[setting].get('settings')

            colorValueType = self.setting_dictionary[setting].get("colorValueType")
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
        
        for eachTab in self.tab_dictionary:
            #eachTab is Page1, Page2, etc.
            #self.tab_dictionary[eachTab]["Name"] is the name of each tab

            self.createTabImage(eachTab)
            if self.tab_dictionary[eachTab]['Name'] == 'Setup':
                global setupWindow
                self.tab_dictionary[eachTab]['SetupWindow'] = tk.Toplevel(self)
                setupWindow = self.tab_dictionary[eachTab]['SetupWindow']
                setupWindow.title('Setup')
                self.tab_dictionary[eachTab]["TkFrameForTab"] = ttk.Frame(setupWindow)
                self.tab_dictionary[eachTab]["TkFrameForTab"].pack()
                setupWindow.protocol("WM_DELETE_WINDOW", self.withdraw_setup)
                if not fromChooseGameWindow:
                    setupWindow.withdraw()
            elif self.tab_dictionary[eachTab]['Name'] == 'Preferences':
                global preferencesWindow
                self.tab_dictionary[eachTab]['PreferencesWindow'] = tk.Toplevel(self)
                preferencesWindow = self.tab_dictionary[eachTab]['PreferencesWindow']
                preferencesWindow.title('Preferences')
                self.tab_dictionary[eachTab]["TkFrameForTab"] = ttk.Frame(preferencesWindow)
                self.tab_dictionary[eachTab]["TkFrameForTab"].pack()
                preferencesWindow.protocol("WM_DELETE_WINDOW", self.withdraw_preferences)
                preferencesWindow.withdraw()
            else:
                self.tab_dictionary[eachTab]["TkFrameForTab"] = ttk.Frame(self.sub_container)
                self.sub_container.add(self.tab_dictionary[eachTab]["TkFrameForTab"], text=self.tab_dictionary[eachTab]["Name"], image=self.tab_dictionary[eachTab]["TkPhotoImageForTab"], compound=tk.TOP)

            #self.tab_dictionary[eachTab]["TkFrameForTab"] = ttk.Frame(self.subContainer)
            #self.subContainer.add(self.tab_dictionary[eachTab]["TkFrameForTab"], text=self.tab_dictionary[eachTab]["Name"], image=self.tab_dictionary[eachTab]["TkPhotoImageForTab"], compound=tk.TOP)
            
            self.labelFramesForTab(eachTab)
            
        self.stop_progress()
        if not fromChooseGameWindow:
            self.updateValues()
        self.start_progress()
        self.bindTkVars()
        
        #self.theCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.show_sub_container()
        #self.showStatusBar()
        self.stop_progress()
        self.sme('Loading complete.')
        
    def bindTkVars(self):
        for eachSetting in self.setting_dictionary:
            TkVar = self.setting_dictionary[eachSetting].get('TkVar')
            if TkVar:
                self.setting_dictionary[eachSetting]["TkVar"].trace_add('write', lambda var, indx, mode, setting=eachSetting:self.assignValue(var, indx, mode, setting))
            forceSelect = self.setting_dictionary[eachSetting].get('forceSelect')
            if forceSelect:
                self.assignValue(1, 2, 3, eachSetting)

    def updateValues(self):
        self.start_progress()
        self.sme('Updating INI values.')
        for eachSetting in self.setting_dictionary:
            self.widgetTypeSwitcher(eachSetting)
        self.sme('Checking for dependent settings.')
        self.dependents()
        self.sme('Update values complete.')
        self.stop_progress()

    def dependents(self):
        #self.dependent_settings_dictionary
        for setting in self.dependent_settings_dictionary:
            for masterSetting in self.dependent_settings_dictionary[setting]:
                
                theOperator = self.dependent_settings_dictionary[setting][masterSetting].get('operator')
                setToOff = self.dependent_settings_dictionary[setting][masterSetting].get('setToOff', False)
                if theOperator == 'equal' or theOperator == 'not-equal':
                    value = self.dependent_settings_dictionary[setting][masterSetting].get('value')
                    currentValue = self.widgetTypeSwitcher(masterSetting)
                    var = 'string'
                else:
                    value = float(self.dependent_settings_dictionary[setting][masterSetting].get('value'))
                    currentValue = float(self.widgetTypeSwitcher(masterSetting))
                    var = 'float'
                theOperator = operatorDict[theOperator]
                TkWidgetTwo = self.setting_dictionary[setting].get('TkWidgetTwo')
                if theOperator(currentValue, value):
                    self.setting_dictionary[setting]['TkWidget'].configure(state='normal')
                    if TkWidgetTwo:
                        TkWidgetTwo.configure(state='normal')
                else:
                    if setToOff:
                        offvalue = self.dependent_settings_dictionary[setting][masterSetting].get('offvalue')
                        self.setting_dictionary[setting]['TkVar'].set(offvalue)
                    self.setting_dictionary[setting]['TkWidget'].configure(state='disabled')
                    if TkWidgetTwo:
                        TkWidgetTwo.configure(state='disabled')

                if not self.settings_that_settings_depend_on.get(masterSetting):
                    self.settings_that_settings_depend_on[masterSetting] = {}

                self.settings_that_settings_depend_on[masterSetting][setting] = {
                    'theOperator': operatorDict[self.dependent_settings_dictionary[setting][masterSetting].get('operator')],
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
        INILocation = APP.inis(ini)
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
        #targetINIs = self.tab_dictionary[eachTab]["LabelFrames"][TheLabelFrame]["SettingFrames"][onFrame][TheSetting].get("targetINIs")
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
                        defaultValue = APP.get_value(currentSetting, "default")

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
        openINI = self.open_inis.get(INI)
        if openINI:
            openINIlocation = self.open_inis[INI]['located']
            wID = 0
            for eachLocation in openINIlocation:
                wID += 1
                if openINIlocation[eachLocation]['at'] == location:
                    return openINIlocation[eachLocation].get('object')
            #if the location is not found, add it
            wID += 1
            wID = str(wID)
            self.open_inis[INI]['located'][wID] = {
                'at':location
                }
            self.open_inis[INI]['located'][wID]['object'] = ModifyINI(location + INI)
            return self.open_inis[INI]['located'][wID]['object']
        else:
            wID = "1"
            self.open_inis[INI] = {
                'located': {
                    wID: {
                        'at': location
                        }
                    }
                }
            self.open_inis[INI]['located'][wID]['object'] = ModifyINI(location + INI)
            return self.open_inis[INI]['located'][wID]['object']

def onClosing():
    if messagebox.askyesno("Quit?", "Do you want to quit?"):
        if appConfig.HasBeenModified:
            appConfig.writeINI(1)
        window.save_ini_files()
        window.quit()

def removeExcessDirFiles(theDir, maxToKeep, filesToRemove):
    try:
        sub = os.listdir(theDir)
    except OSError as e:
        sm(f"Info: {theDir} : {e.strerror}")
        return True
    sub.sort(reverse=True)
    if 'First-Time-Backup' in sub:
        sub.remove('First-Time-Backup')
    if maxToKeep > -1:
        for n in range(len(sub)):
            if n < maxToKeep:
                sm(sub[n] + ' will be kept.')
            else:
                dir_path = f'{theDir}\\' + sub[n]
                try:
                    for file in filesToRemove:
                        try:
                            os.remove(f'{dir_path}\\{file}')
                        except OSError as e:
                            sm(f'Error: {dir_path}\\{file} : {e.strerror}')
                    os.rmdir(dir_path)
                    sm(sub[n] + ' was removed.')
                except OSError as e:
                    sm(f"Error: {dir_path} : {e.strerror}")
    return False

cwd = os.getcwd()

#This dictionary maps the operator modules to specific text.
operatorDict = {
    'greater-than': gt,
    'greater-or-equal-than': ge,
    'less-than': lt,
    'less-or-equal-than': le,
    'not-equal': ne,
    'equal': eq
    }

#Specify the name of the application.
MyAppName = "Bethini Pie"
MyAppShortName = "Bethini"

if __name__ == '__main__':
    #Make logs.
    today = datetime.now()
    logDirectoryDate = today.strftime("%Y %b %d %a - %H.%M.%S")
    MyAppNameLogDirectory = f'logs\\{logDirectoryDate}'
    MyAppNameLog = f'{MyAppNameLogDirectory}\\log.log'
    os.makedirs(MyAppNameLogDirectory)
    logging.basicConfig(filename=MyAppNameLog, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    #Get app config settings.
    MyAppNameConfig = f'{MyAppShortName}.ini'
    appConfig = ModifyINI(MyAppNameConfig)
    iMaxLogs = appConfig.getValue('General', 'iMaxLogs', '5')
    appConfig.assignINIValue('General', 'iMaxLogs', iMaxLogs)
    appConfig.assignINIValue('General', 'iMaxBackups', appConfig.getValue('General', 'iMaxBackups', '5'))
    
    theme = appConfig.getValue('General', 'sTheme', default='Default')

    #Remove excess log files.
    removeExcessDirFiles(f'{cwd}\\logs', int(iMaxLogs), ['log.log'])

    #Check to make sure the theme actually exists.
    if os.path.isfile(f'{cwd}\\theme\\{theme}\\theme.ini'):
        sm(f'The theme called \"{theme}\" exists.')
    else:
        #If the theme doesn't exist, revert to Default theme.
        theme = 'Default'
    #Make sure that the theme is specified in the config file.
    appConfig.assignINIValue('General', 'sTheme', theme)

    #Open Theme config.
    ThemeConfig = ModifyINI(f'theme\\{theme}\\theme.ini')
    defaultFontName = 'Segoe UI' #Set the default font name.
    defaultFontSize = 10 #Set the default font size.

    #Set the font names and sizes.
    smallFontSize = ThemeConfig.getValue('Fonts','iSmallFontSize', defaultFontSize)
    smallFont = (ThemeConfig.getValue('Fonts','sSmallFontName', defaultFontName), smallFontSize)

    #Set the theme colors.
    buttonBarColor = ThemeConfig.getValue('Colors','sButtonBarColor','#969696')
    containerColor = ThemeConfig.getValue('Colors','sContainerColor','#555555')
    subContainerColor = ThemeConfig.getValue('Colors','sSubContainerColor','#A5A5A5')
    dropdownColor = ThemeConfig.getValue('Colors','sDropDownColor','#BEBEBE')
    fieldColor = ThemeConfig.getValue('Colors','sFieldColor','#FFFFFF')
    indicatorColor = ThemeConfig.getValue('Colors','sIndicatorColor','#FFFFFF')
    textColor = ThemeConfig.getValue('Colors','sTextColor','#000000')

    textColorDisabled = ThemeConfig.getValue('Colors','sTextColorDisabled','#7F7F7F')
    textColorPressed = ThemeConfig.getValue('Colors','sTextColorPressed','#323232')
    textColorActive = ThemeConfig.getValue('Colors','sTextColorActive','#000000')

    backgroundColorDisabled = ThemeConfig.getValue('Colors','sBackgroundColorDisabled','#E1E1E1')
    backgroundColorPressed = ThemeConfig.getValue('Colors','sBackgroundColorPressed','#828282')
    backgroundColorActive = ThemeConfig.getValue('Colors','sBackgroundColorActive','#A5A5A5')

    #Start the app class
    window = BethiniApp()
    window.protocol("WM_DELETE_WINDOW", onClosing)
    window.mainloop()

