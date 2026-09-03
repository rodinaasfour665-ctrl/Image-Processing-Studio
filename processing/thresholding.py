# thresholding.py - Thresholding and segmentation

import numpy as np
import cv2


def manual_threshold(image, threshold=128):
    """Manual binary thresholding."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def otsu_threshold(image):
    """Otsu's automatic thresholding - finds optimal threshold."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def adaptive_threshold(image, block_size=11, C=2):
    """Adaptive thresholding - different thresholds per region."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    if block_size % 2 == 0:
        block_size += 1
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size, C
    )
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
