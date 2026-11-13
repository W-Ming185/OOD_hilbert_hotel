class HashMod:
    def __init__(self):
        self.__list = []   # buildings in the order they were added (slot = position in this list)

    @property
    def get_buildings(self):
        return self.__list

    @property
    def get_no_building(self):
        return len(self.__list)

    def add_building(self,building):
        self.__list.append(building)
        return building

    def remove_building(self, building):
        self.__list.remove(building)   # the order of the remaining buildings is kept
        return building

    def get_building_for_guest(self,hash_value):
        index = hash_value % len(self.__list)   # Mod-N : H(guest) mod N
        return self.__list[index]