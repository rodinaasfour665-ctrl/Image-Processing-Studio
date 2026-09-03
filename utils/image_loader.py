# image_loader.py - Image loading and saving utilities

import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk


def load_image(path):
    """Load image from disk using OpenCV (BGR format)."""
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not load image: {path}")
    return img


def save_image(path, image):
    """Save image to disk."""
    cv2.imwrite(path, image)


def cv2_to_photoimage(image, max_size=(500, 400)):
    """Convert OpenCV BGR image to Tkinter PhotoImage, resized to fit."""
    h, w = image.shape[:2]
    max_w, max_h = max_size

    # Compute scale preserving aspect ratio
    scale = min(max_w / w, max_h / h, 1.0)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB) if len(resized.shape) == 3 else resized
    pil_img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(pil_img)


def get_image_info(path, image):
    """Return a dict with image metadata."""
    import os
    h, w = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1
    size_kb = os.path.getsize(path) / 1024 if path else 0
    return {
        "filename": os.path.basename(path) if path else "N/A",
        "dimensions": f"{w} × {h}",
        "channels": channels,
        "dtype": str(image.dtype),
        "size_kb": f"{size_kb:.1f} KB",
    }
