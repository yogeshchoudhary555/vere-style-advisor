# VÉRÉ Style Advisor — Demo Video Script (1–3 min, target ~2:15)

Hackathon: **YouCam API Skin AI & eCommerce VTO** (Perfect Corp, $6,000) · Deadline: 2 Nov 2026, 22:15 IST
Record: screen-capture of the app on `http://localhost:8000` + face-cam voiceover (English, Hindi optional).
Audio: your own voiceover; NO copyrighted music (Devpost rule). Keep total ≤ 2:30 so judges don't stop early.

## SHOT 0 — Title card (0:00–0:05) — 5s
- **Visual:** Black screen, text: "VÉRÉ Style Advisor — an AI style advisor that tells you what NOT to buy."
- **VO:** "VÉRÉ Style Advisor — an AI style advisor for online fashion that tells you what NOT to buy."

## SHOT 1 — Hook: the problem (0:05–0:25) — 20s
- **Visual:** Full-screen shot of the app UI landing page; cursor pans across the catalog of 8 garments.
- **VO:** "Generative try-on will render anything you ask for — but nobody upstream of the render is qualified to ask. Online fashion returns happen because *it looked different on me*. A pretty render of a bad choice is still a bad choice."
- **Overlay:** one line bottom: "The problem: pretty renders of bad choices."

## SHOT 2 — Selfie → skin profile (0:25–0:55) — 30s
- **Visual:** Upload the demo portrait in the app. Show the skin profile result panel (skin #a67f62, eye, lip, brow, hair hexes).
- **VO:** "Step one — you upload a selfie. YouCam's Skin AI — the **skin-tone-analysis** API, version 1.0 — reads your skin, eye, lip, brow and hair colors into a personal profile. This is real skin analysis, the same models powering 800-plus beauty and fashion brands. Twenty API units per analysis."
- **Key line (say it):** "Powered by the YouCam skin-tone-analysis API."

## SHOT 3 — The decision layer (0:55–1:35) — 40s
- **Visual:** Show the verdicts panel — REFUSED garments first, then KEEP.
- **VO:** "Step two — the decision layer. A rule-based advisor judges every garment against YOUR profile: warmth harmony, tonal contrast, pattern discipline. It doesn't just warn — it **refuses** bad matches with a stated reason."
- **Visual beat:** hover the Emerald Satin Dress refusal.
- **VO (read the refusal aloud):** "'Saturated cool color against warm skin — it pulls the eye away from your face and can make skin look washed out.'"
- **Visual:** pan to the Ivory Linen Shirt KEEP (74%): "'Warm tone harmonizes with your warm skin.'"
- **VO:** "Every rule is deterministic and auditable — no black box."

## SHOT 4 — Try-on: render only what survives (1:35–2:05) — 30s
- **Visual:** Click "Try On" on the Terracotta Silk Blouse. Show the render result. Then attempt try-on on the Emerald Satin Dress → show the 400 refusal.
- **VO:** "Step three — only what survives gets rendered. The kept garment goes to YouCam's **cloth-v4** AI Clothes Virtual Try-On. And watch this — if I try to render a refused garment, the advisor blocks it. The try-on serves the decision, not the other way round."
- **Key line (say it):** "Using YouCam's cloth-v4 AI try-on API."

## SHOT 5 — Unit budget ledger (2:05–2:20) — 15s
- **Visual:** Show the budget ledger panel.
- **VO:** "Every API call is a ledger line item — live per-call costs pulled from YouCam's machine-readable feature-cost API. Store owners see exactly what each shopper session costs."

## SHOT 6 — Close (2:20–2:30) — 10s
- **Visual:** App hero shot. Bottom line text: "Built with YouCam Skin AI + Cloth VTO · Code on GitHub."
- **VO:** "VÉRÉ Style Advisor — judge, don't just render. Built with YouCam Skin AI and cloth virtual try-on. Full code on GitHub."
- **End card:** repo URL.

## Judge checklist covered
- [ ] 1–3 min (target 2:15–2:30) ✓
- [ ] Explains the YouCam APIs used: skin-tone-analysis (Skin AI) + cloth-v4 (Apparel VTO) ✓
- [ ] Footage of the project functioning on its device (screen capture of web app) ✓
- [ ] No third-party trademarks / copyrighted music ✓
- [ ] Public on YouTube, link in Devpost form ✓ (upload as Unlisted→Public; keep "Made for Kids: No")

## Recording notes
- Record in **demo mode** (no key needed, deterministic) OR top up YouCam units and record live. Demo mode is safer — no API surprises mid-record.
- 1080p, 16:9. Export H.264.
- If recording live: keep a backup demo-mode take.
