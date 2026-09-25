import guest
import class_RoomAddr
import class_Building

class HotelSystem:
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

    def search_guest_location(self,guest_id:tuple):
        if guest_id in self.__guest:
            guest = self.__guest.get(guest_id)
            guestroom = guest.room
            return (guestroom.node_id,guestroom.room_no)
        else:
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

    def export_csv():
        pass
