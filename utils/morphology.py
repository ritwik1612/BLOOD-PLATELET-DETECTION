from __future__ import annotations

"""Conservative cell-centering for frozen autoencoder experiments."""

import cv2
import numpy as np


def standardize_cell_crop(image: np.ndarray, output_size: int = 64) -> np.ndarray:
    """Center the dominant stained object without altering its morphology.

    Returns the original crop when a reliable central object cannot be found.
    This helper is deliberately inference-only; it does not sharpen, recolour,
    synthesize, or otherwise enhance a cell.
    """
    if image.size == 0:
        return image
    height, width = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation, value = hsv[:, :, 1], hsv[:, :, 2]
    mask = ((saturation >= max(18, int(np.percentile(saturation, 55)))) & (value <= 248)).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    if count <= 1:
        return cv2.resize(image, (output_size, output_size), interpolation=cv2.INTER_AREA)

    center = np.array([width / 2, height / 2])
    candidates = []
    for index in range(1, count):
        area = int(stats[index, cv2.CC_STAT_AREA])
        if area < max(12, int(0.02 * width * height)):
            continue
        distance = float(np.linalg.norm(centroids[index] - center))
        candidates.append((distance / max(width, height) - 0.002 * area, index))
    if not candidates:
        return cv2.resize(image, (output_size, output_size), interpolation=cv2.INTER_AREA)

    selected = min(candidates)[1]
    left, top, component_width, component_height, _ = stats[selected]
    padding = max(2, int(0.15 * max(component_width, component_height)))
    left, top = max(0, left - padding), max(0, top - padding)
    right, bottom = min(width, left + component_width + 2 * padding), min(height, top + component_height + 2 * padding)
    cell = image[top:bottom, left:right]
    if cell.size == 0:
        return cv2.resize(image, (output_size, output_size), interpolation=cv2.INTER_AREA)
    return cv2.resize(cell, (output_size, output_size), interpolation=cv2.INTER_AREA)
