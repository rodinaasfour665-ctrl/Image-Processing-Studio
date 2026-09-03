# themes.py - Color palette and styling constants

COLORS = {
    "bg_main":       "#0f1f24",
    "bg_panel":      "#132a30",
    "bg_secondary":  "#18363d",
    "accent_teal":   "#2f7f7b",
    "accent_teal_hover": "#3a9e99",
    "soft_gold":     "#c7a96b",
    "text_primary":  "#f1f1f1",
    "text_secondary":"#b8c4c2",
    "border":        "#2a5a58",
    "success":       "#4caf50",
    "warning":       "#ff9800",
    "error":         "#f44336",
    "btn_bg":        "#1e4a4a",
    "btn_hover":     "#2f7f7b",
    "slider_bg":     "#1a3a3a",
}

FONTS = {
    "title":    ("Segoe UI", 18, "bold"),
    "subtitle": ("Segoe UI", 13, "bold"),
    "body":     ("Segoe UI", 11),
    "small":    ("Segoe UI", 9),
    "mono":     ("Courier New", 10),
    "label":    ("Segoe UI", 10, "bold"),
}

def apply_dark_theme(widget):
    """Recursively apply dark theme to tkinter widgets."""
    try:
        widget.configure(bg=COLORS["bg_main"], fg=COLORS["text_primary"])
    except Exception:
        pass
    for child in widget.winfo_children():
        apply_dark_theme(child)
