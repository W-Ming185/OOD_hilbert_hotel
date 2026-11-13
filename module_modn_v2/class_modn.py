from module_modn_v2.Building import Building

class HashMod:
    """Mod-N selector : building index = hash % N (N = number of buildings).
    Replaces ConsistentHashRing (no ring, no vnode)."""
    def __init__(self):
        self.__list = []   # buildings in insertion order

    @property
    def get_buildings(self):
        return self.__list
    @property
    def get_no_building(self):
        return len(self.__list)

    def add_building(self,building):
        self.__list.append(building)
        return building

    def remove_building(self,building):
        self.__list.remove(building)
        return building

    def get_building_for_guest(self,hash_value):
        if not self.__list:
            return None
        return self.__list[hash_value % len(self.__list)]