# VÉRÉ Style Advisor

**An AI style advisor for online fashion that tells you what NOT to buy.**

Submitted to the **YouCam API Skin AI & eCommerce VTO Hackathon**
($6,000 prize pool · Perfect Corp) — https://youcam-api-skin-ai-ecommerce.devpost.com

## The problem

Generative try-on renders whatever you ask for — but nobody upstream of the render
is qualified to ask. Shoppers try on the wrong things, and eCommerce returns are
driven by *"it looked different on me."* A pretty render of a bad choice is still
a bad choice.

## The solution

VÉRÉ Style Advisor puts a **decision layer** between the shopper and the render:

1. **Selfie → skin tone profile.** YouCam's *AI Facial Color Tones Analyzer*
   (`skin-tone-analysis`) reads the shopper's skin/eye/lip/brow/hair colors.
2. **Rule-based advisor judges every garment** against that profile —
   warmth harmony, tonal contrast, pattern discipline — and **refuses** bad
   matches with a stated reason, not a disclaimer:
   > *"Saturated cool color against warm skin — it pulls the eye away from your
   > face and can make skin look washed out."*
3. **Render only what survives.** Kept garments go to YouCam's *AI Clothes
   Virtual Try-On* (`cloth-v4`) for the final preview.
4. **Visible unit budget.** Every API call is a ledger line item, with live
   per-call costs pulled from YouCam's machine-readable `feature-cost` API.

A judge sees a **decision**, not just a picture.

## YouCam APIs used (all documented)

| Step | Feature | Endpoint | Units |
|---|---|---|---|
| Skin tone | `skin-tone-analysis` v1.0 | `POST /s2s/v2.0/task/skin-tone-analysis` | 20 |
| Try-on | `cloth-v4` v2.0 | `POST /s2s/v2.0/task/cloth-v4` | live cost API |
| Upload | File API | `POST /s2s/v2.0/file` + PUT upload URL | 0 |
| Budget | Credits | `GET /s2s/v1.0/client/credit`, `GET /s2s/v2.0/credit/feature-cost` | 0 |

API patterns follow the official [YouCam-API/skills](https://github.com/YouCam-API/skills)
reference (`youcam_core.py`: upload → create task → poll). Architecture inspired by the
[fit-check](https://github.com/bodycount82/fit-check) reference (decision layer +
budget tracker), rebuilt here as a FastAPI web app with a skin-*tone*-first advisor.

## Demo (no API key needed)

The app runs in **graceful demo mode** when `YOUCAM_API_KEY` is not set: a
deterministic demo skin profile and an honest, watermarked composite render —
so the full flow is testable without spending a single unit.

![Demo render](docs/demo-render.jpg)

Sample advisor output (demo profile, warm skin `#b9947c`):

```
REFUSE  28%  Emerald Satin Dress   -> Saturated cool color against warm skin...
REFUSE  34%  Royal Indigo Kurta    -> Saturated cool color against warm skin...
KEEP    74%  Ivory Linen Shirt     -> Warm tone harmonizes with your warm skin...
KEEP    68%  Terracotta Silk Blouse-> Warm tone harmonizes with your warm skin...
```

## How to run

```bash
# 1. Install
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 2. Configure (optional — demo mode works without it)
cp .env.example .env
# add your key from https://yce.perfectcorp.com/api-console/en/api-keys/

# 3. Serve
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Open http://localhost:8000
#    1) upload a selfie (or use the demo portrait)
#    2) read the advisor's verdicts (refused first, each with a reason)
#    3) render a kept garment
#    4) watch the unit budget ledger
```

Run the advisor tests: `.venv/bin/python -m pytest tests/ -q`

## Project layout

```
app/
  main.py      FastAPI routes (analyze / verdicts / tryon / budget / credits)
  youcam.py    YouCam API client (upload -> task -> poll; credits; feature costs)
  advisor.py   Rule-based style advisor (deterministic, auditable rules)
  catalog.py   8-garment demo catalog
  budget.py    Session unit-budget ledger
static/        index.html + app.js + styles.css + generated assets
scripts/gen_assets.py   generates demo portrait + garment images (PIL, original)
tests/         advisor unit tests
```

## Notes

- No secrets in code: the API key comes only from the `YOUCAM_API_KEY` env var.
- AI-generated previews are labeled as such in the UI, per YouCam's output rules.
- All demo assets are generated locally with PIL — no external images.
