"""Deterministic tests for the rule-based style advisor."""

from app.advisor import (
    DEMO_PROFILE,
    Garment,
    SkinProfile,
    color_lightness,
    color_saturation,
    color_warmth,
    judge,
    judge_catalog,
)


def _warm_profile() -> SkinProfile:
    return SkinProfile(skin_color="#b9947c", source="test")


def _garment(gid="t1", color="#C1553B", pattern="solid", sheen="matte",
             name="Test Garment") -> Garment:
    return Garment(garment_id=gid, name=name, category="upper_body",
                   color_hex=color, warmth=0.0, pattern=pattern,
                   sheen=sheen, image="/static/x.png")


def test_color_math_sanity():
    assert color_warmth("#ff0000") > 0.5      # pure red is warm
    assert color_warmth("#0000ff") < -0.5     # pure blue is cool
    assert color_lightness("#ffffff") > 0.9
    assert color_lightness("#000000") < 0.1
    assert color_saturation("#ff0000") > 0.9
    assert color_saturation("#808080") < 0.1


def test_warm_harmony_keeps():
    v = judge(_warm_profile(), _garment(color="#C1553B"))
    assert v.keep and v.score >= 55
    assert "warm" in v.reason.lower()


def test_cool_clash_refuses_with_reason():
    v = judge(_warm_profile(), _garment(gid="t2", color="#1a2aff", name="Neon Blue"))
    assert not v.keep
    assert len(v.reason) > 20  # a stated reason, not a bare flag


def test_refused_come_first():
    catalog = [_garment(gid="k", color="#C1553B", name="Kept"),
               _garment(gid="r", color="#1a2aff", name="Refused")]
    verdicts = judge_catalog(_warm_profile(), catalog)
    assert verdicts[0].garment_id == "r"
    assert verdicts[1].garment_id == "k"


def test_judgement_is_deterministic():
    g = _garment()
    a, b = judge(_warm_profile(), g), judge(_warm_profile(), g)
    assert (a.score, a.keep, a.reason) == (b.score, b.keep, b.reason)


def test_demo_profile_scores_sensibly():
    from app.catalog import CATALOG
    verdicts = judge_catalog(DEMO_PROFILE, CATALOG)
    kept = [v for v in verdicts if v.keep]
    refused = [v for v in verdicts if not v.keep]
    assert kept and refused  # advisor both keeps AND refuses
    assert all(0 <= v.score <= 100 for v in verdicts)
