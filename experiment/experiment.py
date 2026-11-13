import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root
 
import io
import time
import statistics
import tracemalloc
import contextlib
import matplotlib.pyplot as plt
 
from Module.hotelsystem import HotelSystem as ConsistentSystem
from module_modn_v2.hotelsystem import HotelSystem as ModNSystem
 
# ==========================================
# SETTINGS  (change these to change the graph)
# ==========================================
SALTS = ["0", "1", "2"]          # 3 rounds, same salt for both methods (brief section 7.1)
CHANNELS = 10
LOG_X = True                      # log scale on the K axis (graph A)
LOG_Y = True                      # log scale on the Y axis (graph A, memory + time) -> pattern is easier to see
SHOW_BAND = True                  # min-max band around the median
 
METHODS = {                       # name -> (class, colour)
    "consistent": (ConsistentSystem, "tab:blue"),
    "mod n":      (ModNSystem,       "tab:orange"),
}
 
# ==========================================
# HELPERS
# ==========================================
def build_guest_id(n, c):
    each_c = n // c
    left_over = n % c
    res = []
    for i in range(1 , c+1):
        for j in range(each_c):
            res.append((i , j + 1))
        if left_over > 0:
            res.append((i , each_c + 1))
            left_over-=1
    return res
 
def make_system(cls, salt, v):
    system = cls()
    system.set_salt(salt)
    system.set_vnode_size(v)
    return system
 
def fill(system, n, guest_ids):
    for i in range(n):
        system.add_building(i+1)
    for c, s in guest_ids:
        system.add_guest_single(c, s)
 
def quiet(func, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return func(*args)
 
def calc_building(system, h):
    if hasattr(system, "ring") and system.ring is not None:
        return system.ring.get_vnode_for_guest(h)
    return system.hashmod.get_building_for_guest(h)
 
def cv_of(system, show=False):
    if show:
        res = system.show_load_balance_report()      # prints the report
    else:
        res = quiet(system.show_load_balance_report)
    counts = [float(x[1]) for x in res] if res else []
    if not counts or sum(counts) == 0:
        return 0.0
    mean = sum(counts) / len(counts)
    sd = (sum((x - mean) ** 2 for x in counts) / len(counts)) ** 0.5
    return sd / mean
 
def memory_run(cls, salt, n, v, guest_ids):
    """Memory is measured in its OWN run (tracemalloc slows the code, so no timing here)."""
    tracemalloc.start()
    system = make_system(cls, salt, v)
    fill(system, n, guest_ids)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current / (1024 * 1024), peak / (1024 * 1024), system
 
def stat(values):
    return statistics.median(values), min(values), max(values)
 
def plot_lines(ax, x, series, title, xlabel, ylabel, logx=False, logy=False):
    """series = {method: [(median, min, max) per x]}"""
    for name, pts in series.items():
        color = METHODS[name][1]
        med = [p[0] for p in pts]
        ax.plot(x, med, marker='o', label=name, color=color)
        if SHOW_BAND:
            ax.fill_between(x, [p[1] for p in pts], [p[2] for p in pts], color=color, alpha=0.2)
    if logx:
        ax.set_xscale('log'); ax.set_xticks(x); ax.set_xticklabels([f"{v:,}" for v in x])
        ax.minorticks_off()
    if logy:
        ax.set_yscale('log')
    else:
        ax.set_ylim(bottom=0)   # start at 0 so tiny differences are not exaggerated
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='-', alpha=0.3)
    ax.legend()
 
