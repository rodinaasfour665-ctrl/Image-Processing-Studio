# color_spaces.py - Color space conversions and frequency domain

import numpy as np
import cv2


def to_hsv(image):
    """Convert BGR to HSV and back for display."""
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Return as BGR for display
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def to_lab(image):
    """Convert BGR to CIELAB color space."""
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    return lab


def fourier_transform_vis(image):
    """Visualize Fourier Transform magnitude spectrum."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    dft = np.fft.fft2(gray.astype(np.float32))
    dft_shift = np.fft.fftshift(dft)
    magnitude = 20 * np.log(np.abs(dft_shift) + 1)
    magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)
