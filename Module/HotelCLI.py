#from hotelsystem import HotelSystem
from guest import Guest
class HotelCLI:
    def __init__(self,system : HotelSystem):
        self.__system = system
        self.run()
    @property
    def get_system(self):
        return self.__system

    def _read_int(self , text : str):
        try:
            input = int(input(f"{text} :"))
            return input
        except:
            raise Exception("Error")
            
    def run(self):
        # show menu and call method
        pass
    def initialize_system(self):

        pass

    def handle_add_guest(self , method : str) -> None:
            method = input("Enter Method : ")
            if method == "Batch":
                c = self._read_int("c")
                s_start = self._read_int("s_start")
                n = self._read_int("n")
                return self.handle_add_batch(c , s_start , n )
            elif method == "Single":
                c = self._read_int("c")
                s = self._read_int("s")
                return self.handle_add_single(c , s)
            else:
                print("Invalid Method")
                return "Invalid Method"
    
    def handle_add_batch(self , c , s_start , n):
        try:
            c = int(c)
            s_start = int(s_start)
            n = int(n)
        except:
            print("Error c,s_start,n should be int")
            return "Error c,s_start,n should be int"
        system = self.get_system
        return system.add_batch(c , s_start , n)

    def handle_add_single(self , c , s):
        try:
            c = int(c)
            s = int(s)
        except:
            print("Error c,s should be int")
            return "Error c,s should be int"
        
        system = self.get_system
        return system.add_guest_single(c , s)
    
    def handle_remove_guest(self , c , s):
        try:
            c = int(c)
            s = int(s)
        except:
            print("Error c,s should be int")
            return "Error c,s should be int"
        
        system = self.get_system
        return system.remove_guest(c , s)
    
    def handle_add_building(self , node_id):
        try:
            node_id = int(node_id)
        except:
            print("Node it Need to be int")
            return "Node it Need to be int"
        system = self.get_system

        return system.add_building(node_id)
    
    def handle_remove_building(self , node_id):
        system = self.get_system

        return system.remove_building(node_id)
    
    def handle_search_guest_location(self):
        system = self.get_system

        return system.search_guest_location()
    
    def handle_search_guest_by_room_id_and_building_id(self):
        system = self.get_system

        return system.search_guest_by_room_id_and_building_id()
    
    def show_occupied_rooms(self):
        system = self.get_system

        return system.show_occupied_rooms()
    
    def show_load_balance_report(self):
        system = self.get_system

        return system.show_load_balance_report()
    
    def run_benchmark(self):
        system = self.get_system

        return system.run_benchmark()
    
    def export_csv(self):
        system = self.get_system
        return system.export_csv()
