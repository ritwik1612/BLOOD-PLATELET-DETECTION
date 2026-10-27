"""Launch BPD as a self-contained Windows desktop application."""
from __future__ import annotations

import base64
import io
import json
import tempfile
import time

import cv2
import mimetypes
import sys
from pathlib import Path

import webview

from web_app.app import APP_ROOT, RESULT_DIR, UPLOAD_DIR, app, artifacts_ready, get_pipeline
from utils.image_quality import assess_smear_image


def _data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


class DesktopApi:
    """Direct JavaScript-to-Python bridge; no localhost server or port is used."""

    def predict(self, encoded_image: str, filename: str) -> dict:
        """Present existing pipeline results to the desktop UI without changing scoring."""
        started = time.perf_counter()
        try:
            suffix = Path(filename).suffix.lower()
            if suffix not in {".png", ".jpg", ".jpeg"}:
                return {"ok": False, "error": "Choose a PNG or JPEG image."}
            payload = encoded_image.split(",", 1)[-1]
            image_bytes = base64.b64decode(payload, validate=True)
            if len(image_bytes) > 20 * 1024 * 1024:
                return {"ok": False, "error": "Choose an image smaller than 20 MB."}
            with tempfile.TemporaryDirectory(prefix="bpd-ui-") as temporary:
                source = Path(temporary) / ("specimen" + suffix)
                source.write_bytes(image_bytes)
                image = cv2.imread(str(source))
                if image is None:
                    return {"ok": False, "error": "The selected file is not a readable image."}
                quality = assess_smear_image(image)
                if quality["status"] == "reject":
                    return {"ok": False, "error": quality["message"], "quality": quality}
                pipeline = get_pipeline()
                image, detections = pipeline.analyze_path(source)
                rows = []
                for index, item in enumerate(detections, start=1):
                    rows.append({
                        "id": index,
                        "class_id": int(item["class_id"]),
                        "class_label": item["class_label"],
                        "label": item["display_label"],
                        "xyxy": [int(value) for value in item["xyxy"]],
                        "status": item["status"],
                        "confidence": float(item["confidence"]),
                        "mse": float(item["mse"]),
                        "cosine_distance": float(item["cosine_distance"]),
                        "anomaly_score": float(item["anomaly_score"]),
                        "threshold": float(item.get("anomaly_threshold", pipeline.threshold)),
                    })
                return {
                    "ok": True,
                    "filename": filename,
                    "width": int(image.shape[1]),
                    "height": int(image.shape[0]),
                    "seconds": round(time.perf_counter() - started, 2),
                    "cells_detected": len(rows),
                    "abnormal_cells": sum(item["status"] == "Abnormal" for item in rows),
                    "quality": quality,
                    "detections": rows,
                    "input_url": _data_url(source),
                }
        except Exception as error:
            return {"ok": False, "error": str(error)}


def _desktop_html() -> str:
    html = (APP_ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    css = (APP_ROOT / "static" / "style.css").read_text(encoding="utf-8")
    javascript = (APP_ROOT / "static" / "app.js").read_text(encoding="utf-8")
    ready = artifacts_ready()
    html = html.replace(
        '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'style.css\') }}">',
        f"<style>{css}</style>",
    )
    html = html.replace("{{ 'ready' if ready else 'pending' }}", "ready" if ready else "pending")
    html = html.replace("{{ 'MODEL READY' if ready else 'MODEL PREPARING' }}", "MODEL READY" if ready else "MODEL PREPARING")
    html = html.replace(
        '<script src="{{ url_for(\'static\', filename=\'app.js\') }}"></script>',
        f"<script>{javascript}</script>",
    )
    for filename, mime_type in (("manrope.ttf", "font/ttf"), ("dm-serif.ttf", "font/ttf")):
        font_path = APP_ROOT / "static" / "fonts" / filename
        font_data = base64.b64encode(font_path.read_bytes()).decode("ascii")
        html = html.replace(f"fonts/{filename}", f"data:{mime_type};base64,{font_data}")
    return html


def _self_test(image_path: Path, report_path: Path | None = None) -> int:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    result = DesktopApi().predict(f"data:image/jpeg;base64,{encoded}", image_path.name)
    valid = (
        result.get("ok") is True
        and isinstance(result.get("cells_detected"), int)
        and str(result.get("input_url", "")).startswith("data:image/")
        and all("xyxy" in cell and "threshold" in cell for cell in result.get("detections", []))
    )
    if report_path is not None:
        report_path.write_text(json.dumps({
            "ok": valid,
            "cells_detected": result.get("cells_detected"),
            "review_candidates": result.get("abnormal_cells"),
            "detections": result.get("detections", []),
            "error": result.get("error"),
            "ui_fonts_embedded": "data:font/ttf;base64," in _desktop_html(),
        }, indent=2), encoding="utf-8")
    return 0 if valid else 1


if __name__ == "__main__":
    if len(sys.argv) in (3, 4) and sys.argv[1] == "--self-test":
        raise SystemExit(_self_test(Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) == 4 else None))
    webview.create_window(
        "BPD — Blood cell analysis",
        html=_desktop_html(),
        js_api=DesktopApi(),
        width=1440,
        height=900,
        min_size=(1024, 700),
        background_color="#000000",
        text_select=True,
    )
    webview.start(gui="edgechromium", debug=False, private_mode=True, http_server=False)
