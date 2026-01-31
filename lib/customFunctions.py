#
# This work is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/
# or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#

import ctypes.wintypes
import logging
import os
import sys
import re
from pathlib import Path
from tkinter import filedialog, simpledialog

if os.name == "nt":
    import winreg
    from ctypes import windll, byref, c_int, sizeof

if __name__ == "__main__":
    sys.exit(1)

from lib.app import AppName
from lib.ModifyINI import ModifyINI
from lib.type_helpers import *

logger = logging.getLogger(__name__)


def set_titlebar_style(window: tk.Misc) -> None:
    """
    Set the title bar style for a given window to use dark mode and Mica effect on Windows 11.

    Args:
        window (tk.Misc): The window to apply the title bar style to.
    """
    # Check if the windowing system is win32 (Windows) and the build version is 22000 or higher (Windows 11)
    winsys = window.style.tk.call("tk", "windowingsystem")
    if winsys == "win32" and sys.getwindowsversion().build >= 22000:
        window.update()  # Ensure the window is updated to get the correct window handle
        hwnd = windll.user32.GetParent(
            window.winfo_id())  # Get the window handle

        # Constants for setting the dark mode and Mica effect
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_MICA_EFFECT = 1029

        # Enable dark mode for the title bar
        dark_mode = c_int(1)
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(dark_mode), sizeof(dark_mode))

        # Enable Mica effect for the title bar
        mica_effect = c_int(1)
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_MICA_EFFECT, byref(mica_effect), sizeof(mica_effect))


def set_theme(style_object: ttk.Style, theme_name: str) -> None:
    """Set the application theme."""

    style_object.theme_use(theme_name)
    style_object.configure("choose_game_button.TButton", font=("Segoe UI", 14))
    ModifyINI.app_config().assign_setting_value("General", "sTheme", theme_name)


def sanitize_and_convert_float(value: str) -> str:
    """
    Sanitize a string to ensure it can be converted to a valid float and handle exponential notation.

    This function takes a string input, removes any invalid characters, and converts exponential notation
    to its decimal equivalent. If the input contains invalid characters, the function shortens the string
    to the valid part before the invalid characters start. If the conversion to float fails, the function
    defaults the value to "0".

    Args:
        value (str): The input string to be sanitized and converted.

    Returns:
        str: A sanitized string that can be safely converted to a float.
    """
    # New code to handle invalid characters and exponentials
    match = re.match(r"^[\d.eE+-]+", value)
    if match:
        value = match.group(0)
        try:
            # Convert exponential notation to decimal
            value = str(float(value))
        except ValueError:
            # If conversion fails, default to 0
            value = "0"
    else:
        value = "0"  # Default to 0 if no valid part is found
    return value


def trim_trailing_zeros(value: float) -> str:
    """
    Remove trailing zeros from a float and return it as a string.

    Args:
        value (float): The float value to be formatted.

    Returns:
        str: The formatted string without trailing zeros.
    """
    # Format as a fixed-point number first
    formatted = f"{value:f}"
    # If there is a decimal point, strip trailing zeros and the trailing decimal point if needed.
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted

def is_valid_hex(value: str) -> bool:
    """Check if a string is a valid hex value."""
    is_hex = False
    if (
        value.startswith("#")
        or value.lower().startswith("0x")
        or re.search(r"[A-Fa-f]", value)
    ):
        try:
            hex_str = value.lstrip("#")
            if hex_str.lower().startswith("0x"):
                hex_str = hex_str[2:]
            hex_str = str(int(hex_str, 16))
            is_hex = True
        except ValueError:
            is_hex = False
    return is_hex

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an RGB color value to a hex representation."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def rgba_to_hex(rgba: tuple[int, int, int, int]) -> str:
    """Convert an RGBA color value to a hex representation."""
    return "#{:02x}{:02x}{:02x}{:02x}".format(*rgba)


