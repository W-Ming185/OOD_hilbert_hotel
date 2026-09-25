import hashlib
import bisect
from guest import Guest
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
        ring = self.ring
        #find the latest sequence
        latest_sequence = 0
        latest_ch = 0

        for item in self.guest:
            channel , squence = item
            if channel > latest_ch:
                latest_ch = channel

            if channel == c:
                last_sequence += 1

        
        #First Man in new channel
        if last_sequence == 0:
            new_guest = Guest(c , 1)


            return   
        #Continue the seuqence
        new_guest = Guest(c , last_sequence + 1)


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
