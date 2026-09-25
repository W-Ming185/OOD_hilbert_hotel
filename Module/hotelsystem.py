class HotelSystem():
    def __init__(self):
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

    def add_building(self,node_id):
        if node_id in self.__buildings:
            print(f"Building {node_id} already exists.")
            return
        else:
            building = Building(node_id)
            self.__buildings[node_id] = building
            return building
        pass

    def remove_building(self,node_id):
        if node_id in self.__buildings:
            building = self.__buildings.pop(node_id)
            print(f"Success adding building {node_id}.")
            return building
        else:
            print(f"{node_id} is not exist.")
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