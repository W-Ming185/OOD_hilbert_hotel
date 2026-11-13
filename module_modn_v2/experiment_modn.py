"""Reproducible Mod-N experiment set A/B from section 7 of the project brief."""

from __future__ import annotations

import argparse
import csv
import gc
import html
import statistics
import time
import tracemalloc
from collections import defaultdict
from pathlib import Path

from .hotelsystem import HotelSystem


SALTS = ("0", "1", "2")
SIZE_CASES = (1_000, 10_000, 100_000)
BUILDING_CASES = (5, 10, 20)
CHANNELS = 10


def _initial_guest_count(k: int, channel_id: int) -> int:
    base, remainder = divmod(k, CHANNELS)
    return base + (1 if channel_id <= remainder else 0)


def populate_modn(n: int, k: int, salt: str) -> HotelSystem:
    hotel = HotelSystem(salt=salt)
    for node_id in range(1, n + 1):
        hotel.add_building(node_id)
    for channel_id in range(1, CHANNELS + 1):
        count = _initial_guest_count(k, channel_id)
        if count:
            hotel.add_guest_batch(channel_id, 1, count)
    return hotel


def measure_memory(n: int, k: int, salt: str) -> tuple[float, float]:
    gc.collect()
    tracemalloc.start()
    hotel = populate_modn(n, k, salt)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    # Keep the local reference alive through both measurements.
    assert len(hotel.guest) == k
    mib = 1024 * 1024
    return current / mib, peak / mib


def run_size_case(n: int, k: int, salt: str) -> dict:
    hotel = HotelSystem(salt=salt)
    start = time.perf_counter()
    for node_id in range(1, n + 1):
        hotel.add_building(node_id)
    building_setup_seconds = time.perf_counter() - start

    start = time.perf_counter()
    for channel_id in range(1, CHANNELS + 1):
        count = _initial_guest_count(k, channel_id)
        if count:
            hotel.add_guest_batch(channel_id, 1, count)
    assign_seconds = time.perf_counter() - start

    query_ids = [guest.guest_id for guest in hotel.guest]
    start = time.perf_counter()
    for index in range(1_000):
        if hotel.search_guest_location(*query_ids[index % len(query_ids)]) == "guest_id not found":
            raise AssertionError("A generated guest could not be found")
    search_avg_seconds = (time.perf_counter() - start) / 1_000

    room_rows = [(room.node_id, room.room_no, room.guest.guest_id)
                 for room in hotel.show_occupied_room()]
    start = time.perf_counter()
    rooms = sorted(room_rows, key=lambda row: (row[0], row[1]))
    sorted_room_listing_seconds = time.perf_counter() - start
    if len(rooms) != k:
        raise AssertionError("Room listing did not return every guest")

    balance = hotel.show_load_balance_report()
    current_mib, peak_mib = measure_memory(n, k, salt)
    return {
        "experiment": "A",
        "N": n,
        "K": k,
        "salt": salt,
        "channels": CHANNELS,
        "building_setup_seconds": building_setup_seconds,
        "guest_assignment_seconds": assign_seconds,
        "search_1000_avg_seconds": search_avg_seconds,
        "sorted_room_listing_seconds": sorted_room_listing_seconds,
        "load_min": balance["min"],
        "load_max": balance["max"],
        "load_mean": float(balance["mean"]),
        "load_sd": float(balance["sd"]),
        "load_cv": float(balance["cv"]) if balance["cv"] is not None else None,
        "memory_current_mib": current_mib,
        "memory_peak_mib": peak_mib,
    }


