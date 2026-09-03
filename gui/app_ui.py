# app_ui.py - Main application window, wiring all components together

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import os

from gui.themes import COLORS, FONTS
from gui.sidebar import Sidebar
from gui.image_panel import DualImagePanel
from gui.controls import ControlPanel
from utils.image_loader import load_image, save_image, cv2_to_photoimage, get_image_info
from utils.histogram_utils import (histogram_stretch, histogram_equalize,
                                   create_histogram_figure)

import processing.basic_ops as basic
import processing.filters as filt
import processing.advanced_ops as adv
import processing.morphology as morph
import processing.thresholding as thresh_mod
import processing.color_spaces as cs
import processing.effects as eff


class App(tk.Tk):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        self.title("Advanced Image Processing Studio")
        self.geometry("1360x820")
        self.minsize(1100, 650)
        self.configure(bg=COLORS["bg_main"])
        try:
            self.state("zoomed")  # maximize on Windows/Linux
        except Exception:
            pass

        # State
        self.original_image = None   # numpy BGR
        self.processed_image = None  # numpy BGR
        self.second_image   = None   # numpy BGR for multi-image ops
        self.image_path     = None
        self.current_filter = "None"

        self._build_ui()

    # ─── UI CONSTRUCTION ──────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_status_bar()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["bg_panel"], height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Left: title
        tk.Label(header, text="✦  Advanced Image Processing Studio",
                 font=("Segoe UI", 16, "bold"),
                 fg=COLORS["soft_gold"], bg=COLORS["bg_panel"]).pack(side="left", padx=20)

        # Right: status indicator
        right = tk.Frame(header, bg=COLORS["bg_panel"])
        right.pack(side="right", padx=16)

        self.status_dot = tk.Label(right, text="●", font=("Segoe UI", 10),
                                   fg="#666", bg=COLORS["bg_panel"])
        self.status_dot.pack(side="left")
        self.status_var = tk.StringVar(value="No image loaded")
        tk.Label(right, textvariable=self.status_var, font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"]).pack(side="left", padx=6)

    def _build_body(self):
        body = tk.Frame(self, bg=COLORS["bg_main"])
        body.pack(fill="both", expand=True)

        # Left sidebar
        self.sidebar = Sidebar(body, app=self)
        self.sidebar.pack(side="left", fill="y")

        tk.Frame(body, bg=COLORS["border"], width=1).pack(side="left", fill="y")

        # Right control panel
        self.controls = ControlPanel(body, app=self)
        self.controls.pack(side="right", fill="y")

        tk.Frame(body, bg=COLORS["border"], width=1).pack(side="right", fill="y")

        # Center: dual image panel + log
        center = tk.Frame(body, bg=COLORS["bg_main"])
        center.pack(side="left", fill="both", expand=True)

        self.dual_panel = DualImagePanel(center)
        self.dual_panel.pack(fill="both", expand=True, padx=6, pady=6)

        # Processing log
        log_frame = tk.Frame(center, bg=COLORS["bg_panel"], height=90)
        log_frame.pack(fill="x", padx=6, pady=(0, 6))
        log_frame.pack_propagate(False)

        tk.Label(log_frame, text="Processing Log", font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"]).pack(anchor="w", padx=8, pady=(4, 0))

        self.log_text = tk.Text(log_frame, height=4, font=FONTS["mono"],
                                bg=COLORS["bg_main"], fg=COLORS["text_secondary"],
                                relief="flat", state="disabled", padx=6)
        self.log_text.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=COLORS["bg_secondary"], height=24)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.progress_var = tk.DoubleVar(value=0)
        style = tk.ttk.Style() if False else None  # avoid import issue
        self.progress = tk.Canvas(bar, bg=COLORS["bg_secondary"], height=3, highlightthickness=0)
        self.progress.pack(side="bottom", fill="x")

        self.statusbar_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.statusbar_var, font=FONTS["small"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_secondary"]).pack(side="left", padx=10)

        tk.Label(bar, text="CS303 Image Processing Studio  |  Cairo University",
                 font=FONTS["small"], fg=COLORS["border"],
                 bg=COLORS["bg_secondary"]).pack(side="right", padx=10)

    # ─── HELPERS ──────────────────────────────────────────────────────

    def _log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"› {msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _set_status(self, msg, color=None):
        self.status_var.set(msg)
        self.statusbar_var.set(msg)
        self.status_dot.config(fg=color or COLORS["accent_teal"])

    def _show_processed(self, img, filter_name):
        """Store processed result and refresh the processed panel."""
        if img is None:
            return
        self.processed_image = img
        self.current_filter = filter_name
        photo = cv2_to_photoimage(img, max_size=(580, 520))
        h, w = img.shape[:2]
        self.dual_panel.processed.display(photo, info_text=f"{filter_name}  |  {w}×{h}")
        self.dual_panel.processed._current_photo = photo  # prevent GC
        self.sidebar.set_active_filter(filter_name)
        self._log(f"Applied: {filter_name} → output {w}×{h}")
        self._set_status(f"Filter applied: {filter_name}")

    def _require_image(self):
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return False
        return True

    def _require_second_image(self):
        if self.second_image is None:
            messagebox.showwarning("No Second Image", "Please upload a second image first.")
            return False
        return True

    # ─── FILE OPERATIONS ──────────────────────────────────────────────

    def upload_image(self):
        path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"), ("All", "*.*")]
        )
        if not path:
            return
        try:
            img = load_image(path)
            self.original_image = img
            self.processed_image = img.copy()
            self.image_path = path

            photo = cv2_to_photoimage(img, max_size=(580, 520))
            h, w = img.shape[:2]
            self.dual_panel.original.display(photo, info_text=f"Original  |  {w}×{h}")
            self.dual_panel.original._current_photo = photo

            info = get_image_info(path, img)
            self.sidebar.update_info(info)
            self.sidebar.set_active_filter("None")
            self._set_status(f"Loaded: {os.path.basename(path)}", COLORS["success"])
            self._log(f"Uploaded: {os.path.basename(path)}  ({w}×{h}, {img.dtype})")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def upload_second_image(self):
        path = filedialog.askopenfilename(
            title="Open Second Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"), ("All", "*.*")]
        )
        if not path:
            return
        try:
            self.second_image = load_image(path)
            self._log(f"Second image loaded: {os.path.basename(path)}")
            self._set_status(f"2nd image ready: {os.path.basename(path)}", COLORS["soft_gold"])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Nothing to Save", "No processed image to save.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if path:
            save_image(path, self.processed_image)
            self._log(f"Saved: {os.path.basename(path)}")
            self._set_status(f"Saved: {os.path.basename(path)}", COLORS["success"])

    def reset_image(self):
        if not self._require_image():
            return
        self.processed_image = self.original_image.copy()
        photo = cv2_to_photoimage(self.original_image, max_size=(580, 520))
        h, w = self.original_image.shape[:2]
        self.dual_panel.processed.display(photo, info_text=f"Reset  |  {w}×{h}")
        self.dual_panel.processed._current_photo = photo
        self.sidebar.set_active_filter("None")
        self._log("Image reset to original")
        self._set_status("Image reset")

    # ─── FILTER BINDINGS ──────────────────────────────────────────────
    # Each method checks for an image, applies the op, and calls _show_processed.

    def _apply(self, fn, name, *args, **kwargs):
        if not self._require_image():
            return
        src = self.processed_image if self.processed_image is not None else self.original_image
        try:
            result = fn(src, *args, **kwargs)
            self._show_processed(result, name)
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))
            self._log(f"ERROR in {name}: {e}")

    # Point Ops
    def apply_grayscale_avg(self):    self._apply(basic.grayscale_average, "Grayscale (Avg)")
    def apply_grayscale_weighted(self): self._apply(basic.grayscale_weighted, "Grayscale (Weighted)")
    def apply_negative(self):         self._apply(basic.negative, "Negative")
    def apply_solarize(self):         self._apply(basic.solarize, "Solarize")
    def apply_red(self):              self._apply(basic.red_channel, "Red Channel")
    def apply_green(self):            self._apply(basic.green_channel, "Green Channel")
    def apply_blue(self):             self._apply(basic.blue_channel, "Blue Channel")

    def apply_brightness_add(self):
        v = int(self.controls.brightness_val.get())
        self._apply(basic.brightness_add, f"Brightness +{v}", value=v)

    def apply_brightness_subtract(self):
        v = int(self.controls.brightness_val.get())
        self._apply(basic.brightness_subtract, f"Brightness −{v}", value=v)

    def apply_brightness_multiply(self):
        v = self.controls.brightness_val.get() / 50.0  # 0-255 → factor 0-5
        self._apply(basic.brightness_multiply, f"Brightness ×{v:.1f}", factor=max(v, 0.1))

    def apply_brightness_divide(self):
        v = self.controls.brightness_val.get() / 50.0
        self._apply(basic.brightness_divide, f"Brightness ÷{v:.1f}", factor=max(v, 0.1))

    # Histogram
    def show_histogram(self):
        if not self._require_image():
            return
        win = tk.Toplevel(self)
        win.title("Histogram")
        win.configure(bg=COLORS["bg_panel"])
        win.geometry("500x280")
        src = self.processed_image or self.original_image
        canvas_widget = create_histogram_figure(src, win)
        canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def apply_hist_stretch(self):  self._apply(histogram_stretch, "Hist. Stretching")
    def apply_hist_equalize(self): self._apply(histogram_equalize, "Hist. Equalization")

    # Neighbourhood filters
    def apply_mean(self):
        k = int(self.controls.kernel_slider.get())
        self._apply(filt.mean_filter, f"Mean Filter ({k}×{k})", kernel_size=k)

    def apply_median(self):
        k = int(self.controls.kernel_slider.get())
        self._apply(filt.median_filter, f"Median Filter ({k}×{k})", kernel_size=k)

    def apply_min(self):
        k = int(self.controls.kernel_slider.get())
        self._apply(filt.min_filter, f"Min Filter ({k}×{k})", kernel_size=k)

    def apply_max(self):
        k = int(self.controls.kernel_slider.get())
        self._apply(filt.max_filter, f"Max Filter ({k}×{k})", kernel_size=k)

    def apply_gaussian(self):
        k = int(self.controls.kernel_slider.get())
        self._apply(filt.gaussian_filter, f"Gaussian ({k}×{k})", kernel_size=k)

    # Sharpen
    def apply_laplacian(self): self._apply(filt.laplacian_sharpening, "Laplacian Sharpening")
    def apply_emboss(self):    self._apply(filt.emboss_filter, "Emboss")
    def apply_unsharp(self):   self._apply(filt.unsharp_masking, "Unsharp Masking")

    # Noise
    def apply_snp_noise(self):
        r = self.controls.noise_ratio.get()
        self._apply(adv.salt_pepper_noise, f"Salt & Pepper ({r:.2f})", noise_ratio=r)

    def apply_gauss_noise(self):
        s = self.controls.noise_sigma.get()
        self._apply(adv.gaussian_noise, f"Gaussian Noise (σ={s:.0f})", sigma=s)

    # Edge detection
    def apply_sobel(self):   self._apply(adv.sobel_edge, "Sobel Edge")
    def apply_prewitt(self): self._apply(adv.prewitt_edge, "Prewitt Edge")

    def apply_canny(self):
        lo = int(self.controls.canny_low.get())
        hi = int(self.controls.canny_high.get())
        self._apply(adv.canny_edge, f"Canny ({lo},{hi})", low=lo, high=hi)

    # Morphology
    def apply_erosion(self):
        k = int(self.controls.morph_size.get())
        self._apply(morph.erosion, f"Erosion ({k}×{k})", kernel_size=k)

    def apply_dilation(self):
        k = int(self.controls.morph_size.get())
        self._apply(morph.dilation, f"Dilation ({k}×{k})", kernel_size=k)

    def apply_opening(self):
        k = int(self.controls.morph_size.get())
        self._apply(morph.opening, f"Opening ({k}×{k})", kernel_size=k)

    def apply_closing(self):
        k = int(self.controls.morph_size.get())
        self._apply(morph.closing, f"Closing ({k}×{k})", kernel_size=k)

    # Thresholding
    def apply_manual_thresh(self):
        t = int(self.controls.thresh_val.get())
        self._apply(thresh_mod.manual_threshold, f"Manual Thresh (T={t})", threshold=t)

    def apply_otsu(self):     self._apply(thresh_mod.otsu_threshold, "Otsu Threshold")

    def apply_adaptive(self):
        b = int(self.controls.adapt_block.get())
        self._apply(thresh_mod.adaptive_threshold, f"Adaptive Thresh (B={b})", block_size=b)

    # Geometric
    def apply_rotate(self):
        a = self.controls.rotate_angle.get()
        self._apply(adv.rotate_image, f"Rotate {a:.0f}°", angle=a)

    def apply_flip_h(self): self._apply(adv.flip_horizontal, "Flip Horizontal")
    def apply_flip_v(self): self._apply(adv.flip_vertical, "Flip Vertical")

    def apply_zoom(self):
        z = self.controls.zoom_factor.get()
        self._apply(adv.zoom_image, f"Zoom ×{z:.1f}", factor=z)

    # Color space
    def apply_hsv(self):    self._apply(cs.to_hsv, "HSV Conversion")
    def apply_lab(self):    self._apply(cs.to_lab, "CIELAB Conversion")
    def apply_fourier(self): self._apply(cs.fourier_transform_vis, "Fourier Transform")

    # Effects
    def apply_gamma(self):
        g = self.controls.gamma_val.get()
        self._apply(eff.gamma_correction, f"Gamma (γ={g:.1f})", gamma=g)

    def apply_sepia(self):     self._apply(eff.sepia_tone, "Sepia Tone")
    def apply_posterize(self): self._apply(eff.posterize, "Posterize")

    def apply_vignette(self):
        s = self.controls.vignette_str.get()
        self._apply(eff.vignette, f"Vignette ({s:.2f})", strength=s)

    def apply_bilateral(self): self._apply(filt.bilateral_filter, "Bilateral Filter")
    def apply_sketch(self):    self._apply(eff.sketch_effect, "Sketch Effect")

    # Multi-image
    def apply_blend(self):
        if not self._require_image() or not self._require_second_image():
            return
        alpha = self.controls.blend_alpha.get()
        src = self.processed_image or self.original_image
        result = basic.blend_images(src, self.second_image, alpha=alpha)
        self._show_processed(result, f"Blend (α={alpha:.2f})")

    def apply_subtract(self):
        if not self._require_image() or not self._require_second_image():
            return
        src = self.processed_image or self.original_image
        result = basic.subtract_images(src, self.second_image)
        self._show_processed(result, "Image Subtraction")
