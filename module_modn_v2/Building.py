from module_modn_v2.guest import Guest
from module_modn_v2.RoomAddr import RoomAddr
import bisect

class Building:
    def __init__(self,node_id):
        self.__node_id = node_id
        self.__RoomAddr = []
    
    @property
    def get_node_id(self):
        return self.__node_id
    @property
    def get_RoomAddr(self):
        return self.__RoomAddr
    
    def add_room(self , guest : Guest):
        c , s = guest.guest_id
        a = c - 1
        b = s - 1
        room_no = (a+b) * (a+b+1) // 2 + b + 1
        new_room = RoomAddr(self.get_node_id, room_no , guest)
        #Bidirectional Link
        new_room.assign_guest(guest)
        guest.assign_room(new_room)
        #Add room into building
        bisect.insort(self.__RoomAddr , new_room , key=lambda x : x.room_no)
        #self.__RoomAddr.append(new_room)

    def remove_room(self , room_id):
        idx = bisect.bisect_left(self.__RoomAddr,room_id,key=lambda room: room.room_no,)
        if idx is None:
            return "This room not exist"
        del self.__RoomAddr[idx]
        return "Deletion Succeed"