# ==========================================
# EXPERIMENT 1 : A = time / memory vs K   (N=10, V=32)
# ==========================================
def experiment_1():
    print("\nExperiment 1 : ")
    K = [1000 , 10000 , 100000]
    N, V = 10, 32
    keys = ['build_routing', 'assign_guests', 'guest_search', 'room_search', 'calc_building', 'peak_memory']
    metrics = {name: {key: [] for key in keys} for name in METHODS}
 
    for k in K:
        guest_ids = build_guest_id(k, CHANNELS)
        for name, (cls, _) in METHODS.items():
            exp_start = time.perf_counter()
            rows = {key: [] for key in keys}
            for salt in SALTS:
                system = make_system(cls, salt, V)
 
                start = time.perf_counter()
                for i in range(N):
                    system.add_building(i+1)
                rows['build_routing'].append((time.perf_counter() - start) * 1000)
 
                start = time.perf_counter()
                for c, s in guest_ids:
                    system.add_guest_single(c, s)
                rows['assign_guests'].append((time.perf_counter() - start) * 1000)
 
                search_n = min(1000, k)
                start = time.perf_counter()
                for i in range(search_n):
                    system.search_guest_location(guest_ids[i])
                rows['guest_search'].append((time.perf_counter() - start) / search_n * 1_000_000)
 
                # real (building, room) pairs that exist in the system
                pairs = [(g.get_room.node_id, g.get_room.room_no) for g in system.guest[:search_n]]
                start = time.perf_counter()
                for node_id, room_no in pairs:
                    system.search_guest_by_room_id_and_building_id(node_id, room_no)
                rows['room_search'].append((time.perf_counter() - start) / search_n * 1_000_000)
 
                hashes = [g.get_hash_value for g in system.guest[:search_n]]
                start = time.perf_counter()
                for h in hashes:
                    calc_building(system, h)
                rows['calc_building'].append((time.perf_counter() - start) / search_n * 1_000_000)
 
                _, peak, _ = memory_run(cls, salt, N, V, guest_ids)   # separate run
                rows['peak_memory'].append(peak)
 
            for key in keys:
                metrics[name][key].append(stat(rows[key]))
            elapsed = time.perf_counter() - exp_start
            print(f"Done Exp 1: K={k} | {name} | Memory={metrics[name]['peak_memory'][-1][0]:.4f} MiB | Time={elapsed:.2f} s")
 
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle(f"A: Time vs K; N={N}, V={V}, {CHANNELS} channels\nsalts={','.join(SALTS)}; median with min-max band; memory measured in a separate run", fontsize=14)
    specs = [('build_routing', "Build routing", "ms"), ('assign_guests', "Assign guests", "ms"),
             ('guest_search', "Guest search", "μs per search"), ('room_search', "Room search", "μs per search"),
             ('calc_building', "Calculate building", "μs per calculation"), ('peak_memory', "Peak Python memory", "MiB")]
    for ax, (key, title, unit) in zip(axes.flat, specs):
        plot_lines(ax, K, {n: metrics[n][key] for n in METHODS}, title, 'Guest count K', unit, LOG_X, LOG_Y)
    plt.tight_layout()
    plt.savefig('graph_A_time_vs_K.png', dpi=200)
    plt.close(fig)
    print("-> Saved Graph A (graph_A_time_vs_K.png)")
 
