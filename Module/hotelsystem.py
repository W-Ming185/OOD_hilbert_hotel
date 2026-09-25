class HotelSystem():
    def init(self):
        self.__buildings = {}
        self.__guest = {}
        self.__report = Report()
        self.__ring = ConsistentHashRing()
        self.__csvexport = CSVExporter()
        self.__benchmark = BenchmarkResult()

    def initialize_system():
        pass

    # Add Controller
    def add_guest_single():

        pass
    def add_add_guest_batch():

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

    def show_occupied_room(self):
        all_room = []
        for Building in self.__buildings:
            for room in Building.get_RoomAddr:
                all_room.append(room)
                
        return all_room

    def show_load_balance_report():
        pass

    def run_benchmark():
        pass

    def export_csv():
        pass
