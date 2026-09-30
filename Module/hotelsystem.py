import hashlib
import bisect
import csv
from Module.guest import Guest
from vnode import VNode
from Building import Building
from CSVExporter import CSVExporter
from bisect import bisect_left, insort

class HotelSystem():
    def __init__(self):
        self.__buildings = {}
        self.__guest = []
        self.__report = Report()
        self.__ring = ConsistentHashRing(vnode_size = 4 )#กำหนดเอง
        self.__csvexport = CSVExporter() 
        self.__benchmark = BenchmarkResult()

    @property
    def ring(self):
        return self.__ring
    @property
    def guest(self):
        return self.__guest
    
    def initialize_system():
        pass

    # ! ! ! No edge case yet ! ! !
    def add_guest_single(self, c , s):
        id = tuple(c,s)
        if id in self.__guest:
            print("This id is already exist")
            return "This id is already exist"

        #SHA-256 Hash
        salt = "ball"
        text = f"{c}:{s}{salt}"

        hash_num = hashlib.sha256(text.encode('utf-8'))
        hash_num_64bit = hash_num.digest()[:8]

        position = int.from_bytes(hash_num_64bit, byteorder='big')

        #Adding into the ring
        ring = self.ring

        if len(ring.get_Vnode) == 0:

            return "Cannot Insert Guest : No Building To InserT"
        vnode_to_be_inserted = None
        vnode_position = float("inf")

        for vnode in ring.get_Vnode:
            #ยังไม่ได้ handle กรณี vnode ซ้อนกัน
            if position <= vnode.get_hash_key < vnode_position :
                vnode_to_be_inserted  = vnode
                vnode_position = vnode_to_be_inserted.get_position

        if vnode_to_be_inserted is None:
            print("There is no vnode to be inserted")
            return "There is no vnode to be inserted"

        building = vnode_to_be_inserted.get_building
        new_guest = Guest(c,s)
        bisect.insort(self.__guest , new_guest , key= lambda x : x.get_hash_value)
        building.add_room(new_guest)
        print("Add Guest Succeed")
        return "Add Guest Succeed"

    def add_guest_batch(self , c , s_start , n):
        #Demo ก่อน Optimize ทีหลังได้ถ้า performance ไม่ดี
        for x in range(s_start , n):
            id = tuple(c,x)
            if id in self.__guest:
                print("There is some guest in this range already")
                return
        
        for x in range(s_start , n):
            self.add_guest_single(x , c)
        return "Add Batch Succeed"

    def remove_guest(self , c ,s):
        id = tuple(c,s)
        if id not in self.__guest:
            print("There are no guest in this id")
            return "There are no guest in this id"
        rm_guest = self.__guest.pop(id)
        room = rm_guest.get_room
        bulding_id = room.get_node_id

        building = self.__buildings[bulding_id]
        building.remove_room(room.get_room_no)

        #reference clearing (จะมีไม่มีก็ได้)
        room.assign_guest(None)
        rm_guest.assign_room(None)
        return "Removal Succeed"

    def add_building(self,node_id): #อย่าลืมmigrationnnnnnnnnnnnnnnnnnnnnn
        if node_id in self.__buildings:
            print(f"Building {node_id} already exists.")
            return
        else:
            building = Building(node_id)
            self.__buildings[node_id] = building
            vnode_size = self.__ring.get_vnode_size
            for _ in range(vnode_size):
                self.__ring.add_node(building)
            print(self.__buildings,[x.get_hash_key() for x in self.__ring.get_Vnode])
            return building
        pass

    def remove_building(self,node_id): #อย่าลืมmigrationnnnnnnnnnnnnnnnnnnnnn
        if node_id in self.__buildings:
            building = self.__buildings.pop(node_id)
            self.__ring.remove_node(building)
            print(f"Success removing building {node_id}.")
            print(self.__buildings,[x.get_hash_key() for x in self.__ring.get_Vnode]) 
            return building
        else:
            print(f"{node_id} is not exist.")
        pass

    def search_guest_location(self,guest_id:tuple):
        i = bisect_left(self.__guest, guest_id, key=lambda g: g.guest_id)
        if i < len(self.__guest) and self.__guest[i].guest_id == guest_id:
            guest = self.__guest[i]
            room = guest.get_room
            return (room.node_id, room.room_no)
        return "guest_id not found"

    def search_guest_by_room_id_and_building_id(self,location:tuple):
        node_id,room_no = location
        if node_id in self.__buildings:
            building = self.__buildings.get(node_id)
            for i in building.RoomAddr:
                if i.room_no == room_no:
                    room = i
                    guest = room.guest
                    return guest.guest_id
            return "room_no not found"
        else:
            return "node_id not found"

    def show_occupied_room():
        pass

    def show_load_balance_report():
        pass

    def run_benchmark():
        pass

    def export_guest_csv(self):
            data = []
            for value in self.__guest:
                c, s = value.guest_id
                node_id = value.get_room.node_id
                room_no = value.get_room.room_no
                data.append({
                    "channel_id": c,
                    "seat_id": s,
                    "node_id": node_id,
                    "room_no": room_no,
                })
    
            CSVExporter.write_csv(
                "guest.csv", data,
                fieldnames=["channel_id", "seat_id", "node_id", "room_no"]
            )
    
    def export_migration_csv():
        pass

    def export_experiment_csv():
        pass


hotel = HotelSystem()
hotel.add_building("a")
hotel.add_building("b")
hotel.remove_building("b")