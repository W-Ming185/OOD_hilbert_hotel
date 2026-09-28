from class_Building import Building
from class_ConsistentHashRing import ConsistentHashRing
from guest import Guest
from vnode import VNode
from class_RoomAddr import RoomAddr
import bisect
class HotelSystem():
    def __init__(self):
        self.__buildings = {}
        self.__guest = []
        # self.__report = Report()
        self.__ring = ConsistentHashRing(vnode_size = 4 )#กำหนดเอง
        # self.__csvexport = CSVExporter() 
        # self.__benchmark = BenchmarkResult()

    def initialize_system():
        pass

    # Add Controller
    def add_guest_single():

        pass
    def add_add_guest_batch():

        pass
    def remove_guest():
        pass

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

            affected_guest = []
            for vnode in building.get_Vnode:
                prev = self.__ring.prev_vnode(vnode) 
                prev_hash = prev.get_hash_key()
                new_hash = vnode.get_hash_key()

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
                self.migration(affected_guest)
            return building
        pass

    def remove_building(self,node_id): #อย่าลืมmigrationnnnnnnnnnnnnnnnnnnnnn
        if node_id in self.__buildings:
            building = self.__buildings[node_id]
            old_vnode = self.__ring.remove_node(building)
            
            print(f"Success removing building {node_id}.")
            print(self.__buildings,[x.get_hash_key() for x in self.__ring.get_Vnode]) 

            affected_guest = []
            for room in building.get_RoomAddr:
                affected_guest.append(room.get_guest)
            if affected_guest:
                self.migration(affected_guest)
            self.__buildings.pop(node_id)
            return building
        else:
            print(f"{node_id} is not exist.")
        pass

    def migration(self,guest_list):
        history = []
        for guest in guest_list:
            room = guest.get_room
            old_node_id = room.get_node_id
            old_node = self.__buildings[old_node_id]
            new_vnode = self.__ring.get_vnode_for_guest(guest.get_hash_value)
            new_node = new_vnode.get_building()
            new_node.add_room(guest)
            old_node.remove_room(room.get_room_no)
            history.append(f"{guest.get_guest_id} : {old_node_id} -> {new_node.get_node_id}")
        return history
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


hotel = HotelSystem()
hotel.add_building("a")
hotel.add_building("b")
hotel.remove_building("b")