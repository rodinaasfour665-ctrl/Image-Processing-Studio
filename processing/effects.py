# effects.py - Visual effects and enhancements

import numpy as np
import cv2


def gamma_correction(image, gamma=1.5):
    """Gamma correction: y = (x/255)^gamma * 255."""
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)], dtype=np.uint8)
    return cv2.LUT(image, table)


def sepia_tone(image):
    """Apply warm sepia toning."""
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    img_float = image.astype(np.float32)
    r = np.clip(img_float[:,:,2]*0.393 + img_float[:,:,1]*0.769 + img_float[:,:,0]*0.189, 0, 255)
    g = np.clip(img_float[:,:,2]*0.349 + img_float[:,:,1]*0.686 + img_float[:,:,0]*0.168, 0, 255)
    b = np.clip(img_float[:,:,2]*0.272 + img_float[:,:,1]*0.534 + img_float[:,:,0]*0.131, 0, 255)
    sepia = np.stack([b, g, r], axis=2).astype(np.uint8)
    return sepia


def posterize(image, levels=4):
    """Reduce number of color levels (posterize)."""
    shift = 8 - int(np.log2(levels)) if levels > 1 else 7
    return ((image >> shift) << shift).astype(np.uint8)


def vignette(image, strength=0.5):
    """Apply vignette effect - darken corners."""
    h, w = image.shape[:2]
    sigma_x = w / 2
    sigma_y = h / 2
    X = np.linspace(-1, 1, w)
    Y = np.linspace(-1, 1, h)
    Xv, Yv = np.meshgrid(X, Y)
    mask = np.exp(-(Xv**2 / (2 * (1-strength)**2) + Yv**2 / (2 * (1-strength)**2)))
    mask = (mask / mask.max())
    if len(image.shape) == 3:
        mask = mask[:, :, np.newaxis]
    return np.clip(image.astype(np.float32) * mask, 0, 255).astype(np.uint8)


def sketch_effect(image):
    """Create pencil sketch effect."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    inv = 255 - gray
    blurred = cv2.GaussianBlur(inv, (21, 21), 0)
    inv_blurred = 255 - blurred
    sketch = np.clip(gray.astype(np.float32) * 255 / (inv_blurred.astype(np.float32) + 1), 0, 255).astype(np.uint8)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
