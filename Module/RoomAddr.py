from guest import Guest
class RoomAddr:
    def __int__(self,node_id,room_no):
        self.__node_id = node_id
        self.__room_no = room_no
        self.__guest = None

    @property
    def get_node_id(self):
        return self.__node_id
    @property
    def get_room_no(self):
        return self.__room_no
    @property
    def get_guest(self):
        return self.__guest
    
    def assign_guest(self , guest : Guest):
        self.__guest = guest

