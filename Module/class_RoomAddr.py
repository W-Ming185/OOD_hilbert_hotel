class RoomAddr:
    def __int__(self,node_id,room_no,guest):
        self.__node_id = node_id
        self.__room_no = room_no
        self.__guest = guest

    @property
    def node_id(self):
        return self.__node_id

    @property
    def room_no(self):
        return self.__room_no

    @property
    def guest(self):
        return self.__guest
    
    def assign_guest(self):
        pass

