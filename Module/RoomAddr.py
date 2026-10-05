from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Module.guest import Guest
class RoomAddr:
    def __init__(self,node_id,room_no,guest):
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
    
    def assign_guest(self , guest : "Guest"):
        self.__guest = guest

