from guest import Guest
from RoomAddr import RoomAddr
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
    
    def add_room(self , guest : Guest):
        c , s = guest.get_guest_id
        a = c - 1
        b = s - 1
        room_no = (a+b) * (a+b+1) // 2 + b + 1
        id 
        new_room = RoomAddr(self.get_node_id, room_no)
        #Bidirectional Link
        new_room.assign_guest(guest)
        guest.assign_room(new_room)
        #Add room into building
        self.__RoomAddr.append(new_room)
        
        


    def add_vnode(self,node):
        self.__Vnode.append(node)
        return len(self.__Vnode)