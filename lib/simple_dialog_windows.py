import sys
import logging
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Icon

if __name__ == "__main__":
    sys.exit(1)

from lib.customFunctions import set_titlebar_style

logger = logging.getLogger(__name__)


class AskQuestionWindow(ttk.Toplevel):
    """AskQuestionWindow is a Toplevel window asking the user a yes/no question, with the button pressed being stored as the self.result."""
    def __init__(self, master, title: str, question: str, wraplength: int = 400, **kwargs):
        super().__init__(master, **kwargs)
        self.title(title)
        set_titlebar_style(self)
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.minsize(200, 35)
        self.result = None

        # Create the main frame for the dialog
        ask_question_frame = ttk.Frame(self)
        ask_question_frame.pack(fill=BOTH, expand=True)

        # Create a sub-frame for the content
        ask_question_frame_real = ttk.Frame(ask_question_frame)
        ask_question_frame_real.pack(anchor=CENTER, expand=True, pady=10)

        # Store the PhotoImage object as an instance variable to prevent garbage collection
        self.question_icon = ttk.PhotoImage(data=Icon.question)

        # Create and pack the icon label
        icon_lbl = ttk.Label(ask_question_frame_real, image=self.question_icon)
        icon_lbl.pack(side=LEFT, padx=5, anchor=CENTER)

        # Create and pack the question label
        ask_question_label = ttk.Label(
            ask_question_frame_real,
            text=question,
            justify=LEFT,
            wraplength=wraplength,
        )
        ask_question_label.pack(anchor=CENTER, padx=10, pady=10)
        logger.debug(f"User was asked: {question}")

        # Add a separator
        ttk.Separator(ask_question_frame).pack(fill=X)

        # Create and pack the "Yes" button
        yes_button = ttk.Button(
            ask_question_frame, text="Yes", style="success.TButton")
        yes_button.pack(side=RIGHT, padx=8, pady=8)
        yes_button.bind(
            "<Button-1>", lambda e: self.on_yes(e))

        # Create and pack the "No" button
        no_button = ttk.Button(
            ask_question_frame, text="No", style="danger.TButton")
        no_button.pack(side=RIGHT, pady=8)
        no_button.bind(
            "<Button-1>", lambda e: self.on_no(e))

    def on_no(self, event):
        """Handle the "No" button click event."""
        logger.debug("User clicked no.")
        self.result = False
        self.destroy()

    def on_yes(self, event):
        """Handle the "Yes" button click event."""
        logger.debug("User clicked yes.")
        self.result = True
        self.destroy()

class ManualEntryWindow(ttk.Toplevel):
    """ManualEntryWindow is a Toplevel window asking the user to input into a text box."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Manual Entry")
        set_titlebar_style(self)
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.minsize(300, 35)
        self.result = ttk.StringVar(self, value=None)

        # Create the main frame for the dialog
        manual_entry_frame = ttk.Frame(self)
        manual_entry_frame.pack(fill=BOTH, expand=True)

        # Create a sub-frame for the content
        manual_entry_frame_real = ttk.Frame(manual_entry_frame)
        manual_entry_frame_real.pack(anchor=CENTER, expand=True, pady=10)

        # Create and pack the question label
        manual_entry_label = ttk.Label(
            manual_entry_frame_real,
            text="Enter a custom value:",
            justify=CENTER,
        )
        manual_entry_label.pack(anchor=CENTER, padx=10, pady=10)

        # Create and pack the entry
        manual_entry = ttk.Entry(manual_entry_frame_real, textvariable=self.result)
        manual_entry.pack()

        # Add a separator
        ttk.Separator(manual_entry_frame).pack(fill=X)

        # Create and pack the "Yes" button
        ok_button = ttk.Button(
            manual_entry_frame, text="OK")
        ok_button.pack(side=RIGHT, padx=8, pady=8)
        ok_button.bind(
            "<Button-1>", lambda e: self.on_ok(e))

    def on_ok(self, event):
        """Handle the "OK" button click event."""
        logger.debug("User clicked OK.")
        self.destroy()