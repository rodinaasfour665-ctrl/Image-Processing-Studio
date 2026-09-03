import tkinter as tk
from tkinter import ttk
from gui.themes import COLORS, FONTS


class CollapsibleSection(tk.Frame):
    """A section with a toggle header and collapsible body."""

    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, bg=COLORS["bg_panel"], **kwargs)
        self._expanded = True
        self._build_header(title)
        self.body = tk.Frame(self, bg=COLORS["bg_card"],
                             highlightbackground=COLORS["border_teal"],
                             highlightthickness=1)
        self.body.pack(fill="x", padx=4, pady=(0, 4))

    def _build_header(self, title):
        hdr = tk.Frame(self, bg=COLORS["bg_secondary"], cursor="hand2")
        hdr.pack(fill="x", padx=4, pady=(6, 0))
        self._arrow = tk.Label(hdr, text="▼", bg=COLORS["bg_secondary"],
                                fg=COLORS["accent_teal"], font=FONTS["small"])
        self._arrow.pack(side="left", padx=(6, 2), pady=4)
        tk.Label(hdr, text=title, bg=COLORS["bg_secondary"],
                 fg=COLORS["text_primary"], font=FONTS["section"],
                 pady=4).pack(side="left")
        hdr.bind("<Button-1>", self._toggle)
        self._arrow.bind("<Button-1>", self._toggle)

    def _toggle(self, event=None):
        if self._expanded:
            self.body.pack_forget()
            self._arrow.config(text="▶")
        else:
            self.body.pack(fill="x", padx=4, pady=(0, 4))
            self._arrow.config(text="▼")
        self._expanded = not self._expanded

    def add_button(self, text: str, command, full_width=True):
        btn = tk.Button(self.body, text=text, command=command,
                        bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                        activebackground=COLORS["accent_teal"],
                        activeforeground=COLORS["text_primary"],
                        relief="flat", borderwidth=0,
                        font=FONTS["small"], padx=8, pady=5,
                        anchor="w", cursor="hand2")
        if full_width:
            btn.pack(fill="x", padx=6, pady=2)
        else:
            btn.pack(side="left", padx=3, pady=2)
        btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["hover_teal"],
                                                  fg=COLORS["text_primary"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["bg_secondary"],
                                                  fg=COLORS["text_secondary"]))
        return btn

    def add_slider(self, label: str, from_: float, to: float, default: float,
                   resolution: float = 1, callback=None) -> tk.DoubleVar:
        row = tk.Frame(self.body, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=6, pady=(4, 0))
        tk.Label(row, text=label, bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], font=FONTS["small"],
                 anchor="w", width=14).pack(side="left")
        var = tk.DoubleVar(value=default)
        val_lbl = tk.Label(row, text=str(default), bg=COLORS["bg_card"],
                           fg=COLORS["accent_gold"], font=FONTS["small"], width=5)
        val_lbl.pack(side="right")
        slider = ttk.Scale(self.body, from_=from_, to=to, variable=var,
                           orient="horizontal")
        slider.pack(fill="x", padx=6, pady=(0, 4))

        def _on_change(*_):
            rounded = round(var.get(), 2)
            val_lbl.config(text=str(rounded))
            if callback:
                callback(rounded)

        var.trace_add("write", _on_change)
        return var

    def add_separator(self):
        tk.Frame(self.body, bg=COLORS["separator"], height=1).pack(fill="x",
                                                                     padx=6, pady=4)


