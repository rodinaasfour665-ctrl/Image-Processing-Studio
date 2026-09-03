# morphology.py - Morphological operations

import numpy as np
import cv2


def _get_kernel(size=5):
    return np.ones((size, size), np.uint8)


def erosion(image, kernel_size=5):
    """Erode image - shrinks white regions."""
    kernel = _get_kernel(kernel_size)
    return cv2.erode(image, kernel)


def dilation(image, kernel_size=5):
    """Dilate image - expands white regions."""
    kernel = _get_kernel(kernel_size)
    return cv2.dilate(image, kernel)


def opening(image, kernel_size=5):
    """Opening = erosion then dilation. Removes small bright spots."""
    kernel = _get_kernel(kernel_size)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def closing(image, kernel_size=5):
    """Closing = dilation then erosion. Fills small dark holes."""
    kernel = _get_kernel(kernel_size)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
