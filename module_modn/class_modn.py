class HashMod:

    def __init__(self):
        self.buildings = []
        self.no_building = 0

    def add_building(self, building):
        self.buildings.append(building)
        self.no_building = len(self.buildings)

    def remove_building(self, node_id):
        for i, building in enumerate(self.buildings):
            if building.get_node_id == node_id:
                self.buildings.pop(i)
                self.no_building = len(self.buildings)
                return building

        return None

    def calculate_index(self, hash_value):
        return hash_value % self.no_building

    def get_building(self, hash_value):
        index = self.calculate_index(hash_value)
        return self.buildings[index]