def run_building_case(n: int, k: int, salt: str, action: str) -> dict:
    hotel = populate_modn(n, k, salt)
    start = time.perf_counter()
    if action == "add":
        hotel.add_building(n + 1)
    else:
        hotel.remove_building(1)
    elapsed = time.perf_counter() - start
    return {
        "experiment": "B",
        "N": n,
        "K": k,
        "salt": salt,
        "channels": CHANNELS,
        "action": action,
        "operation_seconds": elapsed,
        "moved_guests": hotel.last_migration_count,
        "migration_rate": float(hotel.last_migration_rate or 0),
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _summarize(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    keys = ("experiment", "N", "K", "action")
    for row in rows:
        groups[tuple(row.get(key) for key in keys)].append(row)
    summary = []
    for group, group_rows in groups.items():
        item = {key: value for key, value in zip(keys, group) if value is not None}
        item["rounds"] = len(group_rows)
        item["salts"] = ",".join(row["salt"] for row in group_rows)
        metrics = ("building_setup_seconds", "guest_assignment_seconds", "search_1000_avg_seconds",
                   "sorted_room_listing_seconds", "memory_current_mib", "memory_peak_mib",
                   "load_min", "load_max", "load_mean", "load_sd", "load_cv",
                   "operation_seconds", "moved_guests", "migration_rate")
        for metric in metrics:
            values = [row[metric] for row in group_rows if metric in row]
            if values:
                item[f"median_{metric}"] = statistics.median(values)
                item[f"min_{metric}"] = min(values)
                item[f"max_{metric}"] = max(values)
        summary.append(item)
    return summary


def _svg_chart(path: Path, title: str, caption: str, categories: list[str],
               y_label: str, series: list[tuple[str, list[float], list[float], list[float], str]]) -> None:
    """Write a dependency-free SVG line chart with median points and min/max bars."""
    width, height = 900, 520
    left, right, top, bottom = 92, 36, 92, 115
    plot_w, plot_h = width - left - right, height - top - bottom
    values = []
    parsed = series
    for _, median, minimum, maximum, _ in parsed:
        values.extend(minimum)
        values.extend(maximum)
    maximum_y = max(values, default=1.0) * 1.12
    if maximum_y <= 0:
        maximum_y = 1.0

    def y(value: float) -> float:
        return top + plot_h - value / maximum_y * plot_h

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold">{html.escape(title)}</text>',
             f'<text x="{width/2}" y="59" text-anchor="middle" font-family="Arial" font-size="13">{html.escape(caption)}</text>']
    for tick in range(6):
        value = maximum_y * tick / 5
        yy = y(value)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#d8dee8"/>')
        parts.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{value:.3g}</text>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#333"/>')
    for index, category in enumerate(categories):
        xx = left + plot_w * (index + 0.5) / max(1, len(categories))
        parts.append(f'<text x="{xx:.1f}" y="{top+plot_h+25}" text-anchor="middle" font-family="Arial" font-size="12">{html.escape(category)}</text>')
    parts.append(f'<text x="24" y="{top+plot_h/2}" transform="rotate(-90 24 {top+plot_h/2})" text-anchor="middle" font-family="Arial" font-size="14">{html.escape(y_label)}</text>')
    for series_index, (label, median, minimum, maximum, color) in enumerate(parsed):
        coords = []
        for index in range(len(categories)):
            xx = left + plot_w * (index + 0.5) / max(1, len(categories))
            yy = y(median[index])
            coords.append(f"{xx:.1f},{yy:.1f}")
            parts.append(f'<line x1="{xx:.1f}" y1="{y(minimum[index]):.1f}" x2="{xx:.1f}" y2="{y(maximum[index]):.1f}" stroke="{color}" stroke-width="2"/>')
            parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="5" fill="{color}"/>')
        parts.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        lx = left + series_index * 220
        parts.append(f'<line x1="{lx}" y1="{height-40}" x2="{lx+24}" y2="{height-40}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{lx+32}" y="{height-36}" font-family="Arial" font-size="12">{html.escape(label)} (median; min-max)</text>')
    parts.extend(['</svg>'])
    path.write_text("\n".join(parts), encoding="utf-8")


def _write_charts(summary: list[dict], output_dir: Path) -> list[Path]:
    size_rows = sorted((row for row in summary if row.get("experiment") == "A"), key=lambda row: row["K"])
    building_rows = sorted((row for row in summary if row.get("experiment") == "B"), key=lambda row: (row["action"], row["N"]))
    charts = []
    for filename, title, metric_specs, units, y_label in (
        ("modn_time_by_size.svg", "Mod-N operation time by guest count",
         [("Guest assignment", "guest_assignment_seconds", "#2563eb"),
          ("Sorted room listing", "sorted_room_listing_seconds", "#dc2626")], "seconds", "Time (seconds)"),
        ("modn_memory_by_size.svg", "Mod-N Python-tracked memory by guest count",
         [("Current memory", "memory_current_mib", "#059669"),
          ("Peak memory", "memory_peak_mib", "#7c3aed")], "MiB", "Memory (MiB)"),
    ):
        series = []
        for label, metric, color in metric_specs:
            med = [row[f"median_{metric}"] for row in size_rows]
            low = [row[f"min_{metric}"] for row in size_rows]
            high = [row[f"max_{metric}"] for row in size_rows]
            series.append((label, med, low, high, color))
        output = output_dir / filename
        _svg_chart(output, title, f"N=10, 10 channels, salts 0/1/2, median and min-max range; unit: {units}",
                   [str(row["K"]) for row in size_rows], y_label, series)
        charts.append(output)

    rate_series = []
    for action, label, color in (("add", "Add one building", "#2563eb"),
                                 ("remove", "Remove one building", "#dc2626")):
        rows = [row for row in building_rows if row["action"] == action]
        rate_series.append((label,
                            [row["median_migration_rate"] * 100 for row in rows],
                            [row["min_migration_rate"] * 100 for row in rows],
                            [row["max_migration_rate"] * 100 for row in rows], color))
    output = output_dir / "modn_migration_rate_by_buildings.svg"
    _svg_chart(output, "Mod-N guest migration rate by building count",
               "K=10,000, 10 channels, salts 0/1/2, median and min-max range; unit: percent",
               [str(n) for n in BUILDING_CASES], "Guests moved (percent of K)", rate_series)
    charts.append(output)
    return charts


def run_experiments(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_rows = []
    for k in SIZE_CASES:
        for salt in SALTS:
            raw_rows.append(run_size_case(10, k, salt))
    for n in BUILDING_CASES:
        for salt in SALTS:
            for action in ("add", "remove"):
                raw_rows.append(run_building_case(n, 10_000, salt, action))

    raw_path = output_dir / "modn_experiment_raw.csv"
    summary_path = output_dir / "modn_experiment_summary.csv"
    _write_csv(raw_path, raw_rows)
    summary_rows = _summarize(raw_rows)
    _write_csv(summary_path, summary_rows)
    c_rows = []
    for salt in SALTS:
        size_row = next(row for row in raw_rows
                        if row["experiment"] == "A" and row["K"] == 10_000 and row["salt"] == salt)
        add_row = next(row for row in raw_rows
                       if row["experiment"] == "B" and row["N"] == 10
                       and row["action"] == "add" and row["salt"] == salt)
        remove_row = next(row for row in raw_rows
                          if row["experiment"] == "B" and row["N"] == 10
                          and row["action"] == "remove" and row["salt"] == salt)
        c_rows.append({
            "experiment": "C Mod-N baseline",
            "N": 10,
            "K": 10_000,
            "V": "not applicable to Mod-N",
            "salt": salt,
            "load_min": size_row["load_min"],
            "load_max": size_row["load_max"],
            "load_mean": size_row["load_mean"],
            "load_sd": size_row["load_sd"],
            "load_cv": size_row["load_cv"],
            "memory_current_mib": size_row["memory_current_mib"],
            "memory_peak_mib": size_row["memory_peak_mib"],
            "add_moved_guests": add_row["moved_guests"],
            "add_migration_rate": add_row["migration_rate"],
            "remove_moved_guests": remove_row["moved_guests"],
            "remove_migration_rate": remove_row["migration_rate"],
        })
    _write_csv(output_dir / "modn_experiment_C_baseline.csv", c_rows)
    c_summary = _summarize(c_rows)
    for row in c_summary:
        row["V"] = "not applicable to Mod-N"
    _write_csv(output_dir / "modn_experiment_C_summary.csv", c_summary)
    _write_charts(summary_rows, output_dir)
    return raw_path, summary_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Mod-N section 7 experiment matrix")
    parser.add_argument("--output-dir", type=Path, default=Path("module_modn_v2") / "experiment_results")
    args = parser.parse_args()
    raw, summary = run_experiments(args.output_dir)
    print(f"Raw results: {raw}")
    print(f"Three-round median summary: {summary}")
    print(f"Mod-N C baseline: {args.output_dir / 'modn_experiment_C_baseline.csv'}")
    print(f"Mod-N C three-round summary: {args.output_dir / 'modn_experiment_C_summary.csv'}")
    print("V sweep is not applicable: Mod-N has no virtual-node parameter.")


if __name__ == "__main__":
    main()
