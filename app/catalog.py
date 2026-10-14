"""Garment catalog for the VÉRÉ Style Advisor demo store."""

from __future__ import annotations

from app.advisor import Garment

# warmth is computed from color_hex at serve time if set to 0.0; values below are
# explicit overrides for readability of the rules.
CATALOG: list[Garment] = [
    Garment(
        garment_id="g1",
        name="Terracotta Silk Blouse",
        category="upper_body",
        color_hex="#C1553B",
        warmth=0.7,
        pattern="solid",
        sheen="satin",
        image="/static/assets/garment_g1.png",
    ),
    Garment(
        garment_id="g2",
        name="Midnight Navy Blazer",
        category="upper_body",
        color_hex="#1F2A44",
        warmth=-0.5,
        pattern="solid",
        sheen="matte",
        image="/static/assets/garment_g2.png",
    ),
    Garment(
        garment_id="g3",
        name="Emerald Satin Dress",
        category="full_body",
        color_hex="#0E7C5B",
        warmth=-0.2,
        pattern="solid",
        sheen="shine",
        image="/static/assets/garment_g3.png",
    ),
    Garment(
        garment_id="g4",
        name="Mustard Knit Sweater",
        category="upper_body",
        color_hex="#D9A441",
        warmth=0.8,
        pattern="solid",
        sheen="matte",
        image="/static/assets/garment_g4.png",
    ),
    Garment(
        garment_id="g5",
        name="Crimson Paisley Scarf",
        category="outer",
        color_hex="#B81E3A",
        warmth=0.5,
        pattern="bold",
        sheen="matte",
        image="/static/assets/garment_g5.png",
    ),
    Garment(
        garment_id="g6",
        name="Charcoal Wool Coat",
        category="outer",
        color_hex="#3A3A3E",
        warmth=0.0,
        pattern="solid",
        sheen="matte",
        image="/static/assets/garment_g6.png",
    ),
    Garment(
        garment_id="g7",
        name="Ivory Linen Shirt",
        category="upper_body",
        color_hex="#EFE6D5",
        warmth=0.2,
        pattern="solid",
        sheen="matte",
        image="/static/assets/garment_g7.png",
    ),
    Garment(
        garment_id="g8",
        name="Royal Indigo Kurta",
        category="upper_body",
        color_hex="#2B3A9B",
        warmth=-0.6,
        pattern="subtle",
        sheen="matte",
        image="/static/assets/garment_g8.png",
    ),
]

BY_ID = {g.garment_id: g for g in CATALOG}