class ControlPanel(tk.Frame):
    """Right scrollable control panel with all image processing categories."""

    def __init__(self, parent, apply_fn, **kwargs):
        super().__init__(parent, bg=COLORS["bg_panel"], **kwargs)
        self._apply = apply_fn
        self._build_scrollable()
        self._build_sections()

    def _build_scrollable(self):
        # Scrollable canvas container
        self._canvas = tk.Canvas(self, bg=COLORS["bg_panel"],
                                  highlightthickness=0, width=230)
        scrollbar = ttk.Scrollbar(self, orient="vertical",
                                   command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=COLORS["bg_panel"])
        self._window = self._canvas.create_window((0, 0), window=self._inner,
                                                    anchor="nw")
        self._inner.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._window, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _section(self, title: str) -> CollapsibleSection:
        sec = CollapsibleSection(self._inner, title)
        sec.pack(fill="x", pady=2)
        return sec

    # ─── Slider state ──────────────────────────────────────────────────
    def _build_sections(self):
        p = self._apply  # shorthand

        # ── Point Operations ────────────────────────────────────────────
        sec = self._section("1. Point Operations")
        sec.add_button("Grayscale Average",   lambda: p("grayscale_avg"))
        sec.add_button("Grayscale Weighted",  lambda: p("grayscale_weighted"))
        sec.add_separator()
        self._bright_add_val    = sec.add_slider("Add Value", 0, 255, 50)
        sec.add_button("Brightness Add",      lambda: p("bright_add"))
        self._bright_sub_val    = sec.add_slider("Sub Value", 0, 255, 50)
        sec.add_button("Brightness Subtract", lambda: p("bright_sub"))
        self._bright_mul_val    = sec.add_slider("Multiply ×", 0.1, 5.0, 1.5, 0.1)
        sec.add_button("Brightness Multiply", lambda: p("bright_mul"))
        self._bright_div_val    = sec.add_slider("Divide ÷", 0.1, 10.0, 2.0, 0.1)
        sec.add_button("Brightness Divide",   lambda: p("bright_div"))
        sec.add_separator()
        sec.add_button("Negative",            lambda: p("negative"))
        self._solar_thresh      = sec.add_slider("Threshold", 0, 255, 128)
        sec.add_button("Solarize",            lambda: p("solarize"))
        sec.add_separator()
        sec.add_button("Red Channel",         lambda: p("channel_red"))
        sec.add_button("Green Channel",       lambda: p("channel_green"))
        sec.add_button("Blue Channel",        lambda: p("channel_blue"))

        # ── Histogram ───────────────────────────────────────────────────
        sec = self._section("2. Histogram")
        sec.add_button("Show Histogram",         lambda: p("hist_show"))
        sec.add_button("Histogram Stretching",   lambda: p("hist_stretch"))
        sec.add_button("Histogram Equalization", lambda: p("hist_equalize"))

        # ── Neighbourhood Filters ───────────────────────────────────────
        sec = self._section("3. Neighbourhood Filters")
        self._ksize             = sec.add_slider("Kernel Size", 3, 21, 5, 2)
        sec.add_button("Mean Filter",   lambda: p("mean_filter"))
        sec.add_button("Median Filter", lambda: p("median_filter"))
        sec.add_button("Min Filter",    lambda: p("min_filter"))
        sec.add_button("Max Filter",    lambda: p("max_filter"))
        self._gauss_sigma       = sec.add_slider("Sigma", 0.5, 5.0, 1.0, 0.1)
        sec.add_button("Gaussian Filter", lambda: p("gaussian_filter"))

        # ── Sharpen & Convolve ──────────────────────────────────────────
        sec = self._section("4. Sharpen & Convolve")
        sec.add_button("Laplacian Sharpen", lambda: p("laplacian"))
        sec.add_button("Emboss Filter",     lambda: p("emboss"))
        self._unsharp_strength  = sec.add_slider("Strength", 0.1, 5.0, 1.5, 0.1)
        sec.add_button("Unsharp Masking",   lambda: p("unsharp"))

        # ── Noise ───────────────────────────────────────────────────────
        sec = self._section("5. Noise")
        self._noise_ratio       = sec.add_slider("Noise %", 0.01, 0.3, 0.05, 0.01)
        sec.add_button("Salt & Pepper Noise", lambda: p("noise_sp"))
        self._gauss_noise_sigma = sec.add_slider("Sigma", 1.0, 80.0, 25.0)
        sec.add_button("Gaussian Noise",      lambda: p("noise_gauss"))

        # ── Edge Detection ──────────────────────────────────────────────
        sec = self._section("6. Edge Detection")
        sec.add_button("Sobel",   lambda: p("edge_sobel"))
        sec.add_button("Prewitt", lambda: p("edge_prewitt"))
        self._canny_low         = sec.add_slider("Canny Low",  10, 200, 50)
        self._canny_high        = sec.add_slider("Canny High", 50, 400, 150)
        sec.add_button("Canny",   lambda: p("edge_canny"))

        # ── Morphological ───────────────────────────────────────────────
        sec = self._section("7. Morphological")
        self._morph_ksize       = sec.add_slider("Kernel Size", 3, 21, 5, 2)
        sec.add_button("Erosion",  lambda: p("morph_erode"))
        sec.add_button("Dilation", lambda: p("morph_dilate"))
        sec.add_button("Opening",  lambda: p("morph_open"))
        sec.add_button("Closing",  lambda: p("morph_close"))

        # ── Thresholding ────────────────────────────────────────────────
        sec = self._section("8. Thresholding")
        self._thresh_val        = sec.add_slider("Threshold", 0, 255, 127)
        sec.add_button("Manual Threshold",   lambda: p("thresh_manual"))
        sec.add_button("Otsu Threshold",     lambda: p("thresh_otsu"))
        self._adaptive_block    = sec.add_slider("Block Size", 3, 51, 11, 2)
        sec.add_button("Adaptive Threshold", lambda: p("thresh_adaptive"))

        # ── Geometric ───────────────────────────────────────────────────
        sec = self._section("9. Geometric")
        self._rotate_angle      = sec.add_slider("Angle °", -180, 180, 45)
        sec.add_button("Rotate",         lambda: p("geo_rotate"))
        sec.add_button("Flip Horizontal",lambda: p("geo_flip_h"))
        sec.add_button("Flip Vertical",  lambda: p("geo_flip_v"))
        self._zoom_factor       = sec.add_slider("Zoom ×", 0.1, 4.0, 1.5, 0.1)
        sec.add_button("Zoom",           lambda: p("geo_zoom"))

        # ── Color Space ─────────────────────────────────────────────────
        sec = self._section("10. Color Space")
        sec.add_button("HSV Conversion",   lambda: p("cs_hsv"))
        sec.add_button("CIELAB Conversion",lambda: p("cs_lab"))
        sec.add_button("Fourier Transform",lambda: p("cs_fft"))

        # ── Effects ─────────────────────────────────────────────────────
        sec = self._section("11. Effects")
        self._gamma_val         = sec.add_slider("Gamma", 0.1, 5.0, 1.0, 0.1)
        sec.add_button("Gamma Correction", lambda: p("fx_gamma"))
        sec.add_button("Sepia Tone",       lambda: p("fx_sepia"))
        self._posterize_lvl     = sec.add_slider("Levels", 2, 16, 4, 1)
        sec.add_button("Posterize",        lambda: p("fx_posterize"))
        self._vignette_strength = sec.add_slider("Strength", 0.1, 2.0, 0.7, 0.1)
        sec.add_button("Vignette",         lambda: p("fx_vignette"))
        sec.add_button("Bilateral Filter", lambda: p("fx_bilateral"))
        sec.add_button("Sketch Effect",    lambda: p("fx_sketch"))

        # ── Multi-Image ─────────────────────────────────────────────────
        sec = self._section("12. Multi-Image Ops")
        self._blend_alpha       = sec.add_slider("Alpha", 0.0, 1.0, 0.5, 0.05)
        sec.add_button("Blend Images",    lambda: p("multi_blend"))
        sec.add_button("Subtract Images", lambda: p("multi_subtract"))

    # ─── Parameter getters ─────────────────────────────────────────────
    @property
    def bright_add(self):     return int(self._bright_add_val.get())
    @property
    def bright_sub(self):     return int(self._bright_sub_val.get())
    @property
    def bright_mul(self):     return float(self._bright_mul_val.get())
    @property
    def bright_div(self):     return float(self._bright_div_val.get())
    @property
    def solarize_thresh(self):return int(self._solar_thresh.get())
    @property
    def kernel_size(self):    return int(self._ksize.get()) | 1
    @property
    def gauss_sigma(self):    return float(self._gauss_sigma.get())
    @property
    def unsharp_strength(self): return float(self._unsharp_strength.get())
    @property
    def noise_ratio(self):    return float(self._noise_ratio.get())
    @property
    def noise_sigma(self):    return float(self._gauss_noise_sigma.get())
    @property
    def canny_low(self):      return int(self._canny_low.get())
    @property
    def canny_high(self):     return int(self._canny_high.get())
    @property
    def morph_ksize(self):    return int(self._morph_ksize.get()) | 1
    @property
    def thresh_val(self):     return int(self._thresh_val.get())
    @property
    def adaptive_block(self): return int(self._adaptive_block.get()) | 1
    @property
    def rotate_angle(self):   return float(self._rotate_angle.get())
    @property
    def zoom_factor(self):    return float(self._zoom_factor.get())
    @property
    def gamma(self):          return float(self._gamma_val.get())
    @property
    def posterize_levels(self): return int(self._posterize_lvl.get())
    @property
    def vignette_strength(self): return float(self._vignette_strength.get())
    @property
    def blend_alpha(self):    return float(self._blend_alpha.get())