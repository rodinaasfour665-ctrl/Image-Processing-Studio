# advanced_ops.py - Edge detection, noise, geometric operations

import numpy as np
import cv2


# ─── EDGE DETECTION ────────────────────────────────────────────────

def sobel_edge(image):
    """Sobel edge detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    result = np.clip(magnitude, 0, 255).astype(np.uint8)
    return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)


def prewitt_edge(image):
    """Prewitt edge detection using custom kernels."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    gx = cv2.filter2D(gray.astype(np.float32), -1, kernel_x)
    gy = cv2.filter2D(gray.astype(np.float32), -1, kernel_y)
    magnitude = np.clip(np.sqrt(gx**2 + gy**2), 0, 255).astype(np.uint8)
    return cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)


def canny_edge(image, low=50, high=150):
    """Canny edge detector."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    edges = cv2.Canny(gray, low, high)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


# ─── NOISE ─────────────────────────────────────────────────────────

def salt_pepper_noise(image, noise_ratio=0.05):
    """Add salt & pepper noise."""
    result = image.copy()
    total = image.size
    num_noise = int(noise_ratio * total)
    # Salt (white)
    salt_coords = [np.random.randint(0, i, num_noise // 2) for i in image.shape[:2]]
    result[salt_coords[0], salt_coords[1]] = 255
    # Pepper (black)
    pepper_coords = [np.random.randint(0, i, num_noise // 2) for i in image.shape[:2]]
    result[pepper_coords[0], pepper_coords[1]] = 0
    return result


def gaussian_noise(image, mean=0, sigma=25):
    """Add Gaussian noise."""
    noise = np.random.normal(mean, sigma, image.shape).astype(np.float32)
    result = np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return result


# ─── GEOMETRIC OPERATIONS ──────────────────────────────────────────

def rotate_image(image, angle=45):
    """Rotate image by given angle (degrees)."""
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), borderValue=(20, 42, 48))


def flip_horizontal(image):
    """Flip image horizontally."""
    return cv2.flip(image, 1)


def flip_vertical(image):
    """Flip image vertically."""
    return cv2.flip(image, 0)


def zoom_image(image, factor=1.5):
    """Zoom into center of image."""
    h, w = image.shape[:2]
    new_h, new_w = int(h / factor), int(w / factor)
    y1 = (h - new_h) // 2
    x1 = (w - new_w) // 2
    cropped = image[y1:y1+new_h, x1:x1+new_w]
    return cv2.resize(cropped, (w, h))
