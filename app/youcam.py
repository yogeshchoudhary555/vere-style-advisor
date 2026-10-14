"""Thin client for the YouCam AI REST API (Perfect Corp).

Endpoints used are documented in the official YouCam-API skills repo
(https://github.com/YouCam-API/skills) and the public API reference
(https://yce.perfectcorp.com/document/index.html):
  - POST {base}/s2s/v2.0/file              -> upload URL + file_id
  - POST {base}/s2s/v2.0/task/skin-tone-analysis
  - GET  {base}/s2s/v2.0/task/skin-tone-analysis/{task_id}
  - POST {base}/s2s/v2.0/task/cloth-v4
  - GET  {base}/s2s/v2.0/task/cloth-v4/{task_id}
  - GET  {base}/s2s/v1.0/client/credit
  - GET  {base}/s2s/v2.0/credit/feature-cost

Auth: Bearer token from the YOUCAM_API_KEY env var (never hardcoded).
"""

from __future__ import annotations

import mimetypes
import os
import time
from typing import Any, Optional

import requests

BASE_URL = "https://yce-api-01.makeupar.com"
FILE_PATH = "/s2s/v2.0/file"
CREDIT_BALANCE_PATH = "/s2s/v1.0/client/credit"
FEATURE_COST_PATH = "/s2s/v2.0/credit/feature-cost"

FEATURES = {
    # feature name -> (version, unit cost documented; cost is re-queried live when keyed)
    "skin-tone-analysis": ("v2.0", 20),
    "cloth-v4": ("v2.0", None),  # live cost queried from feature-cost API
}

_REQUEST_TIMEOUT = 30
_POLL_INTERVAL = 2.0
_MAX_POLLS = 45
_TERMINAL = {"success", "error"}


class YouCamError(RuntimeError):
    """Raised when a YouCam API call fails."""


def get_key() -> Optional[str]:
    return os.environ.get("YOUCAM_API_KEY") or None


def _headers(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def check_credits(key: str) -> dict[str, Any]:
    """Return spendable unit balance (0 credits consumed by this call)."""
    r = requests.get(f"{BASE_URL}{CREDIT_BALANCE_PATH}", headers=_headers(key),
                     timeout=_REQUEST_TIMEOUT)
    r.raise_for_status()
    batches = r.json().get("results", []) or []
    spendable = sum(b.get("amount", 0) for b in batches
                    if str(b.get("type", "")).startswith("Api"))
    return {"api_spendable_units": spendable,
            "by_type": {b.get("type", "?"): b.get("amount", 0) for b in batches}}


def feature_costs(key: str) -> dict[str, int]:
    """Per-call unit cost per feature from the machine-readable cost API."""
    costs: dict[str, int] = {}
    token: Optional[str] = None
    while True:
        params = {"page_size": 20}
        if token:
            params["starting_token"] = token
        r = requests.get(f"{BASE_URL}{FEATURE_COST_PATH}", headers=_headers(key),
                         params=params, timeout=_REQUEST_TIMEOUT)
        r.raise_for_status()
        res = r.json().get("result", {}) or {}
        for s in res.get("skus", []) or []:
            url = s.get("run_task_url", "")
            slug = url.rstrip("/").split("/task/")[-1] if "/task/" in url else None
            if slug:
                costs[slug] = int(s.get("amount", 0))
        token = res.get("next_token")
        if not token:
            break
    return costs


def upload_file(key: str, path: str) -> str:
    """Upload a local image via the File API; returns the file_id."""
    if not os.path.isfile(path):
        raise YouCamError(f"file not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        raise YouCamError(f"unsupported image type {ext} (need jpg/png)")
    content_type = mimetypes.guess_type(path)[0] or "image/jpeg"
    meta = requests.post(
        f"{BASE_URL}{FILE_PATH}",
        headers=_headers(key),
        json={"files": [{"content_type": content_type,
                         "file_name": os.path.basename(path),
                         "file_size": os.path.getsize(path)}]},
        timeout=_REQUEST_TIMEOUT,
    )
    meta.raise_for_status()
    info = meta.json()["data"]["files"][0]
    put = info["requests"][0]
    with open(path, "rb") as fh:
        requests.put(put["url"], headers=put.get("headers", {"Content-Type": content_type}),
                     data=fh, timeout=120).raise_for_status()
    return info["file_id"]


def create_task(key: str, feature: str, body: dict[str, Any]) -> str:
    version, _ = FEATURES[feature]
    r = requests.post(f"{BASE_URL}/s2s/{version}/task/{feature}",
                      headers=_headers(key), json=body, timeout=_REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()["data"]["task_id"]


def poll_task(key: str, feature: str, task_id: str) -> dict[str, Any]:
    version, _ = FEATURES[feature]
    url = f"{BASE_URL}/s2s/{version}/task/{feature}/{task_id}"
    data: dict[str, Any] = {}
    for _ in range(_MAX_POLLS):
        r = requests.get(url, headers=_headers(key), timeout=_REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json().get("data", {})
        if data.get("task_status") in _TERMINAL:
            break
        time.sleep(_POLL_INTERVAL)
    return {**data, "task_id": task_id}


def run_feature(key: str, feature: str, body: dict[str, Any]) -> dict[str, Any]:
    """Create a task and poll until it finishes; raises YouCamError on failure."""
    task_id = create_task(key, feature, body)
    result = poll_task(key, feature, task_id)
    if result.get("task_status") == "error":
        raise YouCamError(f"{feature} task failed: {result}")
    return result


def skin_tone_analysis(key: str, src_file_id: str,
                       strictness: str = "high") -> dict[str, Any]:
    """Run AI Facial Color Tones Analyzer. Returns the 'color' result dict."""
    result = run_feature(
        key, "skin-tone-analysis",
        {"src_file_id": src_file_id, "face_angle_strictness_level": strictness},
    )
    color = (result.get("results", {}) or {}).get("color", {})
    if not color:
        raise YouCamError(f"no color result: {result}")
    return color


def try_on(key: str, person_file_id: str, garment_file_id: str,
           garment_category: str = "auto") -> str:
    """Run AI Clothes Virtual Try-On. Returns the result image URL."""
    result = run_feature(
        key, "cloth-v4",
        {"src_file_id": person_file_id, "ref_file_id": garment_file_id,
         "garment_category": garment_category},
    )
    url = (result.get("results", {}) or {}).get("url")
    if not url:
        raise YouCamError(f"no result image url: {result}")
    return url
