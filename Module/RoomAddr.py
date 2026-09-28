class RoomAddr:
    def __init__(self,node_id,room_no,guest):
        self.__node_id = node_id
        self.__room_no = room_no
        self.__guest = guest

    @property
    def get_node_id(self):
        return self.__node_id
    @property
    def get_room_no(self):
        return self.__room_no
    @property
    def get_guest(self):
        return self.__guest
    
    def assign_guest(self):
        pass

