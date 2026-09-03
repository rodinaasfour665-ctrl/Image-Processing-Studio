# controls.py - Right scrollable control panel with all filter categories

import tkinter as tk
from tkinter import ttk
from gui.themes import COLORS, FONTS


class CollapsibleSection(tk.Frame):
    """A collapsible section with a header button and content frame."""

    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, bg=COLORS["bg_panel"], **kwargs)
        self._collapsed = False
        self._build(title)

    def _build(self, title):
        # Header
        self.header = tk.Button(
            self, text=f"▼  {title}", font=FONTS["label"],
            fg=COLORS["soft_gold"], bg=COLORS["bg_secondary"],
            activebackground=COLORS["btn_hover"], activeforeground=COLORS["soft_gold"],
            relief="flat", anchor="w", cursor="hand2",
            command=self._toggle
        )
        self.header.pack(fill="x", pady=(4, 0))

        # Content frame
        self.content = tk.Frame(self, bg=COLORS["bg_panel"])
        self.content.pack(fill="x", padx=4, pady=(0, 4))

    def _toggle(self):
        self._collapsed = not self._collapsed
        if self._collapsed:
            self.content.pack_forget()
            self.header.config(text=self.header.cget("text").replace("▼", "▶"))
        else:
            self.content.pack(fill="x", padx=4, pady=(0, 4))
            self.header.config(text=self.header.cget("text").replace("▶", "▼"))


class FilterButton(tk.Button):
    """Small, styled filter activation button."""

    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(
            parent, text=text, font=FONTS["small"],
            fg=COLORS["text_primary"], bg=COLORS["btn_bg"],
            activebackground=COLORS["accent_teal"],
            activeforeground="#ffffff",
            relief="flat", bd=0, padx=6, pady=4,
            cursor="hand2", command=command, **kwargs
        )
        self.bind("<Enter>", lambda e: self.configure(bg=COLORS["btn_hover"]))
        self.bind("<Leave>", lambda e: self.configure(bg=COLORS["btn_bg"]))


