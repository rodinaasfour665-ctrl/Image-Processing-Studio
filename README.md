# Advanced Image Processing Studio

A fully functional desktop image processing application built for CS303.

## Features

- 50+ image processing operations across 12 categories
- Dual-panel display (Original | Processed)
- Real-time parameter sliders
- Processing log
- Histogram viewer
- Multi-image operations

## Installation

```bash
pip install opencv-python Pillow matplotlib numpy scipy
python main.py
```

## Project Structure

```
project/
├── main.py               # Entry point
├── gui/
│   ├── app_ui.py         # Main window & event wiring
│   ├── sidebar.py        # Left sidebar (file ops, info)
│   ├── image_panel.py    # Dual image display panels
│   ├── controls.py       # Right scrollable filter panel
│   └── themes.py         # Color palette & fonts
├── processing/
│   ├── basic_ops.py      # Point operations, channel ops
│   ├── filters.py        # Neighbourhood & convolutional filters
│   ├── advanced_ops.py   # Edge detection, noise, geometric
│   ├── morphology.py     # Erosion, dilation, opening, closing
│   ├── thresholding.py   # Manual, Otsu, adaptive threshold
│   ├── color_spaces.py   # HSV, CIELAB, Fourier transform
│   └── effects.py        # Gamma, sepia, posterize, vignette, sketch
├── utils/
│   ├── image_loader.py   # Load/save, format conversion
│   ├── histogram_utils.py# Histogram computation & display
│   └── helpers.py        # UI helper widgets
└── assets/               # Icons and resources
```

## Operations Reference

| Category | Operations |
|----------|-----------|
| Point | Grayscale avg/weighted, brightness ±×÷, negative, solarize, R/G/B channels |
| Histogram | Display, stretching, equalization |
| Neighbourhood | Mean, median, min, max, Gaussian |
| Sharpen | Laplacian, emboss, unsharp masking |
| Noise | Salt & pepper, Gaussian |
| Edge | Sobel, Prewitt, Canny |
| Morphology | Erosion, dilation, opening, closing |
| Threshold | Manual, Otsu, adaptive |
| Geometric | Rotate, flip H/V, zoom |
| Color | HSV, CIELAB, Fourier vis. |
| Effects | Gamma, sepia, posterize, vignette, bilateral, sketch |
| Multi-image | Blend, subtract |

## Algorithm Notes

- **Grayscale average**: (R+G+B)/3
- **Grayscale weighted**: 0.299R + 0.587G + 0.114B (ITU-R BT.601)
- **Histogram stretching**: new = (x - min) * 255 / (max - min)
- **Otsu**: maximizes inter-class variance between background and foreground
- **Canny**: Gaussian → gradients → NMS → hysteresis thresholding
- **Morphology**: structuring element (SE) applied per pixel neighborhood




