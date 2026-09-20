from __future__ import annotations

"""Conservative microscopy image-quality checks used before model inference."""

import cv2
import numpy as np


def assess_smear_image(image: np.ndarray) -> dict[str, object]:
    """Return an explainable quality assessment without altering pixel data.

    The thresholds intentionally reject only clearly unusable images. Borderline
    images proceed with a visible review warning rather than being enhanced or
    silently reinterpreted by the detector.
    """
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        return {
            "status": "reject",
            "label": "Unreadable image",
            "score": 0,
            "message": "Use a readable colour PNG or JPEG smear image.",
            "issues": ["The uploaded image is not a readable colour image."],
        }

    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    focus_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    lower, upper = np.percentile(gray, (10, 90))
    contrast = float(upper - lower)
    brightness = float(gray.mean())
    clipped_fraction = float(((gray <= 3) | (gray >= 252)).mean())
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    stained_fraction = float(((hsv[:, :, 1] >= 18) & (hsv[:, :, 2] <= 248)).mean())

    # CBC/TXL microscope images are naturally low-frequency after JPEG export.
    # A field may remain usable below photographic sharpness levels, but fields
    # below this range need a review warning because fine cell boundaries blur.
    focus_score = min(1.0, focus_variance / 25.0)
    contrast_score = min(1.0, contrast / 60.0)
    exposure_score = max(0.0, 1.0 - abs(brightness - 130.0) / 130.0)
    quality_score = round(100 * (0.50 * focus_score + 0.30 * contrast_score + 0.20 * exposure_score))

    issues: list[str] = []
    if min(height, width) < 256:
        issues.append("Image resolution is too low for reliable cell localization.")
    if focus_variance < 3:
        issues.append("The smear is strongly out of focus or blurred.")
    elif focus_variance < 25:
        issues.append("The smear appears soft; small-cell counts may be incomplete.")
    if contrast < 18:
        issues.append("The image has very low contrast.")
    elif contrast < 35:
        issues.append("The image contrast is limited.")
    if brightness < 25 or brightness > 235 or clipped_fraction > 0.35:
        issues.append("The image is severely underexposed or overexposed.")
    elif brightness < 45 or brightness > 215:
        issues.append("The image exposure is outside the preferred range.")
    if stained_fraction < 0.04:
        issues.append("Very little stain is visible; cell boundaries may be missed.")
    elif stained_fraction > 0.82:
        issues.append("Very high stain coverage may indicate crowding or uneven staining.")

    unusable = min(height, width) < 256 or focus_variance < 3 or contrast < 18 or brightness < 25 or brightness > 235
    if unusable:
        status, label = "reject", "Quality insufficient"
        message = "Retake the smear with sharper focus, even illumination, and a higher-resolution field before analysis."
    elif issues:
        status, label = "review", "Quality needs review"
        message = "Analysis completed, but image quality may reduce detection reliability. Review counts and flagged cells cautiously."
    else:
        status, label = "acceptable", "Quality acceptable"
        message = "Image quality is suitable for automated screening."

    return {
        "status": status,
        "label": label,
        "score": int(quality_score),
        "message": message,
        "issues": issues,
        "measurements": {
            "width": width,
            "height": height,
            "focus_variance": round(focus_variance, 1),
            "contrast": round(contrast, 1),
            "brightness": round(brightness, 1),
            "stained_fraction": round(stained_fraction, 3),
        },
    }
