class VNode:
    def __init__(self,hash_value):
        self.__hash_value = hash_value
        self.__node_seq = None
        self.__building = None
        self.__next = None
        self.__prev = None

    def assign_next(self,node):
        pass

    def assign_prev(self,node):
        pass

    def assign_building(self,building):
        pass

    def assign_node_seq(self,rank):
        pass
    
    def get_position(self):
        pass