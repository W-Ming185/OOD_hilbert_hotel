from Module import HotelCLI
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
    K = [1000 , 10000 , 100000]
    N = 10
    V = 32
    res = []    
    #consistent_hash
    for k in K:        
        system = HotelCLI()
        guest_id_list = build_guest_id(k , 10)
        tracemalloc.start()
        start_time = time.perf_counter()
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
    N = [5,10,20]
    K = 10000
    V = 32
    #consistent_hash
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
    V = [1,8,32]
    N = 10
    K = 10000
    #consistent_hash
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