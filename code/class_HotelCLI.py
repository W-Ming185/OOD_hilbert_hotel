from hotelsystem import HotelSystem

class HotelCLI:
    def __int__(self,system : HotelSystem):
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
            self.handle_add_batch(c , s_start , n )
        elif method == "Single":
            c = self._read_int("c")
            s = self._read_int("s")
            self.handle_add_single(c , s)
            
        return 
    
    def handle_add_batch(self , c , s_start , n):
        system = self.get_system
        return system.add_batch(c , s_start , n)
    
    def handle_add_single(self , c , s):
        system = self.get_system
        return system.add_single(c , s)
    
    def handle_remove_guest(self , ):
        system = self.get_system
        return system.remove_guest()
    
    def handle_add_building(self):
        system = self.get_system

        return system.add_building()
    
    def handle_remove_building(self):
        system = self.get_system

        return system.remove_building()
    
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

