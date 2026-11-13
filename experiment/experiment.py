from Module.hotelsystem import HotelSystem
import tracemalloc
import time
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# ส่วนของฟังก์ชันวาดกราฟ (เฉพาะ Consistent Hashing แบบ Grid)
# ==========================================
def plot_graph_a_grid(K_values, metrics, n_param=10, v_param=32):
    """
    สร้างกราฟ A แบบ 2x3 Grid ตามภาพอ้างอิง image.png
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle(f"A: Time vs K; N={n_param}, V={v_param}, 10 channels\nconsistent: HotelSystem", fontsize=14)

    # กำหนดหัวข้อและหน่วยของแต่ละแกน
    titles = ["Build routing", "Assign guests", "Sort rooms", "Guest Search", "Room Search", "Calculate building"]
    y_labels = ["ms", "ms", "ms", "μs per search", "μs per search", "μs per calculation"]
    keys = ['build_routing', 'assign_guests', 'sort_rooms', 'guest_search', 'room_search', 'calc_building']

    for i, ax in enumerate(axes.flat):
        key = keys[i]
        if key in metrics and len(metrics[key]) == len(K_values):
            # วาดเฉพาะเส้น Consistent Hashing (สีฟ้า)
            ax.plot(K_values, metrics[key], marker='o', label='consistent', color='tab:blue')
        else:
            # ถ้าไม่มีข้อมูลให้ใส่ 0 ไว้เพื่อไม่ให้กราฟพัง
            ax.plot(K_values, [0]*len(K_values), marker='o', label='consistent', color='tab:blue')
            
        ax.set_title(titles[i])
        ax.set_xlabel('Guest count K')
        ax.set_ylabel(y_labels[i])
        ax.grid(True, linestyle='-', alpha=0.3)
        ax.legend()

    plt.tight_layout()
    plt.savefig('graph_A_time_vs_K.png', dpi=300)
    print("-> Saved Graph A (graph_A_time_vs_K.png)")

def plot_graph_b_grid(N_values, add_rates, remove_rates, k_param=10000, v_param=32):
    """
    สร้างกราฟ B แบบ 1x2 Grid ตามภาพอ้างอิง imageb.png
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"B: Migration; K=[{k_param}], V={v_param}, 10 channels\nconsistent: HotelSystem", fontsize=14)

    # กราฟย่อยซ้าย: Add
    ax1.plot(N_values, add_rates, marker='o', label='consistent', color='tab:blue')
    ax1.set_title('add', fontsize=14)
    ax1.set_xlabel('Original building count N')
    ax1.set_ylabel('Migrated guests (%)')
    ax1.grid(True, linestyle='-', alpha=0.3)
    ax1.legend()

    # กราฟย่อยขวา: Remove
    ax2.plot(N_values, remove_rates, marker='o', label='consistent', color='tab:blue')
    ax2.set_title('remove', fontsize=14)
    ax2.set_xlabel('Original building count N')
    ax2.set_ylabel('Migrated guests (%)')
    ax2.grid(True, linestyle='-', alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig('graph_B_migration_vs_N.png', dpi=300)
    print("-> Saved Graph B (graph_B_migration_vs_N.png)")

def plot_graph_c_grid(V_values, cv_cons, current_cons, peak_cons,
                      cv_mod=None, current_mod=None, peak_mod=None,
                      n_param=10, k_param=10000):
    """
    สร้างกราฟ C แบบ 1x3 Grid ตามภาพอ้างอิง C
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"C: Effect of V; N={n_param}, K=[{k_param}], 10 channels\nsalts=0,1,2; median with min-max band\nconsistent: HotelSystem; modulo: hash mod N baseline", fontsize=14)

    # 1. Load imbalance (CV)
    axes[0].plot(V_values, cv_cons, marker='o', label='consistent', color='tab:blue')
    if cv_mod: axes[0].plot(V_values, cv_mod, marker='o', label='modulo', color='tab:orange')
    axes[0].set_title('Load imbalance', fontsize=14)
    axes[0].set_xlabel('Virtual nodes per building V')
    axes[0].set_ylabel('CV (stddev / mean)')
    axes[0].grid(True, linestyle='-', alpha=0.3)
    axes[0].legend()

    # 2. Current Python memory
    axes[1].plot(V_values, current_cons, marker='o', label='consistent', color='tab:blue')
    if current_mod: axes[1].plot(V_values, current_mod, marker='o', label='modulo', color='tab:orange')
    axes[1].set_title('Current Python memory', fontsize=14)
    axes[1].set_xlabel('Virtual nodes per building V')
    axes[1].set_ylabel('MiB')
    axes[1].grid(True, linestyle='-', alpha=0.3)
    axes[1].legend()

    # 3. Peak Python memory
    axes[2].plot(V_values, peak_cons, marker='o', label='consistent', color='tab:blue')
    if peak_mod: axes[2].plot(V_values, peak_mod, marker='o', label='modulo', color='tab:orange')
    axes[2].set_title('Peak Python memory', fontsize=14)
    axes[2].set_xlabel('Virtual nodes per building V')
    axes[2].set_ylabel('MiB')
    axes[2].grid(True, linestyle='-', alpha=0.3)
    axes[2].legend()

    plt.tight_layout()
    plt.savefig('graph_C_effect_of_V.png', dpi=300)
    print("-> Saved Graph C (graph_C_effect_of_V.png)")

def experiment_3():
    print("\nExperiment 3 : ")
    V = [1, 8, 32]
    N = 10
    K = 10000
    
    cv_list = []
    current_list = []
    peak_list = []

    salt = input("Enter Salt (Exp 3): ")

    for v in V:
        tracemalloc.start()
        system = HotelSystem()
        if hasattr(system, 'set_salt'):
            system.set_salt(salt)
        system.set_vnode_size(v)
        
        for i in range(N):
            system.add_building(i+1)

        guest_list = build_guest_id(K, 10)
        for guest in guest_list:
            system.add_guest_single(guest[0], guest[1])

        res = system.show_load_balance_report()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        current_list.append(current / (1024 * 1024))
        peak_list.append(peak / (1024 * 1024))
        
        guest_counts = [float(item[1]) for item in res] if res else []
        if guest_counts:
            mean_val = sum(guest_counts) / len(guest_counts)
            sum_squared = sum((x - mean_val) ** 2 for x in guest_counts)
            sd_val = (sum_squared / len(guest_counts)) ** 0.5
            cv_val = sd_val / mean_val if mean_val > 0 else 0
        else:
            cv_val = 0
            
        cv_list.append(cv_val)
        print(f"V={v} | CV={cv_val:.4f} | Current Memory={current_list[-1]:.4f} MiB | Peak Memory={peak_list[-1]:.4f} MiB")

    # เรียกวาดกราฟ C แบบ 3 ช่องแนวนอน
    plot_graph_c_grid(V, cv_list, current_list, peak_list, n_param=N, k_param=K)
# ==========================================
# ส่วนของการทดลอง
# ==========================================
def build_guest_id(n, c):
    each_c = n // c
    left_over = n % c
    res = []
    for i in range(1 , c+1):
        for j in range(each_c):
            res.append((i , j)) 
        if left_over > 0:
            res.append((i , each_c))
            left_over-=1
    return res

def experiment_1():
    print("\nExperiment 1 : ")
    K = [1000 , 10000 , 100000]
    N = 10
    V = 32
    
    metrics = {
        'build_routing': [], 'assign_guests': [], 'sort_rooms': [], 
        'guest_search': [], 'room_search': [], 'calc_building': []
    }
    
    salt = input("Enter Salt (Exp 1): ")
    
    for k in K:        
        tracemalloc.start()
        system = HotelSystem()
        if hasattr(system, 'set_salt'):
            system.set_salt(salt)
        guest_id_list = build_guest_id(k , 10)
        system.set_vnode_size(V)
        
        # 1. Build routing (ms)
        start = time.perf_counter()
        for i in range(0, N):
            system.add_building(i+1)
        metrics['build_routing'].append((time.perf_counter() - start) * 1000)

        # 2. Assign guests (ms) - จัดแขกเข้าตึก
        start = time.perf_counter()
        for guest in guest_id_list:
            system.add_guest_single(guest[0], guest[1])
        metrics['assign_guests'].append((time.perf_counter() - start) * 1000)
        
        # 3. Sort rooms (ms) 
        # ระบบของคุณใช้ bisect.insort ตอน Add room ไปแล้ว ทำให้รายชื่อห้องถูก Sort ไว้ตลอดเวลา 
        # ดังนั้นเวลาที่ใช้ Sort จึงเป็น 0 (เพราะไม่ต้องทำอะไรเพิ่ม)
        metrics['sort_rooms'].append(0) 

        # 4. Guest Search (μs)
        search_count = min(1000, len(guest_id_list))
        start = time.perf_counter()
        for i in range(1000):
            system.search_guest_location(guest_id_list[i])
        metrics['guest_search'].append(((time.perf_counter() - start) / search_count) * 1_000_000)
        
        # 5. Room Search (μs) - จับเวลาค้นหาแขกจาก Building ID และ Room No
        # ดึงห้องแรกของตึกแรกมาลองค้นหา
        test_building_id = 1
        test_room_no = 1 
        start = time.perf_counter()
        for i in range(search_count):
            system.search_guest_by_room_id_and_building_id(test_building_id, test_room_no)
        metrics['room_search'].append(((time.perf_counter() - start) / search_count) * 1_000_000)
        
        # 6. Calculate building (μs) - จับเวลาหา Vnode เป้าหมายจาก Hash (การทำงานของวงแหวน)
        test_hash = 123456789
        start = time.perf_counter()
        for i in range(search_count):
            system.ring.get_vnode_for_guest(test_hash)
        metrics['calc_building'].append(((time.perf_counter() - start) / search_count) * 1_000_000)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Done Exp 1: K={k} | Memory={peak/(1024*1024):.4f} MiB")

    plot_graph_a_grid(K, metrics, n_param=N, v_param=V)

def experiment_2():
    print("\nExperiment 2 : ")
    N = [5, 10, 20]
    K = 10000
    V = 32
    
    # แยกเก็บ Add และ Remove (เป็นเปอร์เซ็นต์ %)
    add_rates_pct = []
    remove_rates_pct = []
    
    salt = input("Enter Salt (Exp 2): ")
    for n in N:
        system = HotelSystem()
        if hasattr(system, 'set_salt'):
            system.set_salt(salt)
        system.set_vnode_size(V)
        guest_list = build_guest_id(K , 10)

        for i in range(0,n):
            system.add_building(i+1)
        for guest in guest_list:
            system.add_guest_single(guest[0],guest[1])
            
        new_building_id = n+1

        # จำลอง Add Building
        building, add_history = system.add_building(new_building_id)
        num_added = len(add_history) if add_history else 0
        add_rates_pct.append((num_added / K) * 100) # แปลงเป็น %

        # จำลอง Remove Building
        building, remove_history = system.remove_building(new_building_id)
        num_removed = len(remove_history) if remove_history else 0
        remove_rates_pct.append((num_removed / K) * 100) # แปลงเป็น %

        print(f"N={n} -> {n+1} | Addย้าย: {num_added}คน ({add_rates_pct[-1]:.2f}%) | Removeย้าย: {num_removed}คน ({remove_rates_pct[-1]:.2f}%)")

    # เรียกวาดกราฟ B แบบ 2 ช่อง ซ้าย-ขวา
    plot_graph_b_grid(N, add_rates_pct, remove_rates_pct, k_param=K, v_param=V)

def experiment_3():
    print("\nExperiment 3 : ")
    V = [1, 8, 32]
    N = 10
    K = 10000
    
    cv_list = []
    # เปลี่ยนจาก memory_list เป็น 2 ตัวนี้ครับ
    current_list = []
    peak_list = []

    salt = input("Enter Salt (Exp 3): ")

    for v in V:
        tracemalloc.start()
        system = HotelSystem()
        if hasattr(system, 'set_salt'):
            system.set_salt(salt)
        system.set_vnode_size(v)
        
        for i in range(N):
            system.add_building(i+1)

        guest_list = build_guest_id(K, 10)
        for guest in guest_list:
            system.add_guest_single(guest[0], guest[1])

        res = system.show_load_balance_report()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # เก็บค่าแยกกันทั้ง 2 ตัว
        current_list.append(current / (1024 * 1024))
        peak_list.append(peak / (1024 * 1024))
        
        guest_counts = [float(item[1]) for item in res] if res else []
        if guest_counts:
            mean_val = sum(guest_counts) / len(guest_counts)
            sum_squared = sum((x - mean_val) ** 2 for x in guest_counts)
            sd_val = (sum_squared / len(guest_counts)) ** 0.5
            cv_val = sd_val / mean_val if mean_val > 0 else 0
        else:
            cv_val = 0
            
        cv_list.append(cv_val)
        print(f"V={v} | CV={cv_val:.4f} | Current Memory={current_list[-1]:.4f} MiB | Peak Memory={peak_list[-1]:.4f} MiB")

    # เรียกฟังก์ชันแบบ 3 ช่อง
    plot_graph_c_grid(V, cv_list, current_list, peak_list, n_param=N, k_param=K)

if __name__ == "__main__":
    experiment_1()
    experiment_2()
    experiment_3()
    print("\nFinish! ตรวจสอบไฟล์รูปกราฟ (graph_A_time_vs_K.png และ graph_B_migration_vs_N.png) ได้เลยครับ")