# ==========================================
# EXPERIMENT 2 : B = migration vs N   (K=10000, V=32)
# ==========================================
def experiment_2():
    print("\nExperiment 2 : ")
    N = [5, 10, 20]
    K, V = 10000, 32
    guest_ids = build_guest_id(K, CHANNELS)
    res = {name: {a: {'pct': [], 'ms': []} for a in ("add", "remove")} for name in METHODS}
 
    for n in N:
        for name, (cls, _) in METHODS.items():
            rows = {a: {'pct': [], 'ms': []} for a in ("add", "remove")}
            for salt in SALTS:
                # add building N -> N+1
                system = make_system(cls, salt, V)
                fill(system, n, guest_ids)
                start = time.perf_counter()
                _, history = system.add_building(n + 1)
                rows["add"]['ms'].append((time.perf_counter() - start) * 1000)
                rows["add"]['pct'].append((len(history) if history else 0) / K * 100)
                # remove building N -> N-1 (building 1, fresh system)
                system = make_system(cls, salt, V)
                fill(system, n, guest_ids)
                start = time.perf_counter()
                _, history = system.remove_building(1)
                rows["remove"]['ms'].append((time.perf_counter() - start) * 1000)
                rows["remove"]['pct'].append((len(history) if history else 0) / K * 100)
            for a in ("add", "remove"):
                for m in ('pct', 'ms'):
                    res[name][a][m].append(stat(rows[a][m]))
            print(f"N={n} | {name:10s} | add moved {res[name]['add']['pct'][-1][0]:.2f}% | remove moved {res[name]['remove']['pct'][-1][0]:.2f}%")
 
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(f"B: Migration; K={K}, V={V}, {CHANNELS} channels\nsalts={','.join(SALTS)}; median with min-max band", fontsize=14)
    for col, a in enumerate(("add", "remove")):
        plot_lines(axes[0][col], N, {n: res[n][a]['pct'] for n in METHODS}, f"{a} one building", 'Original building count N', 'Migrated guests (%)')
        plot_lines(axes[1][col], N, {n: res[n][a]['ms'] for n in METHODS}, f"{a} one building (time)", 'Original building count N', 'ms')
    if LOG_Y:
        for ax in axes[1]:
            ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig('graph_B_migration_vs_N.png', dpi=200)
    plt.close(fig)
    print("-> Saved Graph B (graph_B_migration_vs_N.png)")
 
# ==========================================
# EXPERIMENT 3 : C = effect of V   (N=10, K=10000)
# ==========================================
def experiment_3():
    print("\nExperiment 3 : ")
    V = [1, 8, 32]
    N, K = 10, 10000
    guest_ids = build_guest_id(K, CHANNELS)
    keys = ['cv', 'current', 'peak', 'migration']
    res = {name: {k: [] for k in keys} for name in METHODS}
 
    for v in V:
        for name, (cls, _) in METHODS.items():
            rows = {k: [] for k in keys}
            for salt in SALTS:
                current, peak, system = memory_run(cls, salt, N, v, guest_ids)
                rows['current'].append(current)
                rows['peak'].append(peak)
                print(f"\n=== Load balance report | {name} | V={v} | salt={salt} ===")
                rows['cv'].append(cv_of(system, show=True))
                _, history = system.add_building(N + 1)
                rows['migration'].append((len(history) if history else 0) / K * 100)
            for k in keys:
                res[name][k].append(stat(rows[k]))
            print(f"V={v} | {name:10s} | CV={res[name]['cv'][-1][0]:.4f} | Current={res[name]['current'][-1][0]:.4f} MiB | Peak={res[name]['peak'][-1][0]:.4f} MiB | add moved {res[name]['migration'][-1][0]:.2f}%")
 
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(f"C: Effect of V; N={N}, K={K}, {CHANNELS} channels\nsalts={','.join(SALTS)}; median with min-max band\nmod n has no virtual node, so it does not change with V (reference line)", fontsize=13)
    specs = [('cv', "Load imbalance", "CV (stddev / mean)"), ('migration', "Migration when adding 1 building", "Migrated guests (%)"),
             ('current', "Current Python memory", "MiB"), ('peak', "Peak Python memory", "MiB")]
    for ax, (key, title, unit) in zip(axes.flat, specs):
        plot_lines(ax, V, {n: res[n][key] for n in METHODS}, title, 'Virtual nodes per building V', unit)
    plt.tight_layout()
    plt.savefig('graph_C_effect_of_V.png', dpi=200)
    plt.close(fig)
    print("-> Saved Graph C (graph_C_effect_of_V.png)")
 
if __name__ == "__main__":
    experiment_1()
    experiment_2()
    experiment_3()
    print("\nFinish! Check graph_A_time_vs_K.png, graph_B_migration_vs_N.png, graph_C_effect_of_V.png")
 