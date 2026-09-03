# sidebar.py - Left sidebar with file controls and image metadata

import tkinter as tk
from tkinter import filedialog, messagebox
from gui.themes import COLORS, FONTS


class SidebarButton(tk.Button):
    """Styled sidebar button with hover effects."""

    def __init__(self, parent, text, icon="", command=None, **kwargs):
        full_text = f"  {icon}  {text}" if icon else f"  {text}"
        super().__init__(
            parent,
            text=full_text,
            font=FONTS["body"],
            fg=COLORS["text_primary"],
            bg=COLORS["btn_bg"],
            activebackground=COLORS["accent_teal"],
            activeforeground=COLORS["text_primary"],
            relief="flat",
            bd=0,
            anchor="w",
            cursor="hand2",
            command=command,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.configure(bg=COLORS["btn_hover"]))
        self.bind("<Leave>", lambda e: self.configure(bg=COLORS["btn_bg"]))


class Sidebar(tk.Frame):
    """Left sidebar: upload, save, reset, and image info."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_panel"],
                         width=200, **kwargs)
        self.pack_propagate(False)
        self.app = app
        self._build()

    def _build(self):
        # Logo area
        logo_frame = tk.Frame(self, bg=COLORS["bg_panel"])
        logo_frame.pack(fill="x", pady=(16, 8), padx=10)
        tk.Label(logo_frame, text="⬡", font=("Segoe UI", 22),
                 fg=COLORS["accent_teal"], bg=COLORS["bg_panel"]).pack(side="left")
        tk.Label(logo_frame, text=" AIP\nStudio", font=("Segoe UI", 11, "bold"),
                 fg=COLORS["soft_gold"], bg=COLORS["bg_panel"], justify="left").pack(side="left")

        self._separator()

        # File buttons
        tk.Label(self, text="FILE OPERATIONS", font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w").pack(fill="x", padx=12, pady=(8, 2))

        self._btn("Upload Image", "📂", self.app.upload_image)
        self._btn("Upload 2nd Image", "📂", self.app.upload_second_image)
        self._btn("Save Processed", "💾", self.app.save_image)
        self._btn("Reset Image", "↺", self.app.reset_image)

        self._separator()

        # Image info section
        tk.Label(self, text="IMAGE INFO", font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w").pack(fill="x", padx=12, pady=(8, 4))

        self.info_frame = tk.Frame(self, bg=COLORS["bg_secondary"],
                                   highlightbackground=COLORS["border"],
                                   highlightthickness=1)
        self.info_frame.pack(fill="x", padx=8, pady=2)

        self.info_labels = {}
        for key in ["File", "Size", "Channels", "Type"]:
            row = tk.Frame(self.info_frame, bg=COLORS["bg_secondary"])
            row.pack(fill="x", padx=6, pady=2)
            tk.Label(row, text=f"{key}:", font=FONTS["small"],
                     fg=COLORS["text_secondary"], bg=COLORS["bg_secondary"],
                     width=8, anchor="w").pack(side="left")
            var = tk.StringVar(value="—")
            self.info_labels[key] = var
            tk.Label(row, textvariable=var, font=FONTS["small"],
                     fg=COLORS["text_primary"], bg=COLORS["bg_secondary"],
                     anchor="w", wraplength=110).pack(side="left", fill="x", expand=True)

        self._separator()

        # Active filter display
        tk.Label(self, text="ACTIVE FILTER", font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w").pack(fill="x", padx=12, pady=(8, 2))

        self.filter_var = tk.StringVar(value="None")
        filter_box = tk.Frame(self, bg=COLORS["bg_secondary"],
                              highlightbackground=COLORS["accent_teal"],
                              highlightthickness=1)
        filter_box.pack(fill="x", padx=8, pady=2)
        tk.Label(filter_box, textvariable=self.filter_var, font=FONTS["label"],
                 fg=COLORS["accent_teal"], bg=COLORS["bg_secondary"],
                 anchor="w", padx=8, pady=6).pack(fill="x")

    def _btn(self, text, icon, cmd):
        b = SidebarButton(self, text=text, icon=icon, command=cmd)
        b.pack(fill="x", padx=8, pady=2, ipady=6)

    def _separator(self):
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=8, pady=6)

    def update_info(self, info_dict):
        """Update image metadata display."""
        mapping = {
            "File": info_dict.get("filename", "—"),
            "Size": info_dict.get("dimensions", "—"),
            "Channels": str(info_dict.get("channels", "—")),
            "Type": info_dict.get("dtype", "—"),
        }
        for key, val in mapping.items():
            if key in self.info_labels:
                self.info_labels[key].set(val)

    def set_active_filter(self, name):
        self.filter_var.set(name)
