class Guest():
    def init(self,c,s):
        self.__c = c
        self.__s = s
        self.__room = RoomAddr()
        self.__guest_id


    def get_guest_id(self):
        return self.__guest_id

    def get_room(self):
        return self.__room