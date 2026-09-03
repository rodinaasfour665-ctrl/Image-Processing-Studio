# image_panel.py - Dual image display panels (Original | Processed)

import tkinter as tk
from gui.themes import COLORS, FONTS


class ImagePanel(tk.Frame):
    """A single image display panel with label and border."""

    def __init__(self, parent, title="Image", **kwargs):
        super().__init__(parent, bg=COLORS["bg_secondary"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1, **kwargs)
        self.title = title
        self._build()

    def _build(self):
        # Title bar
        title_bar = tk.Frame(self, bg=COLORS["bg_panel"], height=28)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        dot = tk.Label(title_bar, text="●", fg=COLORS["accent_teal"],
                       bg=COLORS["bg_panel"], font=FONTS["small"])
        dot.pack(side="left", padx=(8, 4), pady=4)

        tk.Label(title_bar, text=self.title, font=FONTS["label"],
                 fg=COLORS["soft_gold"], bg=COLORS["bg_panel"]).pack(side="left")

        # Image canvas
        self.canvas = tk.Canvas(self, bg=COLORS["bg_main"],
                                 highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)

        # Placeholder text
        self._placeholder_id = None
        self._show_placeholder()

        # Info label below
        self.info_var = tk.StringVar(value="No image loaded")
        tk.Label(self, textvariable=self.info_var, font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_secondary"]).pack(pady=(0, 4))

        # Track size for responsive display
        self.canvas.bind("<Configure>", self._on_resize)
        self._current_photo = None

    def _show_placeholder(self):
        if self._placeholder_id:
            self.canvas.delete(self._placeholder_id)
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width() or 300
        h = self.canvas.winfo_height() or 300
        self._placeholder_id = self.canvas.create_text(
            w // 2, h // 2,
            text=f"[ {self.title} ]\n\nUpload an image to begin",
            fill=COLORS["text_secondary"],
            font=FONTS["body"],
            justify="center"
        )

    def _on_resize(self, event):
        if self._current_photo is None:
            self.canvas.delete("all")
            self._placeholder_id = None
            self._show_placeholder()

    def display(self, photo_image, info_text=""):
        """Display a PhotoImage on the canvas."""
        self._current_photo = photo_image
        self.canvas.delete("all")
        self._placeholder_id = None
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width() or photo_image.width()
        h = self.canvas.winfo_height() or photo_image.height()
        self.canvas.create_image(w // 2, h // 2, anchor="center", image=photo_image)
        self.info_var.set(info_text)

    def clear(self):
        """Reset panel to placeholder state."""
        self._current_photo = None
        self.canvas.delete("all")
        self._placeholder_id = None
        self._show_placeholder()
        self.info_var.set("No image loaded")


class DualImagePanel(tk.Frame):
    """Container holding both Original and Processed image panels."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_main"], **kwargs)
        self._build()

    def _build(self):
        self.original = ImagePanel(self, title="Original Image")
        self.original.pack(side="left", fill="both", expand=True, padx=(0, 3), pady=0)

        divider = tk.Frame(self, bg=COLORS["border"], width=2)
        divider.pack(side="left", fill="y")

        self.processed = ImagePanel(self, title="Processed Image")
        self.processed.pack(side="left", fill="both", expand=True, padx=(3, 0), pady=0)
