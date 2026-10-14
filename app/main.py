"""VÉRÉ Style Advisor — FastAPI backend.

Flow:
  1. POST /api/analyze  — upload a selfie. Live: YouCam skin-tone-analysis.
     Demo (no key): deterministic demo profile.
  2. GET  /api/verdicts — advisor judges the catalog against the skin profile.
  3. POST /api/tryon    — render a kept garment. Live: YouCam cloth-v4.
     Demo: honest PIL composite labeled as demo.
  4. GET  /api/budget   — unit spend ledger for the session.
"""

from __future__ import annotations

import os
import shutil
import uuid
from typing import Any, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.advisor import DEMO_PROFILE, SkinProfile, judge_catalog
from app.budget import Budget
from app.catalog import BY_ID, CATALOG
from app import youcam

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = "/tmp/youcam-vto-uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="VÉRÉ Style Advisor")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Single-user demo session state (fine for a hackathon demo).
state: dict[str, Any] = {"selfie_path": None, "profile": None, "profile_source": None}
budget = Budget()


def _key() -> Optional[str]:
    return youcam.get_key()


def _init_live_costs() -> None:
    key = _key()
    if not key:
        return
    try:
        budget.set_live_costs(youcam.feature_costs(key))
    except Exception:
        pass  # fall back to documented estimates


_init_live_costs()


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


@app.get("/api/status")
def status():
    key = _key()
    return {"key_configured": bool(key),
            "mode": "live" if key else "demo",
            "estimated_costs": budget.estimated}


@app.get("/api/catalog")
def catalog():
    return [{"garment_id": g.garment_id, "name": g.name, "category": g.category,
             "color_hex": g.color_hex, "pattern": g.pattern, "sheen": g.sheen,
             "image": g.image} for g in CATALOG]


def _save_upload(upload: UploadFile) -> str:
    ext = os.path.splitext(upload.filename or "")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        raise HTTPException(400, "Please upload a JPG or PNG image.")
    name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, name)
    with open(path, "wb") as fh:
        shutil.copyfileobj(upload.file, fh)
    return path


@app.post("/api/analyze")
def analyze(selfie: UploadFile = File(...)):
    """Analyze the selfie: skin tone profile + budget line."""
    path = _save_upload(selfie)
    key = _key()
    if key:
        try:
            file_id = youcam.upload_file(key, path)
            color = youcam.skin_tone_analysis(key, file_id)
            profile = SkinProfile(
                skin_color=color.get("skin_color", "#b9947c"),
                eye_color=color.get("eye_color", "#000000"),
                lip_color=color.get("lip_color", "#000000"),
                eyebrow_color=color.get("eyebrow_color", "#000000"),
                hair_color=color.get("hair_color", "#000000"),
                source="youcam",
            )
            source = "youcam"
        except Exception as exc:  # surface API errors honestly
            raise HTTPException(502, f"YouCam API error: {exc}")
    else:
        profile = DEMO_PROFILE
        source = "demo"
    state["selfie_path"] = path
    state["profile"] = profile
    state["profile_source"] = source
    line = budget.spend("skin-tone-analysis", detail=f"profile from {source}")
    return {"profile": profile.__dict__, "budget_line": line}


@app.get("/api/verdicts")
def verdicts():
    """Advisor judgement for every catalog item (refused first, then kept)."""
    profile = state.get("profile")
    if not profile:
        raise HTTPException(400, "Analyze a selfie first.")
    return {"profile_source": state["profile_source"],
            "verdicts": [v.__dict__ for v in judge_catalog(profile, CATALOG)]}


def _asset_path(garment) -> str:
    """Map the garment's /static/... URL to a local file path."""
    rel = garment.image.lstrip("/")
    assert rel.startswith("static/"), rel
    return os.path.join(BASE_DIR, rel)


def _demo_composite(selfie_path: str, garment_id: str) -> str:
    """Honest demo-mode render: selfie + garment swatch overlay, watermarked DEMO."""
    from PIL import Image, ImageDraw
    garment = BY_ID[garment_id]
    asset = _asset_path(garment)
    base = Image.open(selfie_path).convert("RGB")
    base.thumbnail((640, 960))
    sw_img = Image.open(asset).convert("RGB")
    sw_img = sw_img.crop((0, 0, sw_img.width, int(sw_img.height * 0.90)))  # drop label bar
    sw_img = sw_img.resize((int(base.width * 0.55), int(base.height * 0.28)))
    # Knock out the near-white swatch background so the garment shape floats.
    sw = sw_img.convert("RGBA")
    px = sw.load()
    for y in range(sw.height):
        for x in range(sw.width):
            r, g, b, _ = px[x, y]
            if r > 235 and g > 235 and b > 235:
                px[x, y] = (r, g, b, 0)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay.alpha_composite(sw, (int(base.width * 0.22), int(base.height * 0.44)))
    out = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(out)
    draw.rectangle([0, out.height - 30, out.width, out.height], fill=(0, 0, 0))
    draw.text((10, out.height - 24),
              "DEMO RENDER - set YOUCAM_API_KEY for the real AI try-on",
              fill=(255, 255, 255))
    name = f"demo_{garment_id}_{uuid.uuid4().hex[:8]}.jpg"
    out_path = os.path.join(UPLOAD_DIR, name)
    out.save(out_path, "JPEG", quality=88)
    return f"/api/render/{name}"


@app.get("/api/render/{name}")
def render(name: str):
    path = os.path.join(UPLOAD_DIR, os.path.basename(name))
    if not os.path.isfile(path):
        raise HTTPException(404, "render not found")
    return FileResponse(path, media_type="image/jpeg")


@app.post("/api/tryon")
def tryon(garment_id: str = Form(...)):
    """Render the try-on for one garment the advisor kept."""
    garment = BY_ID.get(garment_id)
    if not garment:
        raise HTTPException(400, "unknown garment")
    profile = state.get("profile")
    if not profile:
        raise HTTPException(400, "Analyze a selfie first.")
    from app.advisor import judge
    verdict = judge(profile, garment)
    if not verdict.keep:
        raise HTTPException(400, f"Advisor refused this garment: {verdict.reason}")
    selfie_path = state.get("selfie_path")
    key = _key()
    if key and selfie_path:
        try:
            person_id = youcam.upload_file(key, selfie_path)
            asset = _asset_path(garment)
            garment_id_up = youcam.upload_file(key, asset)
            url = youcam.try_on(key, person_id, garment_id_up, garment.category)
            line = budget.spend("cloth-v4", detail=garment.name)
            return {"image_url": url, "mode": "live", "budget_line": line,
                    "note": "AI-generated try-on image for reference only; "
                            "actual fit and appearance may vary."}
        except Exception as exc:
            raise HTTPException(502, f"YouCam API error: {exc}")
    image_url = _demo_composite(selfie_path, garment_id)
    line = budget.spend("cloth-v4", detail=f"{garment.name} (demo render)")
    return {"image_url": image_url, "mode": "demo", "budget_line": line,
            "note": "Demo render — set YOUCAM_API_KEY for the real AI try-on."}


@app.get("/api/budget")
def get_budget():
    return budget.summary()


@app.get("/api/credits")
def credits():
    key = _key()
    if not key:
        raise HTTPException(400, "No API key configured (demo mode).")
    try:
        return youcam.check_credits(key)
    except Exception as exc:
        raise HTTPException(502, f"YouCam API error: {exc}")
