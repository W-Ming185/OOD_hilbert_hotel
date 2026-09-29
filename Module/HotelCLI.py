from Module.hotelsystem import HotelSystem

class HotelCLI:
    def __init__(self,system : HotelSystem):
        self.__system = system
        self.run()

    @property
    def get_system(self):
        return self.__system

    def _read_int(self , text : str):
        try:
            print(f"{text} : ",end="")
            inp = int(input(""))
            return inp
        except:
            raise Exception("Error")
            
    def run(self):
        # show menu and call method
        while True:
            print(
            "-------------------\n"
            "[0] Quit\n" 
            "[1] Add Guest\n" 
            "[2] Add Building\n" \
            "[3] Remove Guest\n"
            "-------------------\n")
            inp = input("Enter : ")
            
            if inp == "0":
                return 
            elif inp == "1":
                print(
                    "--------------------\n"
                    "Add Guest Method:\n"
                    "[1] Batch\n"
                    "[2] Single\n" 
                    "--------------------\n"
                )
                method = input("Method : ")
                self.handle_add_guest(method)
            elif inp == "2":
                building_id = input("Building ID : ")
                self.handle_add_building(building_id)
            elif inp == "3":
                print("Enter Guest ID for removal : ")
                c = input("c :")
                s = input("s :")
                self.handle_remove_guest(c,s)

    def initialize_system(self):

        pass

    def handle_add_guest(self , method : str) -> None:
            
            if method == "1":
                c = self._read_int("c")
                s_start = self._read_int("s_start")
                n = self._read_int("n")
                return self.handle_add_batch(c , s_start , n )
            elif method == "2":
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
            if c < 0 or s_start < 0 or n < 0:
                raise Exception("Input must be positive number")
        except:
            print("Error c,s_start,n should be int")
            return "Error c,s_start,n should be int"
        system = self.get_system
        return system.add_guest_batch(c , s_start , n)

    def handle_add_single(self , c , s):
        try:
            c = int(c)
            s = int(s)
            if c < 0 or s < 0:
                raise Exception("Input must be positive number")
        except:
            print("Error c,s should be int")
            return "Error c,s should be int"
        
        system = self.get_system
        return system.add_guest_single(c , s)
    
    def handle_remove_guest(self , c , s):
        try:
            c = int(c)
            s = int(s)

            if c < 0 or s < 0:
                raise Exception("Input must be positive number")
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

Hotel = HotelCLI(HotelSystem())