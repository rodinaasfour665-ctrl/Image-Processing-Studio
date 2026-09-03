# helpers.py - General utility helpers

import tkinter as tk
from gui.themes import COLORS, FONTS


def make_label(parent, text, font_key="body", color=None, **kwargs):
    color = color or COLORS["text_primary"]
    return tk.Label(parent, text=text, font=FONTS[font_key],
                    fg=color, bg=COLORS["bg_panel"], **kwargs)


def make_separator(parent, orient="horizontal"):
    f = tk.Frame(parent, bg=COLORS["border"],
                 height=1 if orient == "horizontal" else 0,
                 width=0 if orient == "horizontal" else 1)
    return f


def make_section_title(parent, text):
    lbl = tk.Label(parent, text=text, font=FONTS["subtitle"],
                   fg=COLORS["soft_gold"], bg=COLORS["bg_panel"],
                   anchor="w")
    return lbl


def tooltip(widget, text):
    """Simple tooltip on hover."""
    tip = None

    def on_enter(e):
        nonlocal tip
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        tip = tk.Toplevel(widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(tip, text=text, font=FONTS["small"],
                       bg=COLORS["bg_secondary"], fg=COLORS["text_primary"],
                       relief="flat", padx=6, pady=3,
                       bd=1, highlightbackground=COLORS["border"])
        lbl.pack()

    def on_leave(e):
        nonlocal tip
        if tip:
            tip.destroy()
            tip = None

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
