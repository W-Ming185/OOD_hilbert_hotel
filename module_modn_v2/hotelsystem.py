import hashlib
import bisect
import csv
from decimal import Decimal , getcontext

from module_modn_v2.guest import Guest
from module_modn_v2.RoomAddr import RoomAddr
from module_modn_v2.Building import Building
from module_modn_v2.class_modn import HashMod
from module_modn_v2.CSVExport import CSVExporter

class HotelSystem():
    def __init__(self):
        self.__buildings = {} 
        self.__guest = [] #list of sorted hash
        self.__guest_ids_dic = {} #dictionary contain ID of each guest
        # self.__report = Report()
        self.__hashmod = HashMod()
        self.__csvexport = CSVExporter()
        self.__salt = None 
        # self.__benchmark = BenchmarkResult()
    
    def set_salt(self,salt):
        self.__salt = salt

    @property
    def salt(self):
        return self.__salt
    @property
    def hashmod(self):
        return self.__hashmod
    @property
    def guest(self):
        return self.__guest
    
    @property
    def guest_data_list(self):
        res = []
        for i in self.__guest:
            id = i.guest_id
            room = i.get_room.room_no
            hash_value = i.get_hash_value
            node = i.get_room.node_id
            data = (id,room,hash_value,node)
            res.append(data)
        return res
    
    def set_vnode_size(self,size):
        # Mod-N has no virtual nodes : the value is only checked and then ignored
        # (kept so that the CLI and the experiment code stay exactly the same as the consistent-hashing ones)
        try:
            size = int(size)
        except:
            return 0
        return 1
    def print_guest(self):
        ls = self.guest_data_list
        print("-----------------")
        print("ID,ROOM_NO,HASH")
        #for i in ls:
            #print(i)
        print("-----------------")

    def initialize_system(self):
        pass

    def guest_dup_check(self , c , s):
        return (c, s) in self.__guest_ids_dic
    
    def hashmod_check(self):
        if self.__hashmod.get_no_building == 0:
            print("Cannot Insert Guest : No Building To Insert")
            return False
        return  True
    
    # ! ! ! No edge case yet ! ! !
    def add_guest_single(self, c , s):
        
        if not self.hashmod_check():
            return
        
        if self.guest_dup_check(c,s):
            print("This id is already exist")
            return "This id is already exist"
        id = (c,s)
        #SHA-256 Hash
        salt = self.salt
        text = f"{c}:{s}{salt}"

        hash_num = hashlib.sha256(text.encode('utf-8'))
        hash_num_64bit = hash_num.digest()[:8]

        position = int.from_bytes(hash_num_64bit, byteorder='big')

        #Choosing the building : buildings[H(guest) mod N]
        hashmod = self.hashmod
        building = hashmod.get_building_for_guest(position)
        new_guest = Guest(c,s,position)
        bisect.insort(self.__guest , new_guest , key= lambda x : x.get_hash_value)
        building.add_room(new_guest)
        #print("Add Guest Succeed")
        #self.print_guest()
        self.__guest_ids_dic[(c, s)] = new_guest
        return "Add Guest Succeed"

    def add_guest_batch(self , c , s_start , n):
        if not self.hashmod_check():
            return
        #Demo ก่อน Optimize ทีหลังได้ถ้า performance ไม่ดี
        for x in range(s_start , s_start + n):
            if self.guest_dup_check(c , x):
                print("There is some guest in this range already")
                return
        
        for x in range(s_start , s_start + n):
            self.add_guest_single(c , x)
        print("Add Batch Succeed")
        return "Add Batch Succeed"

    def remove_guest(self , c ,s):
        if not self.guest_dup_check(c,s):
            print("This id does not exist for removal")
            return "This id does not exist for removal"
            
        # ดึง Object ออกมาได้เลยแบบ O(1) ไม่ต้องวน For loop หาแล้ว
        rm_guest = self.__guest_ids_dic[(c, s)] 

        room = rm_guest.get_room
        bulding_id = room.node_id

        building = self.__buildings[bulding_id]
        building.remove_room(room.room_no)
        self.__guest.remove(rm_guest)
        del self.__guest_ids_dic[(c, s)]

        #reference clearing (จะมีไม่มีก็ได้)
        room.assign_guest(None)
        rm_guest.assign_room(None)
        self.print_guest()
        print("Removal Succeed")
        return "Removal Succeed"

    def add_building(self,node_id): #อย่าลืมmigrationnnnnnnnnnnnnnnnnnnnnn
        if node_id in self.__buildings:
            print(f"Building {node_id} already exists.")
            return None,None
        else:
            building = Building(node_id)
            self.__buildings[node_id] = building
            self.__hashmod.add_building(building)

            #Mod-N : N changed -> H(guest) mod N changes for EVERY guest, so every guest must be checked again
            affected_guest = list(self.__guest)
            history = None
            if affected_guest:
                history = self.migration(affected_guest)
            return self.__buildings,history            

    def remove_building(self,node_id): #อย่าลืมmigrationnnnnnnnnnnnnnnnnnnnnn
        
        if node_id in self.__buildings:
            if len(self.__buildings) == 1:
                print("This is The Last Building")
                return None,None
            building = self.__buildings[node_id]
            
            self.__hashmod.remove_building(building)

            #Mod-N : N changed -> every guest must be checked again (not only the guests of the removed building)
            affected_guest = list(self.__guest)
            history = None
            if affected_guest:
                history = self.migration(affected_guest)
                
            self.__buildings.pop(node_id)
            return self.__buildings,history
        else:
            print(f"{node_id} is not exist.")
            return None,None


    def search_guest_location(self,guest_id:tuple):
        if guest_id in self.__guest_ids_dic:
            i = self.__guest_ids_dic[guest_id]
            room = i.get_room
            return (room.node_id, room.room_no)
        return "guest_id not found"
        
    def migration(self,guest_list):
        history = []
        for guest in guest_list:
            room = guest.get_room
            old_node_id = room.node_id
            old_node = self.__buildings[old_node_id]
            new_node = self.__hashmod.get_building_for_guest(guest.get_hash_value)
            if new_node.get_node_id == old_node_id:
                continue    # same building -> this guest did not move
            new_node.add_room(guest)
            old_node.remove_room(room.room_no)
            history.append(f"{guest.guest_id} : {old_node_id} -> {new_node.get_node_id}")
        return history
        

    def search_guest_by_room_id_and_building_id(self,node_id , room_no):
        if node_id in self.__buildings:
            building = self.__buildings.get(node_id)
            for i in building.get_RoomAddr:
                if i.room_no == room_no:
                    room = i
                    guest = room.guest
                    id = guest.guest_id
                    print(f"Found! GuestID : {id}")
                    return id
            
            print("Cannot Find Guest : RoomNo Not found")
            return "RoomNo Not found"
        else:
            print("Cannot Find Guest : NodeID not found")
            return "NodeID not found"

    def show_occupied_room(self):
        Room = []
        if len(self.__buildings) == 0:
            print("No existing building yet")
            return "No existing building yet"
        print("Occupied room as listed below:")
        for building in self.__buildings.values():
            print(f"Building node_id: {building.get_node_id}")
            for room in building.get_RoomAddr:
                print(f"Room number: {room.room_no}")
                Room.append(room)

        return Room

    def show_load_balance_report(self):
        n = Decimal(str(len(self.__guest)))
        if n == 0:
            print("There is no guest to calculate")
            return
        
        n_building = Decimal(str(len(self.__buildings)))

        if n_building == 0:
            print("There is some guest but there is no building??? There is Some thing wrong in the code")
            return

        min_load = Decimal("Infinity")
        max_load = Decimal("-Infinity")
        
        res = []
        getcontext().prec = 4
        mean = n / n_building
        sum_squred = 0

        for id , b in self.__buildings.items():
            b_guest_n = Decimal(str(len(b.get_RoomAddr)))
            res.append((id , b_guest_n))
            if b_guest_n < min_load:
                min_load = Decimal(str(b_guest_n))
            if b_guest_n > max_load:
                max_load = Decimal(str(b_guest_n))

            sum_squred += (b_guest_n - mean) ** 2

        getcontext().prec = 4
        variance = sum_squred / n_building
        sd = variance.sqrt()

        print("-"*20)
        print("Number of Guest in Each building : \n" , *res)
        print(
        "Load Balance Report\n"
        f"Min        : {min_load}\n" \
        f"Max        : {max_load}\n" \
        f"Mean       : {mean}\n"
        f"SD         : {sd}\n" \
        f"Total Guest: {n}")
        print("-"*20)
        return res

    def run_benchmark(self):
        pass

    def export_guest_csv(self):
        data = []
        for value in self.__guest:
            c, s = value.guest_id
            node_id = value.get_room.node_id
            room_no = value.get_room.room_no
            data.append({
                "channel_id": c,
                "sequence_id": s,
                "node_id": node_id,
                "room_no": room_no,
            })

        CSVExporter.write_csv(
            "guest.csv", data,
            fieldnames=["channel_id", "sequence_id", "node_id", "room_no"]
        )
        print("Export Complete...")
    
    def export_migration_csv(self):#did not test yet
        data = []

    def export_experiment_csv(self):
        pass