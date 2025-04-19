import json
import configparser
import re

print("Hello World")

with open('settings.json', 'r') as f:
    settings = json.load(f)

print("Settings loaded.")

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

def update_preset_value(setting: str, section: str, preset: str, value: str):
    for ini_setting in settings["iniValues"]:
        if ini_setting["name"].lower() == setting.lower() and ini_setting["section"].lower() == section.lower():
            default_value = ini_setting["value"]["default"]
            if ini_setting["type"] != "string":
                value = float(sanitize_and_convert_float(value))
                default_value = float(sanitize_and_convert_float(str(default_value)))
                if ini_setting["type"] != "float":
                    value = int(value)
                    default_value = int(default_value)
            # if default_value == value:
            #     break
            # try:
            #     if ini_setting["notes"] == "Unused":
            #         print(f"Setting {setting} in section {section} is unused, skipping.")
            #         break
            # except KeyError:
            #     print("No notes found for this setting.")
            # print(f"Default value for {setting} in section {section} is {default_value}.")
            ini_setting["value"][preset] = value
            ini_setting["alwaysPrint"] = True
            print(f"Updated {setting} in section {section} to {value} for preset {preset}.")
            break

with open('FalloutPrefs.ini', 'r') as f:
    config = configparser.ConfigParser()
    config.read_file(f)

for section in config.sections():
    print(f"Section: {section}")
    for setting, value in config.items(section):
        print(f"  {setting}: {value}")
        update_preset_value(setting, section, "Bethini Ultra", value)

with open('settings.json', 'w') as f:
    json.dump(settings, f, indent=4, ensure_ascii=False)