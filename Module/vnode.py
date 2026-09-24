class VNode:
    def __init__(self,hash_value,building):
        self.__hash_value = hash_value
        self.__building = building
        self.__node_seq = None

    def assign_node_seq(self,rank):
        self.__node_seq = rank
    
    def get_hash_key(self):
        return self.__hash_value

    def get_building(self):
        return self.__building