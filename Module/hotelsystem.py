import hashlib
import bisect
from guest import Guest
from vnode import VNode
from Building import Building
class HotelSystem():
    def init(self):
        self.__buildings = {}
        self.__guest = {}
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
    def add_guest_single(self, c):
        
        #find the latest sequence
        latest_sequence = 0
        latest_ch = 0

        #find the sequence

        for item in self.guest:
            channel , squence = item
            if channel > latest_ch:
                latest_ch = channel

            if channel == c:
                latest_sequence += 1
        new_sequence = latest_sequence + 1
        new_guest = Guest(c , new_sequence)
        
        #SHA-256 Hash
        salt = "ball"
        text = f"{c}:{new_sequence}{salt}"

        hash_num = hashlib.sha256(text.encode('utf-8'))
        hash_num_64bit = hash_num.digest()[:8]

        position = int.from_bytes(hash_num_64bit, byteorder='big')

        #Adding into the ring
        ring = self.ring

        if len(ring.get_Vnode) == 0:

            return "Cannot Insert Guest : No Building To InserT"
        for vnode in ring.get_Vnode:
            if vnode.get_hash_key >= position:
                building = vnode.get_building
                building.add_room(new_guest)
        return

    def add_guest_batch():


        pass
    def remove_guest():
        
        pass

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
