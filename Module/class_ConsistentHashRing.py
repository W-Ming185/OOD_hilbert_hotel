import bisect

class ConsistentHashRing:
    def __init__(self):
        self.__Vnode = []
    @property
    def get_Vnode(self):
        return self.__Vnode
    
    def add_node(self,building,):
        if self.__Vnode is None:
            pass
        bisect.insort(self.__Vnode,data)
    def remove_node(self):
        pass
