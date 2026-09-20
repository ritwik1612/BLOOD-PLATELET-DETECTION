"""Launch BPD as a self-contained Windows desktop application."""
from __future__ import annotations

import base64
import io
import mimetypes
import sys
from pathlib import Path

import webview

from web_app.app import APP_ROOT, RESULT_DIR, UPLOAD_DIR, app, artifacts_ready


def _data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


class DesktopApi:
    """Direct JavaScript-to-Python bridge; no localhost server or port is used."""

    def predict(self, encoded_image: str, filename: str) -> dict:
        try:
            payload = encoded_image.split(",", 1)[-1]
            image_bytes = base64.b64decode(payload, validate=True)
            with app.test_client() as client:
                response = client.post(
                    "/api/predict",
                    data={"image": (io.BytesIO(image_bytes), filename)},
                    content_type="multipart/form-data",
                )
                data = response.get_json() or {"error": "Analysis failed."}
            data["ok"] = response.status_code < 400
            if not data["ok"]:
                return data

            output_paths = {
                "input_url": UPLOAD_DIR,
                "annotated_url": RESULT_DIR,
                "reconstruction_url": RESULT_DIR,
            }
            for key, directory in output_paths.items():
                if data.get(key):
                    data[key] = _data_url(directory / Path(data[key]).name)
            return data
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
    return html


def _self_test(image_path: Path) -> int:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    result = DesktopApi().predict(f"data:image/jpeg;base64,{encoded}", image_path.name)
    valid = (
        result.get("ok") is True
        and isinstance(result.get("cells_detected"), int)
        and str(result.get("annotated_url", "")).startswith("data:image/")
    )
    return 0 if valid else 1


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        raise SystemExit(_self_test(Path(sys.argv[2])))
    webview.create_window(
        "Blood, in focus. — BPD",
        html=_desktop_html(),
        js_api=DesktopApi(),
        width=1440,
        height=900,
        min_size=(1024, 700),
        background_color="#f3eee4",
        text_select=True,
    )
    webview.start(gui="edgechromium", debug=False, private_mode=True, http_server=False)
