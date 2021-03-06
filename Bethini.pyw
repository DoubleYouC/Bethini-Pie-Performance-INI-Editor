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
            'radioPreset': self.radio_preset
            }

        self.widget_type_value = {
            'TkCheckbutton': self.checkbox_value,
            'TkOptionMenu': self.dropdown_value,
            'TkEntry': self.entry_value,
            'TkSpinbox': self.spinbox_value,
            'TkCombobox': self.combobox_value,
            'TkColor': self.color_value,
            'TkSlider': self.slider_value,
            'TkRadioPreset': self.radio_preset_value
            }

        self.widget_type_assign_value = {
            'TkCheckbutton': self.checkbox_assign_value,
            'TkOptionMenu': self.dropdownAssignValue,
            'TkEntry': self.entryAssignValue,
            'TkSpinbox': self.spinboxAssignValue,
            'TkCombobox': self.comboboxAssignValue,
            'TkColor': self.colorAssignValue,
            'TkSlider': self.sliderAssignValue
            }

        self.types_without_label = ['Checkbutton', 'preset', 'radioPreset', 'description']
        self.types_packed_left = ['Dropdown', 'Combobox', 'Entry', 'Spinbox', 'Slider', 'Color']


        theme_dir = app_config.get_value('General', 'sTheme', 'Default')

        self.open_inis = {
            MyAppNameConfig : {
                'located': {
                    '1': {
                        'at': '',
                        'object': app_config
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

    def tooltip(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_):
        CreateToolTip(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_],
                      self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tooltip"])

    def choose_game(self, forced=0):
        self.withdraw()
        # The Choose App/Game dialog window.  The window is skipped here if
        # sAppName is already set in the Bethini.ini file.
        try:
            choose_game_var = app_config.get_value('General','sAppName')
            if forced == 1:
                self.sme('Force choose game/application.')
                raise Exception("Forcing you to choose")
            if app_config.get_value('General', 'bAlwaysSelectGame', '0') == '1':
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
            self.choose_game_var = app_config.get_value('General','sAppName')
            if self.choose_game_var != game:
                self.sme(f'Change of game from {self.chooseGameVar} to {game}')
                raise Exception("App/Game specified in " + MyAppNameConfig + " differs from the game chosen, so it will be changed to the one you chose.")
        except:
            self.sme('Change of game/application', exception=1)
            app_config.assignINIValue('General','sAppName', game)
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
        #                'object': app_config
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
                                                                      int(app_config.get_value('General', 'iMaxBackups', '-1')),
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
                            for each_setting in settings:
                                if ';' in each_setting:
                                    self.sme(f'{each_setting}:{section} will be preserved, as it is a comment.')
                                elif not APP.does_setting_exist(each_ini, section, each_setting):
                                    this_ini_object.removeSetting(section, each_setting)
                                    self.sme(f'{each_setting}:{section} was removed because it is not recognized.')

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
                ini_location = app_config.get_value('Directories', ini_location)
            the_target_ini = self.open_ini(str(ini_location), str(target_ini))

            the_target_ini.assignINIValue(target_section, each_setting, this_value)
            self.sme(target_ini + " [" + target_section + "] " + each_setting + "=" + this_value)

    def remove_ini_dict(self, ini_dict):
        for each_setting in ini_dict:
            target_ini = ini_dict[each_setting]['ini']
            target_section = ini_dict[each_setting]['section']
            this_value = str(ini_dict[each_setting]['value'])

            ini_location = APP.inis(target_ini)
            if ini_location != '':
                ini_location = app_config.get_value('Directories', ini_location)
            the_target_ini = self.open_ini(str(ini_location), str(target_ini))

            current_value = the_target_ini.get_value(target_section, each_setting, this_value)

            if current_value == this_value:
                the_target_ini.removeSetting(target_section, each_setting)
                self.sme(f"{target_ini} [{target_section}] {each_setting}={this_value}, which is the default value, and since it is not set to alwaysPrint, it will be removed")

    def create_tab_image(self, each_tab):
        try:
            self.tab_dictionary[each_tab]["TkPhotoImageForTab"] = tk.PhotoImage(file = "theme\\" + theme + "\\" + self.tab_dictionary[each_tab]["Name"] + ".png")
        except:
            self.sme('No theme image for tab.', exception=1)
            self.tab_dictionary[each_tab]["TkPhotoImageForTab"] = tk.PhotoImage(file = "theme\\" + theme + "\\Blank.png")

    def label_frames_for_tab(self, each_tab):
        the_dict = self.tab_dictionary[each_tab]
        the_dict["LabelFrames"] = {}
        label_frame_number=0
        for label_frame in APP.label_frames_in_tab(the_dict["Name"]):
            label_frame_number += 1
            the_label_frame=f"LabelFrame{label_frame_number}"
            the_dict["LabelFrames"][the_label_frame] = {"Name":label_frame}
            if "NoLabelFrame" not in label_frame:
                the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"] = ttk.LabelFrame(the_dict["TkFrameForTab"], text=label_frame, width=200)
            else:
                the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"] = ttk.Frame(the_dict["TkFrameForTab"])
            if (label_frame_number) % 2 == 0:
                the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"].pack(anchor=tk.CENTER, side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            else:
                the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"].pack(anchor=tk.CENTER, side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.settings_frames_for_label_frame(each_tab, label_frame, the_label_frame)

    def settings_frames_for_label_frame(self, each_tab, label_frame, the_label_frame):
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"] = {}
        number_of_vertically_stacked_settings = int(APP.number_of_vertically_stacked_settings(self.tab_dictionary[each_tab]["Name"], label_frame))
        setting_number = 0
        for each_setting in APP.settings_in_label_frame(self.tab_dictionary[each_tab]["Name"], label_frame):
            setting_number += 1
            on_frame = "SettingFrame" + str(math.ceil(setting_number / number_of_vertically_stacked_settings) - 1)
            if on_frame not in self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"]:
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame] = {}
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame]["TkSettingFrame"] = ttk.Frame(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["TkLabelFrame"])
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame]["TkSettingFrame"].pack(side=tk.LEFT, anchor='nw')
            the_setting = "Setting" + str(setting_number)
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting] = {"Name":each_setting}
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"] = ttk.Frame(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame]["TkSettingFrame"])
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"].pack(anchor='w', padx='5', pady='2')
            if 'Placeholder' not in each_setting:
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].update(APP.get_all_fields_for_setting(self.tab_dictionary[each_tab]["Name"], label_frame, each_setting))
                self.setting_label(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting)

    def setting_label(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        setting_type = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("type")
        if setting_type not in self.types_without_label:
            if setting_type:
                setting_label = each_setting
            else:
                setting_label = ''
            setting_label_width = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("customWidth")
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkLabel"] = ttk.Label(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                                   text=setting_label, font=smallFont, width=setting_label_width, anchor=tk.E)
            if setting_type in self.types_packed_left:
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkLabel"].pack(anchor=tk.CENTER, side=tk.LEFT, padx=5, pady=5)
            else:
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkLabel"].pack(anchor=tk.CENTER, padx=5, pady=5)
        setting_description = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("Description")
        if setting_description:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkDescriptionLabel"] = ttk.Label(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                                              text=setting_description, font=smallFont, justify="left", wraplength=900)
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkDescriptionLabel"].pack(anchor=tk.N)
        self.setting_type_switcher(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, setting_type)

    def setting_type_switcher(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, setting_type):
        func = self.widget_type_function.get(setting_type, "Invalid")
        if func != "Invalid":
            func(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting)

    def widget_type_switcher(self, each_setting):
        id_ = self.setting_dictionary[each_setting].get('id')
        func = self.widget_type_value.get(id_, "Invalid")
        if func != "Invalid":
            return func(each_setting)

    def add_to_setting_dictionary(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_):
        stuff_to_add_to_setting_dictionary = {
            each_setting : {
                'each_tab': each_tab,
                'label_frame': label_frame,
                'the_label_frame': the_label_frame,
                'on_frame': on_frame,
                'the_setting': the_setting,
                'id': id_,
                'tk_widget': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_],
                'targetINIs': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('targetINIs'),
                'settings': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('settings'),
                'targetSections': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('targetSections')
                }
            }

        self.setting_dictionary.update(stuff_to_add_to_setting_dictionary)

        dependent_settings = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('dependentSettings')
        if dependent_settings:
            self.dependent_settings_dictionary[each_setting] = dependent_settings

    def checkbox(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        #creates the Checkbutton widget
        id_ = "TkCheckbutton"
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)
        on_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("Onvalue")
        off_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("Offvalue")
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Checkbutton(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                              text=each_setting, variable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
                                                                                                                              onvalue=on_value, offvalue=off_value)
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].var = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"]
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor='w', padx=5, pady=3.5)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
            'onvalue': on_value,
            'offvalue': off_value
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def preset(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        #creates a preset button
        id_ = "TkPresetButton"

        preset_id = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("preset id")
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Button(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                         text=each_setting, command=lambda: self.set_preset(preset_id))
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=2)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

    def radio_preset(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        #creates the radio preset button
        id_ = 'TkRadioPreset'
        value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('value')
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Radiobutton(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                              text=each_setting,
                                                                                                                              variable=self.preset_var, value=value)
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=4)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.preset_var
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def dropdown(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        #creates the OptionMenu widget
        id_ = "TkOptionMenu"

        options = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("choices")
                        
        #custom functions allow us to auto-detect certain
        #predefined options that can then easily be selected.

        if type(options) == str:
            if 'FUNC' in options:
                option_string = APP.custom(options)
                if '{}' in option_string:
                    custom_function = APP.custom(f'{options}Format')
                    value_to_insert = getattr(CustomFunctions, custom_function)(GAME_NAME)
                    options = value_to_insert
        else:
            for n in range(len(options)):
                if 'FUNC' in options[n]:
                    option_string = APP.custom(options[n])
                    if '{}' in option_string:
                        custom_function = APP.custom(str(options[n]) + 'Format')
                        value_to_insert = getattr(CustomFunctions, custom_function)(GAME_NAME)
                        options[n] = option_string.format(value_to_insert)

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.OptionMenu(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                             self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
                                                                                                                             options[0], *options,
                                                                                                                             command=lambda c,var=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
                                                                                                                             browse=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("browse"),
                                                                                                                             function=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("custom_function"):
                                                                                                                             var.set(browse_to_location(c, browse, function, GAME_NAME)))
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].var = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"]
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
            'options': options,
            'settingChoices': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('settingChoices'),
            'delimiter': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('delimiter'),
            'decimal places': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('decimal places'),
            'fileFormat': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('fileFormat'),
            'forceSelect': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('forceSelect'),
            'partial': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('partial')
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def combobox(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        id_ = 'TkCombobox'
        options = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("choices")
        width = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("width")
        validate = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("validate")

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)
        
        if validate:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"] = self.register(self.validate)
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Combobox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                           textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
                                                                                                                           width=width, values=options, validate='key', validatecommand=(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"],'%P','%s',validate))
        else:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Combobox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                           textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
                                                                                                                           width=width, values=options)
        
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
            'options': options,
            'decimal places': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('decimal places')
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def entry(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        #creates the Entry widget
        id_ = "TkEntry"
        entry_width = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("entry_width")
        validate = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("validate")

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)

        if validate:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"] = self.register(self.validate)
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Entry(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        width=entry_width, validate='key', font=smallFont,
                                                                                                                        validatecommand=(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        else:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Entry(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        width=entry_width, font=smallFont,
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
            'formula': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("formula"),
            'decimal places': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("decimal places"),
            'partial': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("partial"),
            'fileFormat': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("fileFormat")
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def slider(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        id_ = "TkSlider"
        from_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("from")
        to_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("to")
        resolution_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("resolution")
        digits_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("digits")
        length_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("length")

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = tk.Scale(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        from_=from_value, to=to_value, resolution=resolution_value, showvalue=0, digits=digits_value, orient=tk.HORIZONTAL, relief=tk.FLAT,
                                                                                                                        highlightthickness=0, bg=subContainerColor, length=length_value, font=smallFont, activebackground=backgroundColorActive,
                                                                                                                        troughcolor=fieldColor,
                                                                                                                        variable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])

        width = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("width")
        validate = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("validate")
        increment_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("increment")

        reversed_ = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("reversed")
        if reversed_:
            from_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("to")
            to_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("from")

        if validate:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"] = self.register(self.validate)
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["second_tk_widget"] = ttk.Spinbox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        width=width, validate='key', increment=increment_value, from_=from_value, to=to_value, font=smallFont,
                                                                                                                        validatecommand=(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        else:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["second_tk_widget"] = ttk.Spinbox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        width=width, increment=increment_value, from_=from_value, to=to_value, font=smallFont,
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["second_tk_widget"].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, "second_tk_widget")
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
            'decimal places': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("decimal places"),
            'second_tk_widget': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["second_tk_widget"]
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def spinbox(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        id_ = "TkSpinbox"
        from_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("from")
        to_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("to")
        increment = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("increment")
        width = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("width")
        validate = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("validate")

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)

        if validate:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"] = self.register(self.validate)
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Spinbox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        from_=from_value, to=to_value, increment=increment, width=width, validate='key', font=smallFont,
                                                                                                                        validatecommand=(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        else:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Spinbox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        from_=from_value, to=to_value, increment=increment, width=width, font=smallFont,
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"]
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def color(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        #chooseColor(colorToChange, buttonToModify)
        id_ = "TkColor"

        color_value_type = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("colorValueType")

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)
        if color_value_type == 'hex':
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"].set('#FFFFFF')
        elif color_value_type == 'rgb':
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"].set('(255, 255, 255)')
        elif color_value_type == 'rgb 1':
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"].set('(1.0000, 1.0000, 1.0000)')
        elif color_value_type == 'decimal':
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"].set('16777215')
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = tk.Button(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
                                                                                                                        font=smallFont,
                                                                                                                        command=lambda: self.choose_color(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_],
                                                                                                                                                         color_value_type))
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].var = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"]
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=0, side=tk.RIGHT)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        stuff_to_add_to_setting_dictionary = {
            'tk_var': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
            'colorValueType': color_value_type,
            'rgbType': self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("rgbType")
            }
        self.setting_dictionary[each_setting].update(stuff_to_add_to_setting_dictionary)

    def radio_preset_value(self, each_setting):
        return self.preset_var.get()

    def checkbox_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'))
        
        if setting_value != [] and 'Does Not Exist' not in setting_value:
            on_value = self.setting_dictionary[each_setting].get('onvalue')
            off_value = self.setting_dictionary[each_setting].get('offvalue')
            if setting_value == on_value:
                this_value = on_value
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            elif setting_value == off_value:
                this_value = off_value
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            else:
                this_value = []
                for n in range(len(setting_value)):
                    if setting_value[n] in on_value[n]:
                        this_value.append(1)
                    else:
                        this_value.append(0)

                if all(this_value):
                    this_value = on_value
                else:
                    this_value = off_value
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            try:
                self.sme(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                self.sme(f'No value set for checkbox {each_setting}.')

    def dropdown_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'),
                                             self.setting_dictionary[each_setting].get('settingChoices'), 
                                             self.setting_dictionary[each_setting].get('delimiter'))

        if setting_value != [] and 'Does Not Exist' not in setting_value:
            decimal_places = self.setting_dictionary[each_setting].get("decimal places")
            if decimal_places:
                decimal_places = int(decimal_places)
                this_value = round(float(setting_value[0]), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)
                self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            else:
                file_format = self.setting_dictionary[each_setting].get("fileFormat")
                if file_format:
                    this_value = os.path.split(setting_value[0])
                    if file_format == "directory":
                        if this_value[0] != '':
                            this_value = this_value[0]
                            if this_value[-1] != '\\':
                                this_value += '\\'
                        else:
                            this_value = this_value[0]
                    if file_format == "file":
                        this_value = this_value[1]
                    self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                else:
                    setting_choices = self.setting_dictionary[each_setting].get("settingChoices")
                    if setting_choices and setting_value[0] not in setting_choices:
                        this_value = "Custom"
                        self.setting_dictionary[each_setting]["tk_var"].set(this_value)
                    else:
                        this_value = setting_value[0]
                        self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            self.sme(f"{each_setting} = {this_value}")
            self.setting_dictionary[each_setting]['valueSet'] = True
            return this_value

    def combobox_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'))
        if setting_value != [] and 'Does Not Exist' not in setting_value:
            this_value = setting_value[0]

            decimal_places = self.setting_dictionary[each_setting].get("decimal places")
            if decimal_places:
                decimal_places = int(decimal_places)
                this_value = round(float(this_value), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)
            
            self.setting_dictionary[each_setting]["tk_var"].set(this_value)
            self.sme(f"{each_setting} = {this_value}")
            self.setting_dictionary[each_setting]['valueSet'] = True
            return this_value

    def entry_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'))
        if setting_value != [] and 'Does Not Exist' not in setting_value:
            formula = self.setting_dictionary[each_setting].get("formula")
            file_format = self.setting_dictionary[each_setting].get("fileFormat")
            if formula:
                decimal_places = int(self.setting_dictionary[each_setting].get("decimal places"))
                this_value = round(simple_eval(formula.format(setting_value[0])), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)
            elif file_format:
                this_value = setting_value[0]
                if file_format == "file":
                    this_value = os.path.split(this_value)
                    this_value = this_value[1]
            else:
                this_value = setting_value[0]
            try:
                self.setting_dictionary[each_setting]['tk_var'].set(this_value)
                self.sme(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                self.sme(f'No value set for entry {each_setting}.')

    def slider_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'))

        if setting_value != [] and 'Does Not Exist' not in setting_value:
            this_value = setting_value[0]

            decimal_places = self.setting_dictionary[each_setting].get("decimal places")
            if decimal_places:
                decimal_places = int(decimal_places)
                this_value = round(float(this_value), decimal_places)
                if decimal_places == 0:
                    this_value = int(this_value)
            
            try:
                self.setting_dictionary[each_setting]['tk_var'].set(this_value)
                self.sme(f'{each_setting} = {this_value}')
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                self.sme(f'no value set for slider {each_setting}')

    def spinbox_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'))
        if setting_value != [] and 'Does Not Exist' not in setting_value:
            this_value = setting_value[0]
            try:
                self.setting_dictionary[each_setting]['tk_var'].set(this_value)
                self.sme(f'{each_setting} = {this_value}')
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                self.sme(f'no value set for spinbox {each_setting}')

    def color_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'))
        
        if setting_value != [] and 'Does Not Exist' not in setting_value:
            color_value_type = self.setting_dictionary[each_setting].get("colorValueType")
            if color_value_type == 'hex':
                this_value = setting_value[0]
                new_color = this_value
            elif color_value_type == 'decimal':
                this_value = setting_value[0]
                #convert decimal value to hex
                new_color = rgb_to_hex(decimal_to_rgb(setting_value[0]))
            elif color_value_type == 'rgb':
                rgb_type = self.setting_dictionary[each_setting].get("rgbType")
                if rgb_type == 'multiple settings':
                    this_value = tuple(int(i) for i in setting_value)
                    new_color = rgb_to_hex(this_value)
                    this_value = str(this_value)
                else:
                    this_value = '('
                    for n in range(len(setting_value)):
                        this_value += setting_value[n]
                    this_value += ')'
                    print(this_value)
                    new_color = rgb_to_hex(ast.literal_eval(this_value))
            elif color_value_type == 'rgb 1':
                rgb_type = self.setting_dictionary[each_setting].get("rgbType")
                if rgb_type == 'multiple settings':
                    this_value = tuple(round(float(i),4) for i in setting_value)
                    new_color = rgb_to_hex(tuple(int(float(i)*255) for i in setting_value))
                    this_value = str(this_value)
            self.setting_dictionary[each_setting]['tk_var'].set(this_value)
            tk_widget = self.setting_dictionary[each_setting].get("tk_widget")
            rgb = hex_to_rgb(new_color)
            luminance = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
            if luminance < 128:
                the_text_color = '#FFFFFF'
            else:
                the_text_color = '#000000'
            tk_widget.configure(bg=new_color, activebackground=new_color, fg=the_text_color)
            self.sme(f"{each_setting} = {this_value}")
            self.setting_dictionary[each_setting]['valueSet'] = True
            return this_value

    def check_dependents(self, each_setting):
        for each_dependent_setting in self.settings_that_settings_depend_on[each_setting]:
            var = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get('var')
            
            the_operator = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get('theOperator')
            value = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get('value')
            current_value = self.widget_type_switcher(each_setting)
            second_tk_widget = self.setting_dictionary[each_dependent_setting].get('second_tk_widget')
            if var == 'float':
                value = float(value)
                current_value = float(current_value)
            if the_operator(current_value, value):
                self.setting_dictionary[each_dependent_setting]['tk_widget'].configure(state='normal')
                if second_tk_widget:
                    second_tk_widget.configure(state='normal')
            else:
                set_to_off = self.settings_that_settings_depend_on[each_setting][each_dependent_setting].get('setToOff')
                if set_to_off:
                    off_value = self.setting_dictionary[each_dependent_setting].get('offvalue')

                    self.setting_dictionary[each_dependent_setting]['tk_var'].set(off_value)
                self.setting_dictionary[each_dependent_setting]['tk_widget'].configure(state='disabled')
                if second_tk_widget:
                    second_tk_widget.configure(state='disabled')

    def assign_value(self, var, indx, mode, each_setting):
        id_ = self.setting_dictionary[each_setting].get('id')
        func = self.widget_type_assign_value.get(id_, "Invalid")
        if func != "Invalid":
            func(each_setting)
        
        if each_setting in list(self.settings_that_settings_depend_on.keys()):
            self.check_dependents(each_setting)

    def checkbox_assign_value(self, each_setting):
        tk_var = self.setting_dictionary[each_setting].get('tk_var')
        
        this_value = tk_var.get()
        #this_value is whatever the state of the on_value/off_value is... not a simple boolean


        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')
        targetSections = self.setting_dictionary[each_setting].get('targetSections')
        theSettings = self.setting_dictionary[each_setting].get('settings')
        
        on_value = self.setting_dictionary[each_setting].get('onvalue')
        off_value = self.setting_dictionary[each_setting].get('offvalue')

        setting_value = self.get_setting_values(targetINIs, targetSections, theSettings)
        
        try:
            this_value = list(ast.literal_eval(this_value))
            for n in range(len(this_value)):
                if type(this_value[n]) is tuple:
                    this_value[n] = list(this_value[n])
        except:
            self.sme(f'{this_value} .... Make sure that the {each_setting} checkbutton Onvalue and Offvalue are lists within lists in the json.', exception=1)

        #print(this_value, onvalue, off_value)

        if targetINIs:
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = self.open_ini(str(ini_location), str(targetINIs[n]))
                #1
                if this_value == on_value or this_value == off_value:
                    if type(this_value[n]) is list:
                        if setting_value[n] in this_value[n]:
                            theValue = setting_value[n]
                        elif this_value[n][0] in self.setting_dictionary:
                            self.assign_value(1,2,3, this_value[n][0])
                            continue
                        else:
                            theValue = this_value[n][0]
                            the_target_ini.assignINIValue(targetSections[n], theSettings[n], theValue)
                            self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                        the_target_ini.assignINIValue(targetSections[n], theSettings[n], theValue)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                    else:
                        the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value[n])
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value[n])

    def dropdownAssignValue(self, each_setting):
        tk_var = self.setting_dictionary[each_setting].get('tk_var')
        this_value = tk_var.get()
        #print(this_value)
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')
        targetSections = self.setting_dictionary[each_setting].get('targetSections')
        theSettings = self.setting_dictionary[each_setting].get('settings')

        setting_choices = self.setting_dictionary[each_setting].get('settingChoices')
        delimiter = self.setting_dictionary[each_setting].get('delimiter')
        file_format = self.setting_dictionary[each_setting].get('fileFormat')
        #decimal_places = self.setting_dictionary[each_setting].get('decimal places')
        partial = self.setting_dictionary[each_setting].get('partial')
        theValueStr = ''
        if partial:
            for each_partial_setting in partial:
                if each_partial_setting == each_setting:
                    theValueStr += '{}'
                else:
                    try:
                        if self.setting_dictionary[each_partial_setting]['valueSet']:
                            theValueStr += self.setting_dictionary[each_partial_setting]['tk_var'].get()
                        else:
                            self.sme(f'{each_partial_setting} is not set yet.')
                            return
                    except:
                        self.sme(f'{each_partial_setting} is not set yet.', exception=True)
                        return

        
        if targetINIs:
            for n in range(len(targetINIs)):
                theValue = ''
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = self.open_ini(str(ini_location), str(targetINIs[n]))
                #1280x720
                if this_value == 'Manual...' or this_value == 'Browse...':
                    theValue = ''
                elif delimiter:
                    listOfValues = this_value.split(delimiter)
                    try:
                        theValue = listOfValues[n]
                    except IndexError:
                        theValue = ''
                elif setting_choices:
                    if this_value not in setting_choices:
                        return
                    else:
                        theValue = setting_choices[this_value][n]
                elif file_format:
                    if file_format == 'directory':
                        if this_value == '\\':
                            this_value = this_value[:-1]
                    theValue = this_value
                else:
                    theValue = this_value

                if partial:
                    theValue = theValueStr.format(this_value)
                the_target_ini.assignINIValue(targetSections[n], theSettings[n], theValue)
                self.sme(f'{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}')

    def comboboxAssignValue(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            decimal_places = self.setting_dictionary[each_setting].get('decimal places')
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = self.open_ini(str(ini_location), str(targetINIs[n]))

                if decimal_places and this_value != '':
                    this_value = round(float(this_value),int(decimal_places))
                    if decimal_places == "0":
                        this_value = int(this_value)
                    this_value = str(this_value)

                the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def entryAssignValue(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')
       
        partial = self.setting_dictionary[each_setting].get('partial')
        theValueStr = ''
        if partial:
            for each_partial_setting in partial:
                if each_partial_setting == each_setting:
                    theValueStr += '{}'
                else:
                    #self.widget_type_switcher(each_partial_setting)
                    if self.setting_dictionary[each_partial_setting]['valueSet']:
                        theValueStr += self.setting_dictionary[each_partial_setting]['tk_var'].get()
                    else:
                        return

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            formula = self.setting_dictionary[each_setting].get('formula')
            #decimal_places = self.setting_dictionary[each_setting].get('decimal places')

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = self.open_ini(str(ini_location), str(targetINIs[n]))

                if formula:
                    formulaValue = formula.format(this_value)
                    try:
                        this_value = str(round(simple_eval(formulaValue),8))
                    except:
                        self.sme('Failed to evaluate formula value for {this_value}.')
                #if decimal_places:
                #    this_value = round(this_value,int(decimal_places))

                if partial:
                    this_value = theValueStr.format(this_value)
                the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def sliderAssignValue(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = self.open_ini(str(ini_location), str(targetINIs[n]))

                the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def spinboxAssignValue(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')
        
        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = self.open_ini(str(ini_location), str(targetINIs[n]))

                the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def colorAssignValue(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')
        
        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            color_value_type = self.setting_dictionary[each_setting].get("colorValueType")
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = self.open_ini(str(ini_location), str(targetINIs[n]))

                if color_value_type == 'hex':
                    the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value)
                    self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)
                elif color_value_type == 'decimal':
                    the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value)
                    self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)
                elif color_value_type == 'rgb' or color_value_type == 'rgb 1':
                    if len(theSettings) > 1:
                        theValue = str(ast.literal_eval(this_value)[n])
                        the_target_ini.assignINIValue(targetSections[n], theSettings[n], theValue)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                    else:
                        this_value = this_value.lstrip('(').rstrip(')')
                        the_target_ini.assignINIValue(targetSections[n], theSettings[n], this_value)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)
                
    def createTabs(self, fromChooseGameWindow=False):
        
        for each_tab in self.tab_dictionary:
            #each_tab is Page1, Page2, etc.
            #self.tab_dictionary[each_tab]["Name"] is the name of each tab

            self.create_tab_image(each_tab)
            if self.tab_dictionary[each_tab]['Name'] == 'Setup':
                global setupWindow
                self.tab_dictionary[each_tab]['SetupWindow'] = tk.Toplevel(self)
                setupWindow = self.tab_dictionary[each_tab]['SetupWindow']
                setupWindow.title('Setup')
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(setupWindow)
                self.tab_dictionary[each_tab]["TkFrameForTab"].pack()
                setupWindow.protocol("WM_DELETE_WINDOW", self.withdraw_setup)
                if not fromChooseGameWindow:
                    setupWindow.withdraw()
            elif self.tab_dictionary[each_tab]['Name'] == 'Preferences':
                global preferencesWindow
                self.tab_dictionary[each_tab]['PreferencesWindow'] = tk.Toplevel(self)
                preferencesWindow = self.tab_dictionary[each_tab]['PreferencesWindow']
                preferencesWindow.title('Preferences')
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(preferencesWindow)
                self.tab_dictionary[each_tab]["TkFrameForTab"].pack()
                preferencesWindow.protocol("WM_DELETE_WINDOW", self.withdraw_preferences)
                preferencesWindow.withdraw()
            else:
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(self.sub_container)
                self.sub_container.add(self.tab_dictionary[each_tab]["TkFrameForTab"], text=self.tab_dictionary[each_tab]["Name"], image=self.tab_dictionary[each_tab]["TkPhotoImageForTab"], compound=tk.TOP)

            #self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(self.subContainer)
            #self.subContainer.add(self.tab_dictionary[each_tab]["TkFrameForTab"], text=self.tab_dictionary[each_tab]["Name"], image=self.tab_dictionary[each_tab]["TkPhotoImageForTab"], compound=tk.TOP)
            
            self.label_frames_for_tab(each_tab)
            
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
        for each_setting in self.setting_dictionary:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            if tk_var:
                self.setting_dictionary[each_setting]["tk_var"].trace_add('write', lambda var, indx, mode, each_setting=each_setting:self.assign_value(var, indx, mode, each_setting))
            forceSelect = self.setting_dictionary[each_setting].get('forceSelect')
            if forceSelect:
                self.assign_value(1, 2, 3, each_setting)

    def updateValues(self):
        self.start_progress()
        self.sme('Updating INI values.')
        for each_setting in self.setting_dictionary:
            self.widget_type_switcher(each_setting)
        self.sme('Checking for dependent settings.')
        self.dependents()
        self.sme('Update values complete.')
        self.stop_progress()

    def dependents(self):
        #self.dependent_settings_dictionary
        for each_setting in self.dependent_settings_dictionary:
            for masterSetting in self.dependent_settings_dictionary[each_setting]:
                
                the_operator = self.dependent_settings_dictionary[each_setting][masterSetting].get('operator')
                set_to_off = self.dependent_settings_dictionary[each_setting][masterSetting].get('setToOff', False)
                if the_operator == 'equal' or the_operator == 'not-equal':
                    value = self.dependent_settings_dictionary[each_setting][masterSetting].get('value')
                    current_value = self.widget_type_switcher(masterSetting)
                    var = 'string'
                else:
                    value = float(self.dependent_settings_dictionary[each_setting][masterSetting].get('value'))
                    current_value = float(self.widget_type_switcher(masterSetting))
                    var = 'float'
                the_operator = operatorDict[the_operator]
                second_tk_widget = self.setting_dictionary[each_setting].get('second_tk_widget')
                if the_operator(current_value, value):
                    self.setting_dictionary[each_setting]['tk_widget'].configure(state='normal')
                    if second_tk_widget:
                        second_tk_widget.configure(state='normal')
                else:
                    if set_to_off:
                        off_value = self.dependent_settings_dictionary[each_setting][masterSetting].get('offvalue')
                        self.setting_dictionary[each_setting]['tk_var'].set(off_value)
                    self.setting_dictionary[each_setting]['tk_widget'].configure(state='disabled')
                    if second_tk_widget:
                        second_tk_widget.configure(state='disabled')

                if not self.settings_that_settings_depend_on.get(masterSetting):
                    self.settings_that_settings_depend_on[masterSetting] = {}

                self.settings_that_settings_depend_on[masterSetting][each_setting] = {
                    'theOperator': operatorDict[self.dependent_settings_dictionary[each_setting][masterSetting].get('operator')],
                    'value': value,
                    'var': var,
                    'setToOff': set_to_off
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
        ini_location = APP.inis(ini)
        if ini_location == '':
            ini_location == ''
        elif ini_location == 'sTheme':
            theme_dir = app_config.get_value('General', 'sTheme', 'Default')
            ini_location = f'{cwd}\\theme\\{theme_dir}\\'
        else:
            ini_location = app_config.get_value('Directories', ini_location)
        return ini_location

    def get_setting_values(self, targetINIs, targetSections, theSettings, setting_choices=None, delimiter=None):
        #This function returns the current value of the each_setting.

        #What it needs:
        #targetINIs
        #settings
        #targetSections
        #setting_choices
        #delimiter

        settingValues = []
        #targetINIs = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("targetINIs")
        if targetINIs:
            ININumber = -1
            for INI in targetINIs:
                ININumber += 1
                #Get the Bethini.ini key for the location of the target INI
                ini_location = self.getINILocation(INI)
                if ini_location != "Does Not Exist":
                    #If the INI location is known.

                    currentSetting = theSettings[ININumber]
                    currentSection = targetSections[ININumber]

                    # This looks for a default value in the settings.json
                    if INI == MyAppNameConfig or INI == 'theme.ini':
                        defaultValue = "Does Not Exist"
                    else:
                        defaultValue = APP.get_value(currentSetting, "default")

                    #target_ini = ModifyINI(str(ini_location) + str(INI))

                    target_ini = self.open_ini(str(ini_location), str(INI))
                    value = str(target_ini.get_value(currentSection, currentSetting, default=defaultValue))
                    settingValues.append(value)
            if settingValues != []:
                #Check to see if the settings correspond with specified
                #each_setting choices.
                if setting_choices:
                    for choice in setting_choices:
                        if setting_choices[choice] == settingValues:
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

    def open_ini(self, location, INI):
        open_ini = self.open_inis.get(INI)
        if open_ini:
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
        if app_config.HasBeenModified:
            app_config.writeINI(1)
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
    app_config = ModifyINI(MyAppNameConfig)
    iMaxLogs = app_config.get_value('General', 'iMaxLogs', '5')
    app_config.assignINIValue('General', 'iMaxLogs', iMaxLogs)
    app_config.assignINIValue('General', 'iMaxBackups', app_config.get_value('General', 'iMaxBackups', '5'))
    
    theme = app_config.get_value('General', 'sTheme', default='Default')

    #Remove excess log files.
    removeExcessDirFiles(f'{cwd}\\logs', int(iMaxLogs), ['log.log'])

    #Check to make sure the theme actually exists.
    if os.path.isfile(f'{cwd}\\theme\\{theme}\\theme.ini'):
        sm(f'The theme called \"{theme}\" exists.')
    else:
        #If the theme doesn't exist, revert to Default theme.
        theme = 'Default'
    #Make sure that the theme is specified in the config file.
    app_config.assignINIValue('General', 'sTheme', theme)

    #Open Theme config.
    ThemeConfig = ModifyINI(f'theme\\{theme}\\theme.ini')
    defaultFontName = 'Segoe UI' #Set the default font name.
    defaultFontSize = 10 #Set the default font size.

    #Set the font names and sizes.
    smallFontSize = ThemeConfig.get_value('Fonts','iSmallFontSize', defaultFontSize)
    smallFont = (ThemeConfig.get_value('Fonts','sSmallFontName', defaultFontName), smallFontSize)

    #Set the theme colors.
    buttonBarColor = ThemeConfig.get_value('Colors','sButtonBarColor','#969696')
    containerColor = ThemeConfig.get_value('Colors','sContainerColor','#555555')
    subContainerColor = ThemeConfig.get_value('Colors','sSubContainerColor','#A5A5A5')
    dropdownColor = ThemeConfig.get_value('Colors','sDropDownColor','#BEBEBE')
    fieldColor = ThemeConfig.get_value('Colors','sFieldColor','#FFFFFF')
    indicatorColor = ThemeConfig.get_value('Colors','sIndicatorColor','#FFFFFF')
    textColor = ThemeConfig.get_value('Colors','sTextColor','#000000')

    textColorDisabled = ThemeConfig.get_value('Colors','sTextColorDisabled','#7F7F7F')
    textColorPressed = ThemeConfig.get_value('Colors','sTextColorPressed','#323232')
    textColorActive = ThemeConfig.get_value('Colors','sTextColorActive','#000000')

    backgroundColorDisabled = ThemeConfig.get_value('Colors','sBackgroundColorDisabled','#E1E1E1')
    backgroundColorPressed = ThemeConfig.get_value('Colors','sBackgroundColorPressed','#828282')
    backgroundColorActive = ThemeConfig.get_value('Colors','sBackgroundColorActive','#A5A5A5')

    #Start the app class
    window = BethiniApp()
    window.protocol("WM_DELETE_WINDOW", onClosing)
    window.mainloop()

