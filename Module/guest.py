from RoomAddr import RoomAddr
class Guest():
    def init(self,c,s):
        self.__room = None
        self.__guest_id = (c , s)

    @property
    def get_guest_id(self):
        return self.__guest_id
    
    @property
    def get_room(self):
        return self.__room

    def assign_room(self , room : RoomAddr):
        self.__room = room