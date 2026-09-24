class VNode:
    def __init__(self,building):
        self.__hash_value = None
        self.__building = building
        self.__node_seq = None

    def assign_node_seq(self,rank):
        self.__node_seq = rank
    
    def get_hash_key(self):
        return self.__hash_value

    def get_building(self):
        return self.__building

    def get_node_seq(self):
        return self.__node_seq

    def assign_hash_key(self,key):
        self.__hash_value = key