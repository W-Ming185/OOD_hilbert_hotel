# module_modn_v2

Standalone v2 implementation. It has no imports from the original `module_modn` package.

From the project root, start the interactive program. It asks for N, channel count, and each channel's guest count. Initial building IDs are 1 through N, in that order.

```console
python -m module_modn_v2.HotelCLI
```

The package requires Python 3.10 or newer. A minimal non-interactive example:

```python
from module_modn_v2 import HotelSystem

hotel = HotelSystem()
hotel.add_building(1)
hotel.add_guest_single(3, 10)
print(hotel.search_guest_location(3, 10))
```

Run the brief-based correctness checks from the project root with:

```console
python -m unittest module_modn_v2.test_module_modn_v2 -v
```

Run the Mod-N part of experiment sets A/B, write raw values plus three-round median/min/max summaries, and create the Mod-N graphs:

```console
python -m module_modn_v2.experiment_modn
```

The default output folder is `module_modn_v2/experiment_results`. `modn_experiment_raw.csv` records each salt round; `modn_experiment_summary.csv` reports medians and min/max for A/B; `modn_experiment_C_baseline.csv` and `_summary.csv` provide Mod-N's N=10, K=10,000 load/memory/migration baseline. Three SVG graphs show assignment/listing time, memory, and migration rate. Each round records its salt (`0`, `1`, or `2`). Timing uses `time.perf_counter`; search timing averages 1,000 lookups. Current and peak Python-tracked memory are measured in a separate run with `tracemalloc`. Set C's V sweep is not applicable to Mod-N because this method has no virtual nodes; the C baseline explicitly marks V as not applicable. Cross-method comparison with consistent hashing is performed by the separate consistent-hashing implementation.

This package is the Mod-N implementation only. It selects `buildings[H(guest) % N]` using a stable SHA-256 64-bit guest hash, a salt, and building insertion order. Adding a building appends it; removing one preserves the order of the remaining buildings. After either change it recalculates all assignments and records moved guest IDs, old/new building IDs, and stable room numbers. Guest IDs are positive integers; duplicate guest IDs are rejected. Batch inserts check the full requested range before inserting any guest.

## Mod-N cost notes

Assuming integer/hash comparisons take constant time, selecting a building is O(1). Adding one guest is O(K + R), where K is the sorted guest list length and R is the selected building's sorted room list, due to list insertion. Guest lookup is O(log K); room lookup is O(log R). Removing a guest is O(K + R). A batch of B guests checks duplicates in O(B), then sorts the combined guest list in O((K+B) log(K+B)) and each destination building's room list in O(R_i log R_i). A building change recalculates destinations for all K guests in O(K), filters old room lists in O(K), then sorts changed destination room lists; its worst case is O(K log K). The number of actual moves can range from 0 to K. Building IDs use O(N) space and guest/room records use O(K); batch/migration operations use O(K+B) temporary space. These are bounds for this implementation, not the consistent-hashing implementation.
