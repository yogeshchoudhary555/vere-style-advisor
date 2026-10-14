"""Session budget tracker: every API call is a line item, in units."""

from __future__ import annotations

import threading


class Budget:
    """Tracks units spent per action for the demo session.

    Costs come from the live feature-cost API when a key is configured;
    otherwise documented fallback costs are used and flagged as estimates.
    """

    # Documented unit costs (from the official API reference / skills repo).
    FALLBACK_COSTS = {
        "skin-tone-analysis": 20,
        "cloth-v4": 35,  # estimate until the live cost API is queried
    }

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.lines: list[dict] = []
        self.live_costs: dict[str, int] = {}
        self.estimated: bool = True

    def set_live_costs(self, costs: dict[str, int]) -> None:
        with self._lock:
            self.live_costs = {k: v for k, v in costs.items() if k in self.FALLBACK_COSTS}
            self.estimated = False

    def cost_of(self, action: str) -> tuple[int, bool]:
        """Return (units, is_estimate) for one call of an action."""
        with self._lock:
            if action in self.live_costs:
                return self.live_costs[action], False
            return self.FALLBACK_COSTS.get(action, 0), True

    def spend(self, action: str, detail: str = "") -> dict:
        units, estimated = self.cost_of(action)
        with self._lock:
            line = {"action": action, "units": units, "estimated": estimated,
                    "detail": detail, "n": len(self.lines) + 1}
            self.lines.append(line)
            return line

    def total(self) -> int:
        with self._lock:
            return sum(l["units"] for l in self.lines)

    def summary(self) -> dict:
        with self._lock:
            return {"lines": list(self.lines),
                    "total_units": sum(l["units"] for l in self.lines),
                    "estimated": self.estimated}
