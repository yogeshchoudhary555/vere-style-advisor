# Devpost Submission Draft — YouCam API Skin AI & eCommerce VTO Hackathon

**Project:** VÉRÉ Style Advisor
**Deadline:** 2 Nov 2026, 22:15 IST
**Submit at:** https://youcam-api-skin-ai-ecommerce.devpost.com (sign in → Start project → fill → Submit)
**Status:** app built & tested · repo PUBLIC · demo video script ready · video RECORDING pending (needs ~2h hands-on session)

## Fields to paste

**Project name:**
VÉRÉ Style Advisor — an AI style advisor that tells you what NOT to buy

**Tagline:**
A decision layer between the shopper and the render: YouCam Skin AI reads your face, a rule-based advisor refuses bad matches with stated reasons, and only what survives gets virtually tried on.

**Description (About the project):**
Generative try-on renders whatever you ask for — but nobody upstream of the render is qualified to ask. Shoppers try on the wrong things, and eCommerce returns are driven by "it looked different on me." A pretty render of a bad choice is still a bad choice.

VÉRÉ Style Advisor puts a **decision layer** between the shopper and the render:

1. **Selfie → skin tone profile.** YouCam's AI Facial Color Tones Analyzer (`skin-tone-analysis` v1.0) reads the shopper's skin, eye, lip, brow and hair colors.
2. **Rule-based advisor judges every garment** against that profile — warmth harmony, tonal contrast, pattern discipline — and **refuses** bad matches with a stated reason, not a disclaimer: "Saturated cool color against warm skin — it pulls the eye away from your face and can make skin look washed out."
3. **Render only what survives.** Kept garments go to YouCam's AI Clothes Virtual Try-On (`cloth-v4` v2.0) for the final preview. The advisor also blocks try-on of refused garments.
4. **Visible unit budget.** Every API call is a ledger line item, with live per-call costs pulled from YouCam's machine-readable `feature-cost` API — so store owners see what each session costs.

YouCam APIs used: `skin-tone-analysis` (20 units), `cloth-v4` (live cost API), File API (0 units), Credits + feature-cost APIs (0 units). The app runs in graceful demo mode when no API key is set, so the full flow is testable without spending units. Live API verified: two real skin-tone analyses (cross-photo color stability confirmed) before units ran out.

Built by one builder (Yogesh Choudhary) for VÉRÉ Premium Fashion — his own fashion store's return-rate problem is the motivation.

**Built with:** Python, FastAPI, YouCam API (Skin AI `skin-tone-analysis` v1.0, Apparel VTO `cloth-v4` v2.0), JavaScript, HTML/CSS, PIL, Pytest

**Code repository:** https://github.com/yogeshchoudhary555/vere-style-advisor (public, Apache-2.0)

**Demo video:** (PENDING — record from DEMO-VIDEO-SCRIPT.md, upload to YouTube Public, paste link here)

**Track/topic:** eCommerce VTO

**Screenshots:** REQUIRED by rules — capture: (1) skin profile panel, (2) verdicts panel (refusals first), (3) try-on render, (4) budget ledger. Upload all four on the submission form.

**Winners' terms (agreed by submitting):** must do an exit interview if chosen; must agree to be in a blog article.

## Judging criteria this targets
- **Technological Implementation:** two YouCam APIs deeply integrated (not one decorative call) + live feature-cost API + strictness fallback (high→medium) on face-angle errors.
- **Design:** complete coherent product experience — selfie → verdicts → try-on → budget, demo mode for judges.
- **Potential Impact:** fashion returns are a real, expensive eCommerce pain; ties to his own store.
- **Quality of Idea:** the non-obvious move is the *refusal* layer — judging garments, not just rendering them.

## Remaining owner steps (2 min each)
1. Record 2:15 demo video (DEMO-VIDEO-SCRIPT.md) → YouTube Public.
2. Open Devpost page on his phone/laptop → paste the fields above → attach 4 screenshots → tick rules checkbox → Submit before 2 Nov 22:15 IST.
