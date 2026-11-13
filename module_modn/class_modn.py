class HashMod:

    def __init__(self):
        self.__buildings = []
        self.__no_building = 0

    @property
    def get_buildings(self):
        return self.__buildings
    @property
    def get_no_building(self):
        return self.__no_building
    
    def add_building(self, building):
        self.get_buildings.append(building)
        self.no_building = len(self.get_buildings)

    def remove_building(self, node_id):
        for i, building in enumerate(self.get_buildings):
            if building.get_node_id == node_id:
                self.get_buildings.pop(i)
                self.no_building = len(self.get_buildings)
                return building
        return None

    def calculate_index(self, hash_value):
        return hash_value % self.get_no_building

    def get_building(self, hash_value):
        index = self.calculate_index(hash_value)
        return self.get_no_building[index]