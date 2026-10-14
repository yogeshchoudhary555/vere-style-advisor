"""Rule-based style advisor: decides what is worth rendering, refuses the rest.

Deterministic and auditable — a judge can read exactly why each rule fired.
Inspired by the fit-check reference architecture (same seam: profile + candidate
-> judgement with a stated reason), but built for the VÉRÉ Style Advisor concept:
skin-TONE-first harmony scoring instead of skin-concern scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------- dataclasses

@dataclass
class SkinProfile:
    """Skin tone profile, from YouCam skin-tone-analysis or the demo profile."""
    skin_color: str            # hex, e.g. "#b9947c"
    eye_color: str = "#000000"
    lip_color: str = "#000000"
    eyebrow_color: str = "#000000"
    hair_color: str = "#000000"
    source: str = "demo"       # "youcam" or "demo"


@dataclass
class Garment:
    garment_id: str
    name: str
    category: str              # YouCam cloth-v4 garment_category token
    color_hex: str
    warmth: float              # -1 (cool) .. +1 (warm); computed from color if 0
    pattern: str               # "solid" | "subtle" | "bold"
    sheen: str                 # "matte" | "satin" | "shine"
    image: str                 # static path of the garment reference image


@dataclass
class Judgement:
    garment_id: str
    name: str
    score: int                 # 0..100 — "this color suits your skin tone: N%"
    keep: bool
    reason: str                # the stated reason (keep or refuse)
    rules_fired: list = field(default_factory=list)


# ---------------------------------------------------------------- color math

def _rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0


def color_warmth(hex_color: str) -> float:
    """-1 (cold blue) .. +1 (warm red/orange), from the red-vs-blue balance."""
    r, _, b = _rgb(hex_color)
    return max(-1.0, min(1.0, (r - b) * 2.0))


def color_lightness(hex_color: str) -> float:
    r, g, b = _rgb(hex_color)
    return (r + g + b) / 3.0


def color_saturation(hex_color: str) -> float:
    r, g, b = _rgb(hex_color)
    mx, mn = max(r, g, b), min(r, g, b)
    return 0.0 if mx == 0 else (mx - mn) / mx


# ---------------------------------------------------------------- the rules

KEEP_THRESHOLD = 55

# Each rule: (id, applies(profile, garment) -> delta, reason_template)
RULES = [
    (
        "warm_harmony",
        lambda p, g: color_warmth(p.skin_color) > 0.15 and color_warmth(g.color_hex) > 0.1,
        +18,
        "Warm tone harmonizes with your warm skin — it flatters instead of fighting it.",
    ),
    (
        "cool_harmony",
        lambda p, g: color_warmth(p.skin_color) < -0.15 and color_warmth(g.color_hex) < -0.1,
        +18,
        "Cool tone harmonizes with your cool skin — clean, balanced contrast.",
    ),
    (
        "warmth_clash",
        lambda p, g: (color_warmth(p.skin_color) > 0.2 and color_warmth(g.color_hex) < -0.25
                      and color_saturation(g.color_hex) > 0.45),
        -16,
        "Saturated cool color against warm skin — it pulls the eye away from your face "
        "and can make skin look washed out.",
    ),
    (
        "reverse_clash",
        lambda p, g: (color_warmth(p.skin_color) < -0.2 and color_warmth(g.color_hex) > 0.25
                      and color_saturation(g.color_hex) > 0.45),
        -16,
        "Saturated warm color against cool skin — the clash fights your natural tone.",
    ),
    (
        "deep_skin_low_contrast",
        lambda p, g: color_lightness(p.skin_color) < 0.35
                      and abs(color_lightness(g.color_hex) - color_lightness(p.skin_color)) < 0.12,
        -10,
        "Too close to your skin depth — low contrast, the garment disappears on you.",
    ),
    (
        "strong_silhouette",
        lambda p, g: abs(color_lightness(g.color_hex) - color_lightness(p.skin_color)) > 0.35,
        +8,
        "Good tonal separation from your skin — defines your silhouette crisply.",
    ),
    (
        "bold_pattern_noise",
        lambda p, g: g.pattern == "bold",
        -8,
        "Bold pattern competes with your complexion — the print wears you, not the reverse.",
    ),
    (
        "satin_sheen_risk",
        lambda p, g: g.sheen == "shine",
        -6,
        "High sheen catches light unpredictably in photos — flattering in person, "
        "risky in a render.",
    ),
    (
        "neutral_safe",
        lambda p, g: g.pattern == "solid" and color_saturation(g.color_hex) < 0.35,
        +6,
        "Solid, muted neutral — an easy, dependable base for your tone.",
    ),
]


def judge(profile: SkinProfile, garment: Garment) -> Judgement:
    """Score one garment against the skin profile; refuse with a reason if < threshold."""
    score = 50
    fired: list[str] = []
    pos_reasons: list[str] = []
    neg_reasons: list[str] = []
    for rule_id, applies, delta, reason in RULES:
        if applies(profile, garment):
            score += delta
            fired.append(rule_id)
            (pos_reasons if delta > 0 else neg_reasons).append(reason)
    score = max(0, min(100, score))
    keep = score >= KEEP_THRESHOLD
    if keep:
        reason = pos_reasons[0] if pos_reasons else "Balanced match for your skin tone."
    else:
        reason = neg_reasons[0] if neg_reasons else "Tone mismatch — a better color exists."
    return Judgement(garment_id=garment.garment_id, name=garment.name, score=score,
                     keep=keep, reason=reason, rules_fired=fired)


def judge_catalog(profile: SkinProfile, catalog: list[Garment]) -> list[Judgement]:
    """Judge every catalog item; refused items first (the advisor's signature view),
    then kept items, each sorted by score."""
    verdicts = [judge(profile, g) for g in catalog]
    refused = sorted((v for v in verdicts if not v.keep), key=lambda v: v.score)
    kept = sorted((v for v in verdicts if v.keep), key=lambda v: v.score, reverse=True)
    return refused + kept


# The built-in demo profile (used when no API key is set).
DEMO_PROFILE = SkinProfile(
    skin_color="#b9947c",
    eye_color="#4a3226",
    lip_color="#a05a58",
    eyebrow_color="#3d2b22",
    hair_color="#2e1d14",
    source="demo",
)