def rgba_to_decimal(rgba: tuple[int, int, int, int]) -> str:
    """Convert an RGBA color value to a decimal representation."""
    red, green, blue, alpha = rgba
    decimal_value = (red << 24) + (green << 16) + (blue << 8) + alpha
    return str(decimal_value)


def abgr_to_decimal(abgr: tuple[int, int, int, int]) -> str:
    """Convert an ABGR color value to a decimal representation."""
    alpha, blue, green, red = abgr
    decimal_value = (alpha << 24) + (blue << 16) + (green << 8) + red
    return str(decimal_value)


def hex_to_rgb(value: str) -> tuple[int, int, int] | tuple[int, ...]:
    """Convert a hex color value to an RGB color value."""
    value = value.lstrip("#")
    lv = len(value)
    if lv == 1:
        v = int(value, 16) * 17
        return v, v, v
    if lv == 3:
        return tuple(int(value[i: i + 1], 16) * 17 for i in range(3))
    return tuple(int(value[i: i + lv // 3], 16) for i in range(0, lv, lv // 3))


def hex_to_decimal(hex_: str) -> str:
    """Convert a hex color value to a decimal representation."""
    return str(int(hex_.lstrip("#"), 16))


def decimal_to_rgb(decimal_string: str) -> tuple[int, int, int]:
    """Convert a decimal representation to an RGB color value."""
    decimal = int(decimal_string)
    blue = decimal & 255
    green = (decimal >> 8) & 255
    red = (decimal >> 16) & 255
    return (red, green, blue)


def decimal_to_rgba(decimal_string: str) -> tuple[int, int, int, int]:
    """Convert a decimal representation to an RGBA color value."""
    decimal = int(decimal_string)
    alpha = decimal & 255
    blue = (decimal >> 8) & 255
    green = (decimal >> 16) & 255
    red = (decimal >> 24) & 255
    return (red, green, blue, alpha)


def decimal_to_abgr(decimal_string: str) -> tuple[int, int, int, int]:
    """Convert a decimal representation to an ABGR color value."""
    decimal = int(decimal_string)
    red = decimal & 255
    green = (decimal >> 8) & 255
    blue = (decimal >> 16) & 255
    alpha = (decimal >> 24) & 255
    return (alpha, blue, green, red)


def browse_to_location(choice: str, browse: Browse, function: str, game_name: str) -> str | None:
    """
    Handle browsing to a location or manual entry for a file or directory.

    Args:
        choice (str): The user's choice, either "Browse...", "Manual...", or a predefined option.
        browse (Browse): A tuple containing browse options.
        function (str): A custom function to call if provided.
        game_name (str): The name of the game for context in custom functions.

    Returns:
        str | None: The selected or entered location, or None if the operation was canceled.

    Note:
        This is NOT meant to replace typical queries for paths, but solely for advanced use of the dropdowns optionmenus.
    """
    if choice == "Browse...":
        # Handle directory selection
        if browse[2] == "directory":
            response = filedialog.askdirectory()
            if not response:
                return None

            location = Path(response).resolve()

        else:
            # Handle file selection
            response = filedialog.askopenfilename(
                filetypes=[(browse[1], browse[1])])
            if not response:
                return None

            location = Path(response).resolve()
            try:
                with location.open() as _fp:
                    pass

            except OSError as e:
                logger.exception(f"Failed to open file: {e}")
                return None
            # If a directory is expected but a file is selected, use the file's parent directory
            if browse[0] == "directory" and location.is_file():
                location = location.parent

        logger.debug(f"Location set to '{location}'")
        return str(location) + os.sep

    if choice == "Manual...":
        # Handle manual entry
        response = simpledialog.askstring(
            "  Manual Entry", "Custom Value:") or ""

        if response:
            logger.debug(f"Manually entered a value of '{response}'")
        return response or None

    if function:
        # Call a custom function if provided
        return_value_of_custom_function = getattr(
            CustomFunctions, function)(game_name, choice)
        logger.debug(
            f"Return value of {function}: {return_value_of_custom_function}")

    return choice


class Info:
    @staticmethod
    def get_game_config_directory(game_name: str) -> Path | None:
        """Find the game config directory as used for autodetection in dropdowns."""

        # Get existing saved location
        game_config_directory = ModifyINI.app_config().get_value(
            "Directories", f"s{game_name}INIPath")

        # If no saved location, use the Windows environment variable to find the location
        if game_config_directory is None and os.name == "nt":
            CSIDL_PERSONAL = 5  # My Documents
            SHGFP_TYPE_CURRENT = 0  # Get current, not default value

            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(
                None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

            documents_directory = Path(buf.value)
            logger.info(f"User documents location: {documents_directory}")

            game_config_directory = (
                documents_directory / "My Games" / Info.game_documents_name(game_name))

        if game_config_directory is not None:
            return Path(game_config_directory)
        else:
            return None

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

        game_documents_name = game_name_documents_location_dict.get(
            game_name, "")
        if game_documents_name:
            logger.debug(
                f"{game_name} Documents/My Games/ folder is {game_documents_name}.")
        else:
            logger.error(
                f"{game_name} not in the list of known Documents/My Games/ folders.")
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
            logger.error(
                f"{game_name} not in the list of known registry locations.")

        return game_reg


class CustomFunctions:
    # Placeholders to be set when bethini_app initializes
    screenwidth = 0
    screenheight = 0

    @staticmethod
    def getCurrentResolution(_game_name: str) -> str:
        # _game_name is required for CustomFunction calls
        resolutions_list = ["1280x720", "1366x768", "1440x900", "1600x900", "1680x1050", "1920x1200", "1920x1080", "2560x1080", "2560x1440", "2560x1600", "3440x1440", "3840x2160", "Manual..." ]
        current_resolution = f"{CustomFunctions.screenwidth}x{CustomFunctions.screenheight}"
        if current_resolution not in resolutions_list:
            resolutions_list.append(current_resolution)
        return resolutions_list

    @staticmethod
    def getBethesdaGameFolder(game_name: str) -> str | None:
        """Find the game install directory as used for autodetection in dropdowns for Bethesda games."""

        # Get existing saved location
        game_folder = ModifyINI.app_config().get_value(
            "Directories", f"s{game_name}Path")

        # If no saved location, check the registry
        if game_folder is None and "winreg" in globals():
            key_name = Info.game_reg(game_name)
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, Rf"SOFTWARE\WOW6432Node\Bethesda Softworks\{key_name}") as reg_handle:
                    value, value_type = winreg.QueryValueEx(
                        reg_handle, "Installed Path")

                if value and value_type == winreg.REG_SZ and isinstance(value, str):
                    game_folder = value

            except OSError:
                logger.exception(
                    f"Game path not found in the registry. Run the {game_name} launcher to set it.")

        if game_folder is None:
            game_folder = ""
        return game_folder

    @staticmethod
    def getGamePath(game_name: str) -> str:
        return ModifyINI.app_config().get_value("Directories", f"s{game_name}Path", "")

    @staticmethod
    def getINILocations(gameName: str) -> list[str]:
        game_documents_path = Info.get_game_config_directory(gameName)
        if game_documents_path is None:
            return ["", "Browse..."]
        game_documents_path.mkdir(parents=True, exist_ok=True)
        # This code throws errors if the file doesn't exist. What is its purpose? Commenting out for now.
        # app = AppName(gameName)
        # ini_files = app.what_ini_files_are_used()
        # for file in ini_files:
        #     if gameName == "Starfield" and file == "Ultra.ini":
        #         continue
        #     file_path = game_documents_path / file
        #     with file_path.open() as _fp:
        #         pass

        return [f"{game_documents_path}{os.sep}", "Browse..."]