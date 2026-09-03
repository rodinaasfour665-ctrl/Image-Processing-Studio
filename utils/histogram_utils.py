# histogram_utils.py - Histogram computation and equalization

import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from gui.themes import COLORS


def compute_histogram(image):
    """Compute histogram for a grayscale image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    hist = np.zeros(256, dtype=int)
    for val in gray.flat:
        hist[val] += 1
    return hist


def histogram_stretch(image):
    """Stretch histogram to use full 0-255 range."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    I_min = int(gray.min())
    I_max = int(gray.max())
    if I_max == I_min:
        return image
    stretched = ((gray.astype(np.int32) - I_min) * 255 // (I_max - I_min)).astype(np.uint8)
    if len(image.shape) == 3:
        return cv2.cvtColor(stretched, cv2.COLOR_GRAY2BGR)
    return stretched


def histogram_equalize(image):
    """Histogram equalization for contrast enhancement."""
    if len(image.shape) == 3:
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    return cv2.equalizeHist(image)


def create_histogram_figure(image, parent_frame):
    """Create a matplotlib histogram embedded in a Tkinter frame."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

    fig, ax = plt.subplots(figsize=(4, 2.2), facecolor=COLORS["bg_panel"])
    ax.set_facecolor(COLORS["bg_secondary"])
    ax.hist(gray.ravel(), bins=256, range=(0, 256), color=COLORS["accent_teal"], alpha=0.85)
    ax.set_xlim(0, 255)
    ax.tick_params(colors=COLORS["text_secondary"], labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS["border"])
    ax.set_title("Histogram", color=COLORS["soft_gold"], fontsize=9)
    fig.tight_layout(pad=0.5)

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    plt.close(fig)
    return canvas
