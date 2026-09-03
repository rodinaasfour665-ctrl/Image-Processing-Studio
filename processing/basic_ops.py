# basic_ops.py - Point and basic image operations

import numpy as np
import cv2


def grayscale_average(image):
    """Convert to grayscale using channel averaging."""
    if len(image.shape) == 2:
        return image
    gray = np.mean(image, axis=2).astype(np.uint8)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def grayscale_weighted(image):
    """Convert to grayscale using weighted (luminosity) method."""
    if len(image.shape) == 2:
        return image
    gray = (0.299 * image[:,:,0] + 0.587 * image[:,:,1] + 0.114 * image[:,:,2]).astype(np.uint8)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def brightness_add(image, value=50):
    """Add constant to brighten image."""
    img = image.astype(np.int32)
    result = np.clip(img + value, 0, 255).astype(np.uint8)
    return result


def brightness_subtract(image, value=50):
    """Subtract constant to darken image."""
    img = image.astype(np.int32)
    result = np.clip(img - value, 0, 255).astype(np.uint8)
    return result


def brightness_multiply(image, factor=1.5):
    """Multiply pixel values to brighten image."""
    img = image.astype(np.float32)
    result = np.clip(img * factor, 0, 255).astype(np.uint8)
    return result


def brightness_divide(image, factor=2.0):
    """Divide pixel values to darken image."""
    img = image.astype(np.float32)
    result = np.clip(img / factor, 0, 255).astype(np.uint8)
    return result


def negative(image):
    """Photographic negative: y = 255 - x."""
    return (255 - image).astype(np.uint8)


def solarize(image, threshold=128):
    """Solarize: invert pixels above threshold."""
    result = image.copy()
    result[image >= threshold] = 255 - image[image >= threshold]
    return result


def red_channel(image):
    """Extract only the red channel."""
    if len(image.shape) == 2:
        return image
    result = np.zeros_like(image)
    result[:,:,2] = image[:,:,2]  # OpenCV is BGR
    return result


def green_channel(image):
    """Extract only the green channel."""
    if len(image.shape) == 2:
        return image
    result = np.zeros_like(image)
    result[:,:,1] = image[:,:,1]
    return result


def blue_channel(image):
    """Extract only the blue channel."""
    if len(image.shape) == 2:
        return image
    result = np.zeros_like(image)
    result[:,:,0] = image[:,:,0]  # OpenCV is BGR
    return result


def blend_images(image1, image2, alpha=0.6):
    """Blend two images with weight alpha for image1."""
    if image1.shape != image2.shape:
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
    return cv2.addWeighted(image1, alpha, image2, 1 - alpha, 0)


def subtract_images(image1, image2):
    """Subtract image2 from image1, clamp to 0."""
    if image1.shape != image2.shape:
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
    img1 = image1.astype(np.int32)
    img2 = image2.astype(np.int32)
    result = np.clip(img1 - img2, 0, 255).astype(np.uint8)
    return result
