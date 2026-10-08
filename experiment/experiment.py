from Module.hotelsystem import HotelSystem
import tracemalloc
import time

def build_guest_id(n, c):
    """
        ยังไม่รองรับกรณีหารไม่ลงตัว
    """
    each_c = n // c
    res = []
    for i in range(1 , c+1):
        for j in range(each_c):
                    #   c   s
            res.append((i , j))
    
    return res


def experiment_1():
    print("Experiment 1 : ")
    K = [1000 , 10000 , 100000]
    N = 10
    V = 32
    res = []    
    #consistent_hash
    for k in K:        
        system = HotelSystem()
        guest_id_list = build_guest_id(k , 10)
        system.set_vnode_size(V)
        for i in range(0,N+1):
            system.add_building(i+1)

        
        tracemalloc.start()
        start_time = time.perf_counter()
        for guest in guest_id_list:
            system.add_guest_single(guest[0],guest[1])
        '''
            ทำการทดลอง
            - จัดแขก
            - ค้นหา
            - เรียงลำดับ
            - หน่วยความจำ

        '''
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.perf_counter()
        total_time = end_time - start_time
    
    #hash_mod_n
    for k in K:
        tracemalloc.start()
        start_time = time.perf_counter()
        """
            ทำการทดลอง
        """
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.perf_counter()
        total_time = end_time - start_time        
    pass

def experiment_2():
    print("Experiment 2 : ")
    N = [5,10,20]
    K = 10000
    V = 32
    #consistent_hash
    for n in N:
        system = HotelSystem()
        guest_list = build_guest_id(K , 10)

        for i in range(0,n):
            system.add_building(i+1)

        for guest in guest_list:
            system.add_guest_single(guest[0],guest[1])
        new_building_id = n+1
        start_time = time.perf_counter()

        building,add_history = system.add_building(new_building_id)
        end_time = time.perf_counter()
        total_time = end_time - start_time

        print(f"Total time for add building and migration = {total_time}")
        start_time = time.perf_counter()
        building,remove_history = system.remove_building(new_building_id)
        end_time = time.perf_counter()
        total_time = end_time - start_time

        print(f"Total time for remove building and migration = {total_time}")
        """
            ทำการทดลอง
        """
        for i in add_history:
            print(i)
        for i in remove_history:
            print(i)
    #hash_mod_n
    for n in N:
        tracemalloc.start()
        start_time = time.perf_counter()
        """
            ทำการทดลอง
        """
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.perf_counter()
        total_time = end_time - start_time     
    pass

def experiment_3():
    print("Experiment 3 : ")
    V = [1,8,32]
    N = 10
    K = 10000
    #consistent_hash
    for v in V:
        system = HotelSystem()
        system.set_vnode_size = v
        for i in range(N):
            system.add_building(i+1)
        guest_list = build_guest_id(K)

        for guest in guest_list:
            system.add_guest_single(guest[0],guest[1])

        system.show_load_balance_report()


    #hash_mod_n
    for v in V:
        tracemalloc.start()
        start_time = time.perf_counter()
        """
            ทำการทดลอง
        """
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.perf_counter()
        total_time = end_time - start_time     
    return 