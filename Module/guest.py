from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Module.RoomAddr import RoomAddr
class Guest():
    def __init__(self,c,s,hash_value):
        self.__room = None
        self.__guest_id = (c , s)
        self.__hash_value = hash_value

    @property
    def guest_id(self):
        return self.__guest_id
    
    @property
    def get_room(self):
        return self.__room

    @property
    def get_hash_value(self):
        return self.__hash_value
    
    def assign_room(self , room : "RoomAddr"):
        self.__room = room
