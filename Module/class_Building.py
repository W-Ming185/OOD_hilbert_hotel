class Building:
    def __int__(self,node_id):
        self.__node_id = node_id
        self.__RoomAddr = []
        self.__Vnode = []
    
    @property
    def node_id(self):
        return self.__node_id

    @property
    def RoomAddr(self):
        return self.__RoomAddr

    @property
    def Vnode(self):
        return self.__Vnode

    def add_room(self):
        pass