import sys
import ttkbootstrap as ttk
import logging
from pathlib import Path
from ttkbootstrap.constants import *
from webbrowser import open_new_tab
from ttkbootstrap.themes.standard import STANDARD_THEMES

if __name__ == "__main__":
    sys.exit(1)

from lib.customFunctions import set_titlebar_style, set_theme

logger = logging.getLogger(__name__)


class ChooseGameWindow(ttk.Toplevel):
    def __init__(self, master, version: str, exedir: Path, **kwargs):
        super().__init__(master, **kwargs)
        self.title(f"Bethini Pie {version}")
        set_titlebar_style(self)
        self.grab_set()
        self.focus_set()
        self.lift()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.minsize(300, 35)
        self.master = master
        self.result = None
        x = master.winfo_x()
        y = master.winfo_y()
        self.geometry(f"+{x + 50}+{y + 50}")


        choose_game_frame = ttk.Frame(self)

        choose_game_frame_2 = ttk.Frame(choose_game_frame)

        label_Bethini = ttk.Label(
            choose_game_frame_2, text="Bethini Pie", font=("Segoe UI", 20))
        label_Pie = ttk.Label(
            choose_game_frame_2,
            text="Performance INI Editor\nby DoubleYou",
            font=("Segoe UI", 15),
            justify=CENTER,
            style=WARNING,
        )
        label_link = ttk.Label(
            choose_game_frame_2,
            text="www.nexusmods.com/site/mods/631",
            font=("Segoe UI", 10),
            cursor="hand2",
            style=INFO,
        )

        choose_game_label = ttk.Label(
            choose_game_frame_2, text="Choose Game", font=("Segoe UI", 15))

        self.choose_game_tree = ttk.Treeview(
            choose_game_frame_2, selectmode=BROWSE, show="tree", columns=("Name"))
        self.choose_game_tree.column("#0", width=0, stretch=NO)
        self.choose_game_tree.column("Name", anchor=W, width=300)

        self.master.style_override.configure(
            "choose_game_button.TButton", font=("Segoe UI", 14),
            background=STANDARD_THEMES[master.theme_name.get()]["colors"].get("inputbg"),
            foreground=STANDARD_THEMES[master.theme_name.get()]["colors"].get("inputfg"))
        choose_game_button = ttk.Button(
            choose_game_frame_2,
            text="Select Game",
            style="choose_game_button.TButton",
        )

        choose_game_button.bind(
            "<Button-1>", lambda e: self.on_choose_game(e))

        choose_game_tip = ttk.Label(
            choose_game_frame_2,
            text="Tip: You can change the game at any time\nby going to File > Choose Game.",
            font=("Segoe UI", 12),
            justify=CENTER,
            style="success",
        )
        for option in Path(exedir / "apps").iterdir():
            self.choose_game_tree.insert(
                "", index=END, id=option.name, text=option.name, values=[option.name])

        preferences_frame = ttk.Frame(choose_game_frame_2)

        theme_label = ttk.Label(preferences_frame, text="Theme:")
        theme_names = list(ttk.Style().theme_names())
        theme_mb = ttk.Menubutton(
            preferences_frame, textvariable=master.theme_name)
        theme_menu = ttk.Menu(theme_mb)
        for theme_name in theme_names:
            theme_menu.add_radiobutton(label=theme_name, variable=master.theme_name,
                                       value=theme_name, command=self.set_theme)
        theme_mb["menu"] = theme_menu

        choose_game_frame.pack(fill=BOTH, expand=True)
        choose_game_frame_2.pack(anchor=CENTER, expand=True)

        label_Bethini.pack(padx=5, pady=5)
        label_Pie.pack(padx=5, pady=15)
        label_link.pack(padx=25, pady=5)
        label_link.bind(
            "<Button-1>", lambda _event: open_new_tab("https://www.nexusmods.com/site/mods/631"))

        preferences_frame.pack()
        theme_label.pack(side=LEFT)
        theme_mb.pack(padx=5, pady=15)
        choose_game_label.pack(padx=5, pady=2)
        self.choose_game_tree.pack(padx=10)
        choose_game_button.pack(pady=15)
        choose_game_tip.pack(pady=10)

    def on_choose_game(self, _event) -> None:
        self.result = self.choose_game_tree.focus()
        logger.debug(f"User selected: {self.result}")
        self.destroy()

    def set_theme(self) -> None:
        set_theme(self.master.style_override, self.master.theme_name.get())
        self.master.style_override.configure(
            "choose_game_button.TButton", font=("Segoe UI", 14),
            background=STANDARD_THEMES[self.master.theme_name.get()]["colors"].get("inputbg"),
            foreground=STANDARD_THEMES[self.master.theme_name.get()]["colors"].get("inputfg"))