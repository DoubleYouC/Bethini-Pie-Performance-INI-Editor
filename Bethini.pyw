#
#This work is licensed under the
#Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
#or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import ast
import configparser
import os
import sys
import math
import webbrowser
from shutil import copyfile
from datetime import datetime
from operator import gt, ge, lt, le, ne, eq
#from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR, S_IWGRP, S_IWRITE
#This is for changing file read-only access via os.chmod(filename, S_IREAD,
#S_IRGRP, #S_IROTH) Not currently used.

import logging

# configure logging
LOG_DIR_DATE: str = f'{datetime.now().strftime("%Y %m-%b %d %a - %H.%M.%S")}' # TODO refactor usage of 'the_backup_directory'
APP_LOG_DIR = os.path.join("logs",LOG_DIR_DATE)
APP_LOG_FILE: str = os.path.join("logs", LOG_DIR_DATE, "log.log")

fmt: str = '%(asctime)s  [%(levelname)s]  %(filename)s  %(funcName)s:%(lineno)s:  %(message)s'
datefmt: str  = '%Y-%m-%d %H:%M:%S'
if not os.path.exists(APP_LOG_DIR):
    os.makedirs(APP_LOG_DIR)

logging.basicConfig(filename=APP_LOG_FILE, filemode='w', format=fmt, datefmt=datefmt, encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger() # this is the root logger
_log_stdout = logging.StreamHandler(sys.stdout) # to console
_log_stdout.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
logger.addHandler(_log_stdout)
logger.info(f"Logging to '{APP_LOG_FILE}'")

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.themes import standard as standThemes
from ttkbootstrap.icons import Icon
from tkinter import colorchooser
from tkinter import messagebox

from simpleeval import simple_eval

from lib.app import AppName
from lib.AutoScrollbar import AutoScrollbar
from lib.tooltips import Hovertip
from lib.ModifyINI import ModifyINI
from lib.customFunctions import CustomFunctions, browse_to_location, rgb_to_hex, rgba_to_hex,hex_to_rgb, hex_to_decimal, decimal_to_rgb

#This dictionary maps the operator modules to specific text.
operator_dictionary = {
    'greater-than': gt,
    'greater-or-equal-than': ge,
    'less-than': lt,
    'less-or-equal-than': le,
    'not-equal': ne,
    'equal': eq
    }

tkinter_switch_dict = {
    'Left': tk.LEFT,
    'Right': tk.RIGHT,
    'Top': tk.TOP,
    'Bottom': tk.BOTTOM,
    'X': tk.X,
    'Y': tk.Y,
    'Center': tk.CENTER,
    'Both': tk.BOTH,
    'Horizontal': tk.HORIZONTAL,
    'Flat': tk.FLAT,
    'N': tk.N,
    'NE': tk.NE,
    'NW': tk.NW,
    'NS': tk.NS,
    'NSEW': tk.NSEW,
    'S': tk.S,
    'SE': tk.SE,
    'SW': tk.SW,
    'E': tk.E,
    'EW': tk.EW,
    'W': tk.W,
    'None': None
}

types_without_label = ['Checkbutton', 'preset', 'radioPreset', 'description']
types_packed_left = ['Dropdown', 'Combobox', 'Entry', 'Spinbox', 'Slider', 'Color']

current_working_directory = os.getcwd()

#Specify the name of the application.
my_app_name = "Bethini Pie"
my_app_short_name = "Bethini"

def set_theme(style_object, root, theme_name):
    """ Sets the theme. """
    style_object.theme_use(theme_name)
    style_object.configure('choose_game_button.TButton', font=('Segoe UI', '14'))
    app_config.assign_setting_value('General', 'sTheme', theme_name)

class Scalar(ttk.Scale):
    """ ttk.Scale with limited decimal places """

    def __init__(self, *args, **kwargs):
        self.decimal_places = kwargs.pop('decimal_places')
        self.chain = kwargs.pop('command', lambda *a: None)
        super(Scalar, self).__init__(*args, command=self._value_changed, **kwargs)

    def _value_changed(self, new_value):
        decimal_places = int(self.decimal_places)
        new_value = round(float(new_value), decimal_places)
        if decimal_places == 0:
            new_value = int(new_value)
        self.winfo_toplevel().globalsetvar(self.cget('variable'), (new_value))
        self.chain(new_value)

class bethini_app(ttk.Window):
    #This is the main app, the glue that creates the GUI.

    def __init__(self, *args, **kwargs):
        #You need args for lists and kwargs for dictionaries passed to tkinter
        ttk.Window.__init__(self, *args, **kwargs)

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
            'TkOptionMenu': self.dropdown_assign_value,
            'TkEntry': self.entry_assign_value,
            'TkSpinbox': self.spinbox_assign_value,
            'TkCombobox': self.combobox_assign_value,
            'TkColor': self.color_assign_value,
            'TkSlider': self.slider_assign_value
            }

        # ttk style overrides
        self.s = ttk.Style()

        self.the_canvas = ttk.Canvas(self)
        self.hsbframeholder = ttk.Frame(self)

        self.vsb = AutoScrollbar(self, orient='vertical',
                                 command=self.the_canvas.yview)
        self.hsb = AutoScrollbar(self.hsbframeholder, orient='horizontal',
                                 command=self.the_canvas.xview)
        self.the_canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.container = ttk.Frame(self.the_canvas)
        self.container.bind_all('<Control-s>', self.save_ini_files)

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

        self.choose_game_window = ttk.Toplevel(self)
        self.choose_game_window.title(f'Bethini Pie {version}')

        self.choose_game_frame = ttk.Frame(self.choose_game_window)

        self.choose_game_frame_2 = ttk.Frame(self.choose_game_frame)

        self.label_Bethini = ttk.Label(self.choose_game_frame_2, text="Bethini Pie", font=('Segoe UI', '20'))
        self.label_Pie = ttk.Label(self.choose_game_frame_2, text="Performance INI Editor\nby DoubleYou", font=('Segoe UI', '15'), justify='center', bootstyle="warning")
        self.label_link = ttk.Label(self.choose_game_frame_2, text="www.nexusmods.com/site/mods/631", font=('Segoe UI', '10'), cursor='hand2', bootstyle="info")

        self.choose_game_label = ttk.Label(self.choose_game_frame_2, text="Choose Game", font=('Segoe UI', '15'))

        self.choose_game_tree = ttk.Treeview(self.choose_game_frame_2, selectmode='browse', show='tree', columns=('Name'))
        self.choose_game_tree.column('#0', width=0, stretch=tk.NO)
        self.choose_game_tree.column('Name', anchor=tk.W, width=300)

        self.s.configure('choose_game_button.TButton', font=('Segoe UI', '14'))
        self.choose_game_button = ttk.Button(self.choose_game_frame_2, text='Select Game', style='choose_game_button.TButton',
                                             command=lambda: self.choose_game_done(self.choose_game_tree.focus()))

        self.choose_game_tip = ttk.Label(self.choose_game_frame_2, text="Tip: You can change the game at any time\nby going to File > Choose Game.", font=('Segoe UI', '12'), justify='center', bootstyle="success")
        options = os.listdir('apps/')
        for option in options:
            self.choose_game_tree.insert('', 'end', id=option, text=option, values=[option])


        self.preferences_frame = ttk.Frame(self.choose_game_frame_2)

        self.theme_label = ttk.Label(self.preferences_frame, text="Theme:")
        theme_names = standThemes.STANDARD_THEMES.keys()
        self.theme_name = tk.StringVar(self)
        self.theme_dropdown = ttk.OptionMenu(self.preferences_frame,
                                             self.theme_name, app_config.get_value('General', 'sTheme', 'superhero'), *theme_names,
                                             command=lambda t: set_theme(self.s, self, t))
        self.theme_dropdown.var = self.theme_name

        self.choose_game_frame.pack(fill=tk.BOTH, expand=True)
        self.choose_game_frame_2.pack(anchor=tk.CENTER, expand=True)

        self.label_Bethini.pack(padx=5, pady=5)
        self.label_Pie.pack(padx=5, pady=15)
        self.label_link.pack(padx=25, pady=5)
        self.label_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab('https://www.nexusmods.com/site/mods/631'))

        self.preferences_frame.pack()
        self.theme_label.pack(side=tk.LEFT)
        self.theme_dropdown.pack(padx=5, pady=15)
        self.choose_game_label.pack(padx=5, pady=2)
        self.choose_game_tree.pack(padx=10)
        self.choose_game_button.pack(pady=15)
        self.choose_game_tip.pack(pady=10)
        self.choose_game_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.choose_game_window.minsize(300,35)

        self.preset_var = tk.StringVar(self)
        self.preset_var.set('Bethini')

    def on_frame_configure(self, event):
        self.the_canvas.configure(scrollregion=self.the_canvas.bbox('all'))

    def sub_container_configure(self, event):
        the_width = event.width + 40
        the_height = event.height + 65
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

    def sme(self, message: str, exception: bool=False):
        if exception:
            logger.error(message)
        else:
            logger.debug(message)
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
        #old_color is in format (255, 255, 255)
        if color_value_type == 'rgb':
            old_color = rgb_to_hex(ast.literal_eval(old_color))
        elif color_value_type == 'rgba':
            #(255, 255, 255, 170)
            old_color_original = ast.literal_eval(old_color)
            old_color_hex = rgba_to_hex(old_color_original)
            #ffffffaa
            old_color = old_color_hex[0:7]
            #ffffff
            alpha = old_color_original[3]
            #170
            try:
                new_alpha = tk.simpledialog.askinteger("Alpha", "Alpha transparency (0 - 255):", initialvalue=alpha, minvalue = 0, maxvalue = 255)
                logger.debug(f"New alpha: {new_alpha}")
            except:
                new_alpha = alpha
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
        elif color_value_type == 'rgba':
            new_color_tuple = hex_to_rgb(new_color)
            new_color_list = list(new_color_tuple)
            new_color_list.append(new_alpha)
            new_color_tuple = tuple(new_color_list)
            button_to_modify.var.set(str(new_color_tuple).replace(' ',''))
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
        """Sets the tooltips."""

        #Fectches the tooltip description.
        tooltip_description = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("tooltip", "No description available.")

        tooltip_wrap_length = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("tooltip_wrap_length", 200)

        #Checks for INI settings specified, and adds them to the bottom of the tooltip if found.
        target_ini_files = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("targetINIs")
        if target_ini_files: #If there are INI settings specified
            target_sections = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("targetSections")
            target_settings = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("settings")

            #Place INI settings into a dictionary to filter out duplicate target INI files and sections.
            settings_location_dict = {}
            for n in range(len(target_ini_files)):
                if target_ini_files[n] not in settings_location_dict:
                    settings_location_dict[target_ini_files[n]] = {}
                if target_sections[n] not in settings_location_dict[target_ini_files[n]]:
                    settings_location_dict[target_ini_files[n]][target_sections[n]] = []
                settings_location_dict[target_ini_files[n]][target_sections[n]].append(target_settings[n])

            #Iterates through the dictionary and makes a formatted string to append to the bottom of the tooltip description.
            tooltip_INI_targets = ''
            iterator = 0
            for target_ini in settings_location_dict:
                iterator += 1
                if iterator > 1:
                    tooltip_INI_targets += '\n'
                tooltip_INI_targets += str(target_ini)

                for target_section in settings_location_dict[target_ini]:
                    tooltip_INI_targets += '\n[' + str(target_section) + ']'
                    for target_setting in settings_location_dict[target_ini][target_section]:
                        tooltip_INI_targets += '\n' + str(target_setting)
                if iterator != len(settings_location_dict):
                    tooltip_INI_targets += '\n'

            #Appends our formatted string of INI settings to the bottom of the tooltip description.
            tooltip_text = tooltip_description + '\n\n' + tooltip_INI_targets
        else: #If there are no INI settings specified, only the tooltip description will be used.
            tooltip_text = tooltip_description

        setting_name = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('Name')
        photo_for_setting = os.path.join('apps', GAME_NAME, 'images', f'{setting_name}.jpg')
        if not os.path.isfile(photo_for_setting):
            photo_for_setting = None

        Hovertip(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_], tooltip_text, [PREVIEW_WINDOW, PREVIEW_FRAME, photo_for_setting], tooltip_wrap_length)

    def choose_game(self, forced=0):
        self.withdraw()
        # The Choose App/Game dialog window.  The window is skipped here if
        # sAppName is already set in the Bethini.ini file.
        try:
            choose_game_var = app_config.get_value('General','sAppName')
            if forced == 1:
                self.sme('Force choose game/application.')
                raise NameError
            if app_config.get_value('General', 'bAlwaysSelectGame', '1') != '0':
                self.sme('Force choose game/application at startup.')
                GAME_NAME #By calling the global variable GAME_NAME before it has been created,
                         #we raise
                         #an exception to force the app/game to be chosen only
                         #at startup.
            #raise Exception("Forcing you to choose")
            self.choose_game_done(choose_game_var)
        except NameError:
            self.sme('Choose game/application.', exception=1)
            self.choose_game_window.deiconify()
        except Exception as e:
            self.sme('An unhandled exception occurred.', exception=1)
            messagebox.showerror(title='Unhandled exception', message=f'An unhandled exception occurred.\n{e}\nThis program will now close. No files will be modified.')
            self.quit()

    def choose_game_done(self, game, from_choose_game_window=False):
        if game == '':
            return
        self.choose_game_window.withdraw()

        # Once the app/game is selected, this loads it.
        try:
            self.choose_game_var = app_config.get_value('General','sAppName')
            if self.choose_game_var != game:
                self.sme(f'Change of game from {self.chooseGameVar} to {game}')
                raise Exception("App/Game specified in " + my_app_config + " differs from the game chosen, so it will be changed to the one you chose.")
        except:
            self.sme('Change of game/application', exception=1)
            app_config.assign_setting_value('General','sAppName', game)
            from_choose_game_window = True

        tk.Tk.wm_title(self,f'{my_app_name} {version} - {game}')

        ##############
        # app globals
        ##############

        global APP
        APP = AppName(game)
        global GAME_NAME
        GAME_NAME = APP.data["gameName"]
        self.sme(f'Application/game is {GAME_NAME}')

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
        for tab in APP.tabs():
            tab_number += 1
            self.tab_dictionary["Page" + str(tab_number)] = {"Name":tab}

        self.setup_dictionary = {}
        self.setting_dictionary = {}
        self.dependent_settings_dictionary = {}
        self.settings_that_settings_depend_on = {}
        self.tab = []


        if not from_choose_game_window:
            self.deiconify()
        try:
            self.createTabs(from_choose_game_window)
        except Exception as e:
            self.sme('An unhandled exception occurred.', exception=1)
            messagebox.showerror(title='Unhandled exception', message=f'An unhandled exception occurred.\n{e}\nThis program will now close. No files will be modified.')
            self.quit()
        self.menu(self.s)


    def menu(self, style_object):
        menubar = tk.Menu(self)

        # File
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="Save", command = self.save_ini_files)
        filemenu.add_separator()
        filemenu.add_command(label="Choose game", command = lambda: self.choose_game(forced=1))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command= lambda: on_closing(self))

        # Edit
        editmenu = tk.Menu(menubar, tearoff=False)
        editmenu.add_command(label="Preferences", command = preferencesWindow.deiconify)
        editmenu.add_command(label="Setup", command = self.show_setup)

        # Theme
        theme_menu = tk.Menu(menubar, tearoff=False)
        theme_names = list(standThemes.STANDARD_THEMES.keys())
        for theme_name in theme_names:
            theme_menu.add_command(label=theme_name, command = lambda t=theme_name: set_theme(style_object, self, t))

        # Help
        helpmenu = tk.Menu(menubar, tearoff=False)
        helpmenu.add_command(label="Visit Web Page",
                             command = lambda: webbrowser.open_new_tab('https://www.nexusmods.com/site/mods/631/'))
        helpmenu.add_command(label="Get Support",
                             command = lambda: webbrowser.open_new_tab('https://stepmodifications.org/forum/forum/200-Bethini-support/'))
        helpmenu.add_command(label="About", command = self.about)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Theme", menu=theme_menu)
        menubar.add_cascade(label="Help", menu=helpmenu)

        ttk.Window.config(self, menu=menubar)

    def about(self):
        about_window = ttk.Toplevel(self)
        about_window.title('About')

        about_frame = ttk.Frame(about_window)
        about_frame_real = ttk.Frame(about_frame)

        about_label = ttk.Label(about_frame_real,
                               text=f'About {my_app_name} {version}\n\n{my_app_name} was created by DoubleYou.\n\nLicensing is CC by-NC-SA.',
                               justify=tk.CENTER)

        about_frame.pack(fill=tk.BOTH, expand=True)
        about_frame_real.pack(anchor=tk.CENTER, expand=True)
        about_label.pack(anchor=tk.CENTER, padx='10', pady='10')

    def show_setup(self):
        self.withdraw()
        SETUP_WINDOW.deiconify()

    def withdraw_setup(self):
        SETUP_WINDOW.withdraw()
        self.deiconify()
        self.updateValues()

    def save_ini_files(self, keyevent="None"):
        #self.openINIs = {
        #    my_app_config : {
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
        try:
            self.apply_ini_dict(APP.preset_values('fixedDefault'), only_if_missing=True)
        except NameError as e:
            self.sme(f'NameError: {e}', True)
            return
        ini_list = list(open_inis.keys())
        files_to_remove = ini_list[1:]
        files_to_remove.append('log.log')
        for each_ini in open_inis:
            location_list = list(open_inis[each_ini]['located'].keys())
            for n in range(len(location_list)):
                this_location = open_inis[each_ini]['located'][str(n+1)].get('at')
                this_ini_object = open_inis[each_ini]['located'][str(n+1)].get('object')
                if each_ini == my_app_config:
                    continue
                if not this_ini_object.has_been_modified:
                    self.sme(f'{each_ini} has not been modified, so there is no reason to resave it.')
                    continue
                if messagebox.askyesno(f"Save {each_ini}", f"Do you want to save {this_location}{each_ini}?"):
                    #we need to make a backup of each save before actually saving.
                    first_time_backup_trigger = remove_excess_directory_files(f'{this_location}{my_app_name} backups',
                                                                    int(app_config.get_value('General', 'iMaxBackups', '-1')),
                                                                    files_to_remove)
                    if first_time_backup_trigger:
                        first_time_backup = True
                    if first_time_backup:
                        the_backup_directory = os.path.join(this_location, f'{my_app_name} backups', 'First-Time-Backup')
                        if not os.path.isdir(the_backup_directory):
                            os.makedirs(the_backup_directory)
                        if os.path.exists(f"{the_backup_directory}{each_ini}"):
                            self.sme(f'{the_backup_directory}{each_ini} exists, so it will not be overwritten.')
                        else:
                            try:
                                copyfile(f"{this_location}{each_ini}", f"{the_backup_directory}{each_ini}")
                            except FileNotFoundError:
                                self.sme(f"{this_location}{each_ini} does not exist, so it cannot be backed up. This is typically caused by a path not being set correctly.", True)
                        copyfile(APP_LOG_FILE, f"{the_backup_directory}log.log")
                    the_backup_directory = os.path.join(this_location, f'{my_app_name} backups', LOG_DIR_DATE)
                    if not os.path.isdir(the_backup_directory):
                        os.makedirs(the_backup_directory)
                    if os.path.exists(f"{the_backup_directory}{each_ini}"):
                        self.sme(f'{the_backup_directory}{each_ini} exists, so it will not be overwritten.')
                    else:
                        try:
                            copyfile(f"{this_location}{each_ini}", f"{the_backup_directory}{each_ini}")
                        except FileNotFoundError:
                            self.sme(f"{this_location}{each_ini} does not exist, so it cannot be backed up. This is typically caused by a path not being set correctly.", True)
                    copyfile(APP_LOG_FILE, f"{the_backup_directory}log.log")
                    this_ini_object.save_ini_file(1)
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
        for each_ini in open_inis:
            if each_ini == my_app_config:
                continue
            elif APP.inis(each_ini):
                location_list = list(open_inis[each_ini]['located'].keys())
                for n in range(len(location_list)):
                    this_ini_object = open_inis[each_ini]['located'][str(n+1)].get('object')

                    sections = this_ini_object.get_sections()

                    for section in sections:
                        settings = this_ini_object.get_settings(section)
                        if settings == []:
                            this_ini_object.remove_section(section)
                            self.sme(f'{section} was removed because it was empty.')
                        else:
                            for each_setting in settings:
                                if ';' in each_setting or '#' in each_setting:
                                    self.sme(f'{each_setting}:{section} will be preserved, as it is a comment.')
                                elif not APP.does_setting_exist(each_ini, section, each_setting):
                                    #sm(this_ini_object.remove_setting(section, each_setting))
                                    #Disabling the removal of unknown settings.
                                    self.sme(f'{each_setting}:{section} {each_ini} appears to be invalid.')
                                    if this_ini_object.get_settings(section) == []:
                                        this_ini_object.remove_section(section)
                                        self.sme(f'{section} was removed because it was empty.')

    def apply_ini_dict(self, ini_dict, only_if_missing=False):
        for each_setting in ini_dict:
            target_setting = each_setting.split(':')[0]
            if target_setting in APP.bethini['presetsIgnoreTheseSettings'] and not only_if_missing:
                continue
            target_ini = ini_dict[each_setting]['ini']
            target_section = ini_dict[each_setting]['section']
            this_value = str(ini_dict[each_setting]['value'])

            ini_location = APP.inis(target_ini)
            if ini_location != '':
                ini_location = app_config.get_value('Directories', ini_location)
            the_target_ini = open_ini(str(ini_location), str(target_ini))

            # Check if we are only supposed to add the value if the value is missing
            if only_if_missing and (the_target_ini.get_value(target_section, target_setting, "Not Present") != "Not Present"):
                continue
            the_target_ini.assign_setting_value(target_section, target_setting, this_value)
            self.sme(target_ini + " [" + target_section + "] " + target_setting + "=" + this_value)

    def remove_ini_dict(self, ini_dict):
        for each_setting in ini_dict:
            target_setting = each_setting.split(':')[0]
            target_ini = ini_dict[each_setting]['ini']
            target_section = ini_dict[each_setting]['section']
            this_value = str(ini_dict[each_setting]['value'])

            ini_location = APP.inis(target_ini)
            if ini_location != '':
                ini_location = app_config.get_value('Directories', ini_location)
            the_target_ini = open_ini(str(ini_location), str(target_ini))

            current_value = the_target_ini.get_value(target_section, target_setting, this_value)

            if current_value == this_value:
                remove_setting = the_target_ini.remove_setting(target_section, target_setting)
                if remove_setting == f"No section: {target_section}":
                    self.sme(f"No section {target_section} exists for {target_setting} in {the_target_ini}.")
                else:
                    self.sme(f"{target_ini} [{target_section}] {target_setting}={this_value}, which is the default value, and since it is not set to alwaysPrint, it will be removed")

    def create_tab_image(self, each_tab):
        try:
            self.tab_dictionary[each_tab]["TkPhotoImageForTab"] = tk.PhotoImage(file = os.path.join("icons", f"{self.tab_dictionary[each_tab]['Name']}.png"), height=16, width=16)
        except tk.TclError as e:
            self.sme(f'No image for tab "{each_tab}": {e}', exception=1)
            try:
                self.tab_dictionary[each_tab]["TkPhotoImageForTab"] = tk.PhotoImage(file = os.path.join("icons", "Blank.png"))
            except tk.TclError as e:
                self.sme(f'Failed to load blank icon at {os.path.join(current_working_directory, "icons", "Blank.png")}\n\n{e}', exception=1)
                self.tab_dictionary[each_tab]["TkPhotoImageForTab"] = tk.PhotoImage(data=Icon.warning)

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

            pack_settings = APP.pack_settings(self.tab_dictionary[each_tab]["Name"], label_frame)
            the_dict["LabelFrames"][the_label_frame]["TkLabelFrame"].pack(anchor=tkinter_switch_dict[pack_settings.get('Anchor','NW')],
                                                                          side=tkinter_switch_dict[pack_settings.get('Side','Top')],
                                                                          fill=tkinter_switch_dict[pack_settings.get('Fill','Both')],
                                                                          expand=pack_settings.get('Expand', 1),
                                                                          padx=10, pady=10)
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
        if setting_type not in types_without_label:
            if setting_type:
                setting_label = each_setting
            else:
                setting_label = ''
            setting_label_width = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("customWidth")
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkLabel"] = ttk.Label(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                                   text=setting_label, width=setting_label_width, anchor=tk.E)
            if setting_type in types_packed_left:
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkLabel"].pack(anchor=tk.CENTER, side=tk.LEFT, padx=5, pady=5)
            else:
                self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkLabel"].pack(anchor=tk.CENTER, padx=5, pady=5)
        setting_description = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("Description")
        if setting_description:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkDescriptionLabel"] = ttk.Label(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                                              text=setting_description, justify="left", wraplength=900)
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
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor='w', padx=5, pady=7)
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
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=0)
        self.tooltip(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)
        self.add_to_setting_dictionary(each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting, id_)

    def radio_preset(self, each_tab, label_frame, the_label_frame, on_frame, each_setting, the_setting):
        #creates the radio preset button
        id_ = 'TkRadioPreset'
        value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get('value')
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Radiobutton(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                              text=each_setting,
                                                                                                                              variable=self.preset_var, value=value)
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_].pack(anchor=tk.CENTER, padx=5, pady=7)
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
                                                                                                                        width=entry_width, validate='key',
                                                                                                                        validatecommand=(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        else:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Entry(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        width=entry_width,
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
        decimal_places = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("decimal places")
        length_value = self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting].get("length")

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"] = tk.StringVar(self)

        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = Scalar(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        from_=from_value, to=to_value, orient=tk.HORIZONTAL,
                                                                                                                        length=length_value, decimal_places=decimal_places,
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
                                                                                                                        width=width, validate='key', increment=increment_value, from_=from_value, to=to_value,
                                                                                                                        validatecommand=(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        else:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["second_tk_widget"] = ttk.Spinbox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        width=width, increment=increment_value, from_=from_value, to=to_value,
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
                                                                                                                        from_=from_value, to=to_value, increment=increment, width=width, validate='key',
                                                                                                                        validatecommand=(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["validate"],'%P','%s',validate),
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"])
        else:
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = ttk.Spinbox(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        from_=from_value, to=to_value, increment=increment, width=width,
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
        elif color_value_type == 'rgba':
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"].set('(255, 255, 255, 255)')
        elif color_value_type == 'rgb 1':
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"].set('(1.0000, 1.0000, 1.0000)')
        elif color_value_type == 'decimal':
            self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"].set('16777215')
        self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting][id_] = tk.Button(self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["TkFinalSettingFrame"],
                                                                                                                        textvariable=self.tab_dictionary[each_tab]["LabelFrames"][the_label_frame]["SettingFrames"][on_frame][the_setting]["tk_var"],
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
                logger.debug(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                logger.warning(f'No value set for checkbox {each_setting}.')

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
            logger.debug(f"{each_setting} = {this_value}")
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
            logger.debug(f"{each_setting} = {this_value}")
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
                logger.debug(f"{each_setting} = {this_value}")
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                logger.warning(f'No value set for entry {each_setting}.')

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
                logger.debug(f'{each_setting} = {this_value}')
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                logger.warning(f'no value set for slider {each_setting}')

    def spinbox_value(self, each_setting):
        setting_value = self.get_setting_values(self.setting_dictionary[each_setting].get('targetINIs'),
                                             self.setting_dictionary[each_setting].get('targetSections'),
                                             self.setting_dictionary[each_setting].get('settings'))
        if setting_value != [] and 'Does Not Exist' not in setting_value:
            this_value = setting_value[0]
            try:
                self.setting_dictionary[each_setting]['tk_var'].set(this_value)
                logger.debug(f'{each_setting} = {this_value}')
                self.setting_dictionary[each_setting]['valueSet'] = True
                return this_value
            except:
                logger.warning(f'no value set for spinbox {each_setting}')

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
            elif color_value_type == 'rgba':
                rgb_type = self.setting_dictionary[each_setting].get("rgbType")
                if rgb_type == 'multiple settings':
                    this_value = tuple(int(i) for i in setting_value)
                    new_color = rgb_to_hex(this_value[0:3])
                    this_value = str(this_value)
                else:
                    this_value = '('
                    for n in range(len(setting_value)):
                        this_value += setting_value[n]
                    this_value += ')'
                    print(this_value)
                    new_color = rgb_to_hex(ast.literal_eval(this_value)[0:3])
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
            logger.debug(f"{each_setting} = {this_value}")
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
                the_target_ini = open_ini(str(ini_location), str(targetINIs[n]))
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
                            try:
                                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                                self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}")
                            except AttributeError:
                                self.sme(f"Failed to assign {targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue} because the {targetINIs[n]} has an issue.", True)

                        the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                    else:
                        the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value[n])
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value[n])

    def dropdown_assign_value(self, each_setting):
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
                the_target_ini = open_ini(str(ini_location), str(targetINIs[n]))
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
                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                self.sme(f'{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={theValue}')

    def combobox_assign_value(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            decimal_places = self.setting_dictionary[each_setting].get('decimal places')
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(str(ini_location), str(targetINIs[n]))

                if decimal_places and this_value != '':
                    this_value = round(float(this_value),int(decimal_places))
                    if decimal_places == "0":
                        this_value = int(this_value)
                    this_value = str(this_value)

                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def entry_assign_value(self, each_setting):
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
                the_target_ini = open_ini(str(ini_location), str(targetINIs[n]))

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
                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def slider_assign_value(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(str(ini_location), str(targetINIs[n]))

                try:
                    the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                    self.sme(f"{targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value}")
                except AttributeError as e:
                    self.sme(f"Failed to set {targetINIs[n]} [{targetSections[n]}] {theSettings[n]}={this_value} because the {targetINIs[n]} has an issue.", True)

    def spinbox_assign_value(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(str(ini_location), str(targetINIs[n]))

                the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def color_assign_value(self, each_setting):
        targetINIs = self.setting_dictionary[each_setting].get('targetINIs')

        if targetINIs:
            tk_var = self.setting_dictionary[each_setting].get('tk_var')
            this_value = tk_var.get()

            targetSections = self.setting_dictionary[each_setting].get('targetSections')
            theSettings = self.setting_dictionary[each_setting].get('settings')

            color_value_type = self.setting_dictionary[each_setting].get("colorValueType")
            for n in range(len(targetINIs)):
                ini_location = self.getINILocation(targetINIs[n])
                the_target_ini = open_ini(str(ini_location), str(targetINIs[n]))

                if color_value_type == 'hex':
                    the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                    self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)
                elif color_value_type == 'decimal':
                    the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                    self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)
                elif color_value_type == 'rgb' or color_value_type == 'rgb 1' or color_value_type == 'rgba':
                    if len(theSettings) > 1:
                        theValue = str(ast.literal_eval(this_value)[n])
                        the_target_ini.assign_setting_value(targetSections[n], theSettings[n], theValue)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + theValue)
                    else:
                        this_value = this_value.lstrip('(').rstrip(')')
                        the_target_ini.assign_setting_value(targetSections[n], theSettings[n], this_value)
                        self.sme(targetINIs[n] + " [" + targetSections[n] + "] " + theSettings[n] + "=" + this_value)

    def createTabs(self, fromChooseGameWindow=False):

        # Preview Window
        global PREVIEW_WINDOW
        PREVIEW_WINDOW = ttk.Toplevel(self)
        PREVIEW_WINDOW.title('Preview')
        global PREVIEW_FRAME
        PREVIEW_FRAME = ttk.Frame(PREVIEW_WINDOW)
        PREVIEW_FRAME.pack(padx=5, pady=5)
        preview_close_button = ttk.Button(PREVIEW_WINDOW, text="Close", command=PREVIEW_WINDOW.withdraw)
        preview_close_button.pack(anchor=tk.SE, padx=5, pady=5)
        PREVIEW_WINDOW.protocol("WM_DELETE_WINDOW", PREVIEW_WINDOW.withdraw)
        PREVIEW_WINDOW.withdraw()

        for each_tab in self.tab_dictionary:
            #each_tab is Page1, Page2, etc.
            #self.tab_dictionary[each_tab]["Name"] is the name of each tab

            self.create_tab_image(each_tab)
            if self.tab_dictionary[each_tab]['Name'] == 'Setup':
                global SETUP_WINDOW
                self.tab_dictionary[each_tab]['SetupWindow'] = ttk.Toplevel(self)
                SETUP_WINDOW = self.tab_dictionary[each_tab]['SetupWindow']
                SETUP_WINDOW.title('Setup')
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(SETUP_WINDOW)
                self.tab_dictionary[each_tab]["TkFrameForTab"].pack()

                setup_ok_button = ttk.Button(SETUP_WINDOW, text="OK", command=self.withdraw_setup)
                setup_ok_button.pack(anchor=tk.SE, padx=5, pady=5)

                SETUP_WINDOW.protocol("WM_DELETE_WINDOW", self.withdraw_setup)
                if not fromChooseGameWindow:
                    SETUP_WINDOW.withdraw()
            elif self.tab_dictionary[each_tab]['Name'] == 'Preferences':
                global preferencesWindow
                self.tab_dictionary[each_tab]['PreferencesWindow'] = ttk.Toplevel(self)
                preferencesWindow = self.tab_dictionary[each_tab]['PreferencesWindow']
                preferencesWindow.title('Preferences')
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(preferencesWindow)
                self.tab_dictionary[each_tab]["TkFrameForTab"].pack()

                preferences_ok_button = ttk.Button(preferencesWindow, text="OK", command=preferencesWindow.withdraw)
                preferences_ok_button.pack(anchor=tk.SE, padx=5, pady=5)
                preferencesWindow.minsize(300, 100)

                preferencesWindow.protocol("WM_DELETE_WINDOW", preferencesWindow.withdraw)
                preferencesWindow.withdraw()

            else:
                self.tab_dictionary[each_tab]["TkFrameForTab"] = ttk.Frame(self.sub_container)
                self.sub_container.add(self.tab_dictionary[each_tab]["TkFrameForTab"], text=self.tab_dictionary[each_tab]["Name"], image=self.tab_dictionary[each_tab]["TkPhotoImageForTab"], compound=tk.LEFT)


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
                the_operator = operator_dictionary[the_operator]
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
                    'theOperator': operator_dictionary[self.dependent_settings_dictionary[each_setting][masterSetting].get('operator')],
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
                    if INI == my_app_config:
                        defaultValue = "Does Not Exist"
                    else:
                        defaultValue = APP.get_value(currentSetting, "default")

                    #target_ini = ModifyINI(str(ini_location) + str(INI))

                    target_ini = open_ini(str(ini_location), str(INI))
                    try:
                        value = str(target_ini.get_value(currentSection, currentSetting, default=defaultValue))
                    except AttributeError:
                        self.sme(f"There was a problem with the existing {target_ini} [{currentSection}] {currentSetting}, so {defaultValue} will be used.", True)
                        value = defaultValue
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

def on_closing(root):
    """Initialized upon closing the app. Asks if the user wants to save INI files if any INI files have been modified before quitting."""
    if messagebox.askyesno("Quit?", "Do you want to quit?"):
        if app_config.has_been_modified:
            app_config.save_ini_file(1)
        root.save_ini_files()
        root.quit()

def remove_excess_directory_files(directory, max_to_keep, files_to_remove):
    """Removes excess logs/backups.
    directory: the directory to remove files from
    max_to_keep: the maximum amount of directories that will be excluded from removal
    files_to_remove: list of files that will be removed
    """
    try:
        subdirectories = os.listdir(directory)
    except OSError as e:
        logger.debug(f"Info: {directory} : {e.strerror}")
        return True
    subdirectories.sort()
    if 'First-Time-Backup' in subdirectories:
        subdirectories.remove('First-Time-Backup')
    if max_to_keep > -1:
        for n in range(len(subdirectories)):
            if n < max_to_keep:
                logger.debug(subdirectories[n] + ' will be kept.')
            else:
                dir_path = os.path.join(directory, subdirectories[n])
                try:
                    for file in files_to_remove:
                        try:
                            os.remove(os.path.join(dir_path, file))
                        except OSError as e:
                            logger.error(f"{os.path.join(dir_path, file)}: {e.strerror}")
                    os.rmdir(dir_path)
                    logger.debug(subdirectories[n] + ' was removed.')
                except OSError as e:
                    logger.error(f"{dir_path} : {e.strerror}")
    return False

def open_ini(location, ini):
    """Given the location and name of an INI file, opens the INI object and stores it in open_inis."""
    open_ini = open_inis.get(ini)
    if open_ini:
        open_ini_location = open_inis[ini]['located']
        open_ini_id = 0
        for each_location in open_ini_location:
            open_ini_id += 1
            if open_ini_location[each_location]['at'] == location:
                return open_ini_location[each_location].get('object')
        #if the location is not found, add it
        open_ini_id += 1
        open_ini_id = str(open_ini_id)
        open_inis[ini]['located'][open_ini_id] = {
            'at':location
            }
        open_inis[ini]['located'][open_ini_id]['object'] = ModifyINI(location + ini)
        return open_inis[ini]['located'][open_ini_id]['object']
    #if the ini has not been opened before
    open_ini_id = "1"
    open_inis[ini] = {
        'located': {
            open_ini_id: {
                'at': location
                }
            }
        }
    try:
        open_inis[ini]['located'][open_ini_id]['object'] = ModifyINI(location + ini)
        #open_inis[ini]['located'][open_ini_id]['original'] = ModifyINI(location + ini)
    except configparser.MissingSectionHeaderError as e:
        logger.error(f"{e.strerror}")
    return open_inis[ini]['located'][open_ini_id]['object']

if __name__ == '__main__':

    #Get app config settings.
    my_app_config = f'{my_app_short_name}.ini'
    app_config = ModifyINI(my_app_config)
    iMaxLogs = app_config.get_value('General', 'iMaxLogs', '5')
    app_config.assign_setting_value('General', 'iMaxLogs', iMaxLogs)
    app_config.assign_setting_value('General', 'iMaxBackups', app_config.get_value('General', 'iMaxBackups', '5'))

    #theme
    theme = app_config.get_value('General', 'sTheme', default='superhero')
    if theme not in standThemes.STANDARD_THEMES.keys():
        theme='superhero'
    app_config.assign_setting_value('General', 'sTheme', theme)

    #Remove excess log files.
    remove_excess_directory_files(os.path.join(current_working_directory, 'logs'), int(iMaxLogs), ['log.log'])

    #Initialize open_inis dictionary to store list of opened INI files in.
    open_inis = {
        my_app_config: {
            'located': {
                '1': {
                    'at': '',
                    'object': app_config
                }
            }
        }
    }

    #Get version
    try:
        changelog = open('changelog.txt', 'r')
        version = changelog.readline().replace('\n','')
    except FileNotFoundError:
        version = ''

    #Start the app class

    window = bethini_app(themename=theme, iconphoto=os.path.join('Icons', 'Icon.png'))
    window.choose_game()
    window.minsize(400,200)


    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.mainloop()
