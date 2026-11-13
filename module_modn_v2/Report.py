from __future__ import annotations

from decimal import Decimal, getcontext

from .Building import Building


class Report:
    @staticmethod
    def load_balance(buildings: list[Building], guest_count: int) -> dict:
        counts = [(b.get_node_id, len(b.get_RoomAddr)) for b in buildings]
        if guest_count == 0:
            return {"counts": counts, "min": 0, "max": 0, "mean": Decimal(0),
                    "sd": Decimal(0), "cv": None, "total": 0}
        if not counts:
            raise ValueError("Cannot report guests without buildings")
        getcontext().prec = 8
        mean = Decimal(guest_count) / Decimal(len(counts))
        variance = sum((Decimal(count) - mean) ** 2 for _, count in counts) / Decimal(len(counts))
        sd = variance.sqrt()
        return {"counts": counts, "min": min(n for _, n in counts), "max": max(n for _, n in counts),
                "mean": mean, "sd": sd, "cv": sd / mean if mean else None, "total": guest_count}
