import hashlib
import bisect
from Module.guest import Guest
from vnode import VNode
from Building import Building
class HotelSystem():
    def init(self):
        self.__buildings = {}
        self.__guest = []
        self.__report = Report()
        self.__ring = ConsistentHashRing()
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


    def add_building():
        pass

    def remove_building():
        pass

    def search_guest_location():
        pass

    def search_guest_by_room_id_and_building_id():
        pass

    def show_occupied_room():
        pass

    def show_load_balance_report():
        pass

    def run_benchmark():
        pass

    def export_csv():
        pass