class SliderControl(tk.Frame):
    """A labeled slider with current value display."""

    def __init__(self, parent, label, from_=0, to=255, default=128,
                 resolution=1, callback=None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_panel"], **kwargs)
        self.callback = callback

        row = tk.Frame(self, bg=COLORS["bg_panel"])
        row.pack(fill="x", pady=(2, 0))
        tk.Label(row, text=label, font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w").pack(side="left")
        self.val_label = tk.Label(row, text=str(default), font=FONTS["small"],
                                  fg=COLORS["accent_teal"], bg=COLORS["bg_panel"],
                                  width=5, anchor="e")
        self.val_label.pack(side="right")

        self.var = tk.DoubleVar(value=default)
        self.slider = tk.Scale(
            self, variable=self.var, from_=from_, to=to,
            orient="horizontal", resolution=resolution,
            bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
            troughcolor=COLORS["slider_bg"], highlightthickness=0,
            activebackground=COLORS["accent_teal"],
            sliderrelief="flat", showvalue=False,
            command=self._on_change
        )
        self.slider.pack(fill="x")

    def _on_change(self, val):
        v = float(val)
        self.val_label.config(text=f"{v:.1f}" if v != int(v) else str(int(v)))
        if self.callback:
            self.callback(v)

    def get(self):
        return self.var.get()


class ControlPanel(tk.Frame):
    """Right scrollable panel containing all filter controls."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_panel"], width=240, **kwargs)
        self.pack_propagate(False)
        self.app = app
        self._build()

    def _build(self):
        # Header
        tk.Label(self, text="FILTERS & CONTROLS", font=FONTS["label"],
                 fg=COLORS["soft_gold"], bg=COLORS["bg_panel"]).pack(pady=(10, 4))
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=6)

        # Scrollable canvas
        canvas = tk.Canvas(self, bg=COLORS["bg_panel"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(canvas, bg=COLORS["bg_panel"])
        self.window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(self.window_id, width=canvas.winfo_width())

        self.scroll_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(self.window_id, width=e.width))

        # Mouse wheel scrolling
        def on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        self._build_sections()

    def _build_sections(self):
        p = self.scroll_frame  # shorthand

        # ── 1. POINT OPERATIONS ──────────────────────────────────────
        sec = CollapsibleSection(p, "① Point Operations")
        sec.pack(fill="x", padx=4)
        c = sec.content
        ops = [
            ("Grayscale Avg", self.app.apply_grayscale_avg),
            ("Grayscale Weighted", self.app.apply_grayscale_weighted),
            ("Negative", self.app.apply_negative),
            ("Solarize", self.app.apply_solarize),
            ("Red Channel", self.app.apply_red),
            ("Green Channel", self.app.apply_green),
            ("Blue Channel", self.app.apply_blue),
        ]
        self._grid_buttons(c, ops)

        # Brightness sliders
        tk.Frame(c, bg=COLORS["border"], height=1).pack(fill="x", pady=4)
        tk.Label(c, text="Brightness Operations", font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"]).pack(anchor="w")

        self.brightness_val = SliderControl(c, "Value", 0, 255, 50)
        self.brightness_val.pack(fill="x")

        row = tk.Frame(c, bg=COLORS["bg_panel"])
        row.pack(fill="x", pady=2)
        for text, cmd in [("+ Add", self.app.apply_brightness_add),
                          ("− Sub", self.app.apply_brightness_subtract),
                          ("× Mul", self.app.apply_brightness_multiply),
                          ("÷ Div", self.app.apply_brightness_divide)]:
            FilterButton(row, text=text, command=cmd).pack(side="left", padx=2, pady=2, expand=True, fill="x")

        # ── 2. HISTOGRAM ──────────────────────────────────────────────
        sec2 = CollapsibleSection(p, "② Histogram")
        sec2.pack(fill="x", padx=4, pady=(4, 0))
        c2 = sec2.content
        ops2 = [
            ("Show Histogram", self.app.show_histogram),
            ("Hist Stretch", self.app.apply_hist_stretch),
            ("Hist Equalize", self.app.apply_hist_equalize),
        ]
        self._grid_buttons(c2, ops2)

        # ── 3. NEIGHBOURHOOD ──────────────────────────────────────────
        sec3 = CollapsibleSection(p, "③ Neighbourhood Filters")
        sec3.pack(fill="x", padx=4, pady=(4, 0))
        c3 = sec3.content
        self.kernel_slider = SliderControl(c3, "Kernel Size", 3, 21, 3, resolution=2)
        self.kernel_slider.pack(fill="x")
        ops3 = [
            ("Mean", self.app.apply_mean),
            ("Median", self.app.apply_median),
            ("Min", self.app.apply_min),
            ("Max", self.app.apply_max),
            ("Gaussian", self.app.apply_gaussian),
        ]
        self._grid_buttons(c3, ops3)

        # ── 4. SHARPEN & CONVOLVE ─────────────────────────────────────
        sec4 = CollapsibleSection(p, "④ Sharpen & Convolve")
        sec4.pack(fill="x", padx=4, pady=(4, 0))
        c4 = sec4.content
        ops4 = [
            ("Laplacian", self.app.apply_laplacian),
            ("Emboss", self.app.apply_emboss),
            ("Unsharp Mask", self.app.apply_unsharp),
        ]
        self._grid_buttons(c4, ops4)

        # ── 5. NOISE ──────────────────────────────────────────────────
        sec5 = CollapsibleSection(p, "⑤ Noise")
        sec5.pack(fill="x", padx=4, pady=(4, 0))
        c5 = sec5.content
        self.noise_ratio = SliderControl(c5, "Noise Ratio", 0.01, 0.5, 0.05, resolution=0.01)
        self.noise_ratio.pack(fill="x")
        self.noise_sigma = SliderControl(c5, "Gaussian σ", 1, 100, 25)
        self.noise_sigma.pack(fill="x")
        ops5 = [("Salt & Pepper", self.app.apply_snp_noise),
                ("Gaussian Noise", self.app.apply_gauss_noise)]
        self._grid_buttons(c5, ops5)

        # ── 6. EDGE DETECTION ─────────────────────────────────────────
        sec6 = CollapsibleSection(p, "⑥ Edge Detection")
        sec6.pack(fill="x", padx=4, pady=(4, 0))
        c6 = sec6.content
        self.canny_low  = SliderControl(c6, "Canny Low",  0, 255, 50)
        self.canny_low.pack(fill="x")
        self.canny_high = SliderControl(c6, "Canny High", 0, 255, 150)
        self.canny_high.pack(fill="x")
        ops6 = [("Sobel", self.app.apply_sobel),
                ("Prewitt", self.app.apply_prewitt),
                ("Canny", self.app.apply_canny)]
        self._grid_buttons(c6, ops6)

        # ── 7. MORPHOLOGY ─────────────────────────────────────────────
        sec7 = CollapsibleSection(p, "⑦ Morphological Ops")
        sec7.pack(fill="x", padx=4, pady=(4, 0))
        c7 = sec7.content
        self.morph_size = SliderControl(c7, "SE Size", 3, 21, 5, resolution=2)
        self.morph_size.pack(fill="x")
        ops7 = [("Erosion", self.app.apply_erosion),
                ("Dilation", self.app.apply_dilation),
                ("Opening", self.app.apply_opening),
                ("Closing", self.app.apply_closing)]
        self._grid_buttons(c7, ops7)

        # ── 8. THRESHOLDING ───────────────────────────────────────────
        sec8 = CollapsibleSection(p, "⑧ Thresholding")
        sec8.pack(fill="x", padx=4, pady=(4, 0))
        c8 = sec8.content
        self.thresh_val  = SliderControl(c8, "Threshold", 0, 255, 128)
        self.thresh_val.pack(fill="x")
        self.adapt_block = SliderControl(c8, "Adaptive Block", 3, 51, 11, resolution=2)
        self.adapt_block.pack(fill="x")
        ops8 = [("Manual Thresh", self.app.apply_manual_thresh),
                ("Otsu Thresh", self.app.apply_otsu),
                ("Adaptive", self.app.apply_adaptive)]
        self._grid_buttons(c8, ops8)

        # ── 9. GEOMETRIC ──────────────────────────────────────────────
        sec9 = CollapsibleSection(p, "⑨ Geometric Ops")
        sec9.pack(fill="x", padx=4, pady=(4, 0))
        c9 = sec9.content
        self.rotate_angle = SliderControl(c9, "Angle (°)", -180, 180, 45)
        self.rotate_angle.pack(fill="x")
        self.zoom_factor  = SliderControl(c9, "Zoom", 1.0, 5.0, 1.5, resolution=0.1)
        self.zoom_factor.pack(fill="x")
        ops9 = [("Rotate", self.app.apply_rotate),
                ("Flip H", self.app.apply_flip_h),
                ("Flip V", self.app.apply_flip_v),
                ("Zoom", self.app.apply_zoom)]
        self._grid_buttons(c9, ops9)

        # ── 10. COLOR SPACE ───────────────────────────────────────────
        sec10 = CollapsibleSection(p, "⑩ Color Space")
        sec10.pack(fill="x", padx=4, pady=(4, 0))
        c10 = sec10.content
        ops10 = [("HSV Conv.", self.app.apply_hsv),
                 ("CIELAB Conv.", self.app.apply_lab),
                 ("Fourier Vis.", self.app.apply_fourier)]
        self._grid_buttons(c10, ops10)

        # ── 11. EFFECTS ───────────────────────────────────────────────
        sec11 = CollapsibleSection(p, "⑪ Effects")
        sec11.pack(fill="x", padx=4, pady=(4, 0))
        c11 = sec11.content
        self.gamma_val = SliderControl(c11, "Gamma", 0.1, 5.0, 1.5, resolution=0.1)
        self.gamma_val.pack(fill="x")
        self.vignette_str = SliderControl(c11, "Vignette", 0.0, 0.95, 0.5, resolution=0.05)
        self.vignette_str.pack(fill="x")
        ops11 = [("Gamma", self.app.apply_gamma),
                 ("Sepia", self.app.apply_sepia),
                 ("Posterize", self.app.apply_posterize),
                 ("Vignette", self.app.apply_vignette),
                 ("Bilateral", self.app.apply_bilateral),
                 ("Sketch", self.app.apply_sketch)]
        self._grid_buttons(c11, ops11)

        # ── 12. MULTI-IMAGE ───────────────────────────────────────────
        sec12 = CollapsibleSection(p, "⑫ Multi-Image Ops")
        sec12.pack(fill="x", padx=4, pady=(4, 8))
        c12 = sec12.content
        self.blend_alpha = SliderControl(c12, "Blend α (img1)", 0.0, 1.0, 0.6, resolution=0.05)
        self.blend_alpha.pack(fill="x")
        ops12 = [("Blend Images", self.app.apply_blend),
                 ("Subtract Images", self.app.apply_subtract)]
        self._grid_buttons(c12, ops12)

    def _grid_buttons(self, parent, ops, cols=2):
        """Lay out buttons in a grid of `cols` columns."""
        row_frame = None
        for i, (text, cmd) in enumerate(ops):
            if i % cols == 0:
                row_frame = tk.Frame(parent, bg=COLORS["bg_panel"])
                row_frame.pack(fill="x", pady=1)
            FilterButton(row_frame, text=text, command=cmd).pack(
                side="left", padx=2, pady=2, expand=True, fill="x")
