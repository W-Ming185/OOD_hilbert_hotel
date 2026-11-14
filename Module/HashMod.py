class HashMod:
    """Mod-N building selector (the baseline method).
    building = buildings[hash % N]   N = number of buildings, kept in the order they were added."""
    def __init__(self):
        self.__list = []

    @property
    def get_buildings(self):
        return self.__list
    @property
    def get_no_building(self):
        return len(self.__list)

    def add_building(self,building):
        self.__list.append(building)      # new building goes to the end

    def remove_building(self,building):
        self.__list.remove(building)      # the rest keep their order

    def get_building_for_guest(self,hash_value):
        if not self.__list:
            return None
        return self.__list[hash_value % len(self.__list)]