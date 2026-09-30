import hashlib
import bisect
import csv
from Module.guest import Guest
from Module.vnode import VNode
from Module.RoomAddr import RoomAddr
from Module.Building import Building
from Module.ConsistentHashRing import ConsistentHashRing
from Module.CSVExporter import CSVExporter


class HotelSystem():
    def __init__(self):
        self.__buildings = {}
        self.__guest = []
        # self.__report = Report()
        self.__ring = ConsistentHashRing(vnode_size = 4 )#กำหนดเอง
        # self.__csvexport = CSVExporter() 
        # self.__benchmark = BenchmarkResult()

    @property
    def ring(self):
        return self.__ring
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
    
    def print_guest(self):
        ls = self.guest_data_list
        print("-----------------")
        print("ID,ROOM_NO,HASH")
        for i in ls:
            print(i)
        print("-----------------")

    def initialize_system():
        pass

    def guest_dup_check(self , c , s):
        inp = (c,s)
        for guest in self.__guest:
            if guest.guest_id == inp:
                return True
        return False
    
    def ring_check(self):
        ring = self.__ring
        if len(ring.get_Vnode) == 0:
            print("Cannot Insert Guest : No Building To Insert")
            return False
        return  True
    
    # ! ! ! No edge case yet ! ! !
    def add_guest_single(self, c , s):
        
        if not self.ring_check():
            return
        
        if self.guest_dup_check(c,s):
            print("This id is already exist")
            return "This id is already exist"
        id = (c,s)
        #SHA-256 Hash
        salt = "ball"
        text = f"{c}:{s}{salt}"

        hash_num = hashlib.sha256(text.encode('utf-8'))
        hash_num_64bit = hash_num.digest()[:8]

        position = int.from_bytes(hash_num_64bit, byteorder='big')

        #Adding into the ring
        ring = self.ring
        vnode_to_be_inserted = ring.get_vnode_for_guest(position)
        building = vnode_to_be_inserted.get_building
        new_guest = Guest(c,s,position)
        bisect.insort(self.__guest , new_guest , key= lambda x : x.get_hash_value)
        building.add_room(new_guest)
        print("Add Guest Succeed")
        self.print_guest()
        return "Add Guest Succeed"

    def add_guest_batch(self , c , s_start , n):
        if not self.ring_check():
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
            return
        id = (c,s)
        rm_guest = None
        for guest in self.__guest:
            if guest.guest_id == id:
                rm_guest = guest

        room = rm_guest.get_room
        bulding_id = room.node_id

        building = self.__buildings[bulding_id]
        building.remove_room(room.room_no)
        self.__guest.remove(rm_guest)

        #reference clearing (จะมีไม่มีก็ได้)
        room.assign_guest(None)
        rm_guest.assign_room(None)
        self.print_guest()
        print("Removal Succeed")
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

            for x in self.__buildings.values():
                print(f"node id {x.get_node_id} : {[y.get_hash_key for y in x.get_Vnode]}")

            affected_guest = []
            for vnode in building.get_Vnode:
                prev = self.__ring.prev_vnode(vnode) 
                prev_hash = prev.get_hash_key
                new_hash = vnode.get_hash_key

                if prev_hash < new_hash:
                    start_idx = bisect.bisect_right(self.__guest, prev_hash, key=lambda x: x.get_hash_value)
                    end_idx = bisect.bisect_right(self.__guest, new_hash, key=lambda x: x.get_hash_value)
                    affected_guest.extend(self.__guest[start_idx:end_idx])
                else:
                    start_idx = bisect.bisect_right(self.__guest, prev_hash, key=lambda x: x.get_hash_value)
                    end_idx = bisect.bisect_right(self.__guest, new_hash, key=lambda x: x.get_hash_value)
                    affected_guest.extend(self.__guest[start_idx:])
                    affected_guest.extend(self.__guest[:end_idx])

            if affected_guest:
                history = self.migration(affected_guest)
                for i in history:
                    print(i)
            for i in self.__buildings.values():
                print(f"Building : {i.get_node_id}")
                print(f"Guest : {len(i.get_RoomAddr)}")
                for room in i.get_RoomAddr:
                    print(room.guest.guest_id)
            return building

    def remove_building(self,node_id): #อย่าลืมmigrationnnnnnnnnnnnnnnnnnnnnn
        
        if node_id in self.__buildings:
            if len(self.__buildings) == 1:
                print("This is The Last Building")
                return "This is The Last Building"
            building = self.__buildings[node_id]
            
            old_vnode = self.__ring.remove_node(building)

            affected_guest = []
            for room in building.get_RoomAddr:
                affected_guest.append(room.guest)
            if affected_guest:
                history = self.migration(affected_guest)
                for i in history:
                    print(i)
            self.__buildings.pop(node_id)
            print(f"Success removing building {node_id}.")
            for x in self.__buildings.values():
                print(f"node id {x.get_node_id} : {[y.get_hash_key for y in x.get_Vnode]}")

            for i in self.__buildings.values():
                print(f"Building : {i.get_node_id}")
                print(f"Guest : {len(i.get_RoomAddr)}")
                for room in i.get_RoomAddr:
                    print(room.guest.guest_id)
            return building
        else:
            print(f"{node_id} is not exist.")


    def search_guest_location(self,guest_id:tuple):
        i = bisect.bisect_left(self.__guest, guest_id, key=lambda g: g.guest_id)
        if i < len(self.__guest) and self.__guest[i].guest_id == guest_id:
            guest = self.__guest[i]
            room = guest.get_room
            return (room.node_id, room.room_no)
        return "guest_id not found"
        
    def migration(self,guest_list):
        history = []
        for guest in guest_list:
            room = guest.get_room
            old_node_id = room.node_id
            old_node = self.__buildings[old_node_id]
            new_vnode = self.__ring.get_vnode_for_guest(guest.get_hash_value)
            new_node = new_vnode.get_building
            new_node.add_room(guest)
            old_node.remove_room(room.room_no)
            history.append(f"{guest.guest_id} : {old_node_id} -> {new_node.get_node_id}")
        return history
        

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
    
    def export_migration_csv():#did not test yet
        data = []

    def export_experiment_csv():
        pass


