class Guest:
    def init(self,c,s):
        self.__c = c
        self.__s = s
        self.__room = RoomAddr()
        self.__guest_id

    @property
    def guest_id(self):
        return self.__guest_id
    
    @property
    def room(self):
        return self.__room