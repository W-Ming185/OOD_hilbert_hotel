class Building:
    def __int__(self,node_id):
        self.__node_id = node_id
        self.__RoomAddr = []
        self.__Vnode = []
    
    @property
    def get_node_id(self):
        return self.__node_id
    @property
    def get_RoomAddr(self):
        return self.__RoomAddr
    @property
    def get_Vnode(self):
        return self.__Vnode
    def add_room(self):
        pass
    def add_vnode(self,node):
        self.__Vnode.append(node)
        return len(self.__Vnode)