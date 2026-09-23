class Building:
    def __int__(self,node_id):
        self.__node_id = node_id
        self.__RoomAdrr = []
        self.__Vnode = []
    
    @property
    def get_node_id(self):
        return self.__node_id

    def add_room(self):
        pass