# filters.py - Neighbourhood filters, sharpening, and convolution

import numpy as np
import cv2
from scipy.ndimage import convolve


def _to_gray(image):
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def _apply_per_channel(image, func, **kwargs):
    """Apply a grayscale filter to each channel of a color image."""
    if len(image.shape) == 2:
        return func(image, **kwargs)
    channels = cv2.split(image)
    processed = [func(ch, **kwargs) for ch in channels]
    return cv2.merge(processed)


def mean_filter(image, kernel_size=3):
    """Mean (average) filter using OpenCV."""
    return cv2.blur(image, (kernel_size, kernel_size))


def median_filter(image, kernel_size=3):
    """Median filter - best for salt & pepper noise."""
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.medianBlur(image, kernel_size)


def min_filter(image, kernel_size=3):
    """Min filter - useful for removing salt noise."""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.erode(image, kernel)


def max_filter(image, kernel_size=3):
    """Max filter - useful for removing pepper noise."""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.dilate(image, kernel)


def gaussian_filter(image, kernel_size=5, sigma=1.0):
    """Gaussian smoothing filter."""
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)


def laplacian_sharpening(image):
    """Laplacian sharpening: subtract Laplacian from original."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        sharpened = np.clip(gray.astype(np.float64) - lap, 0, 255).astype(np.uint8)
        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
    lap = cv2.Laplacian(image, cv2.CV_64F)
    return np.clip(image.astype(np.float64) - lap, 0, 255).astype(np.uint8)


def emboss_filter(image):
    """Emboss effect using convolution kernel."""
    kernel = np.array([[-2, -1,  0],
                       [-1,  1,  1],
                       [ 0,  1,  2]], dtype=np.float32)
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        embossed = cv2.filter2D(gray, -1, kernel) + 128
        return cv2.cvtColor(np.clip(embossed, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    return np.clip(cv2.filter2D(image, -1, kernel) + 128, 0, 255).astype(np.uint8)


def unsharp_masking(image, kernel_size=5, sigma=1.0, amount=1.5):
    """Unsharp masking: original + amount * (original - blurred)."""
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
    result = cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)
    return np.clip(result, 0, 255).astype(np.uint8)


def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """Bilateral filter - smooths while preserving edges."""
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
