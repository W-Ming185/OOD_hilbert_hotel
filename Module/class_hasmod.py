class Hashmod:
    def __init__(self):
        self.__building = []
    def add_building(self, data):
        index = data % len(self.__building)
        self.__building[index].append(data)
    def remove_building(self, data):
        index = data % len(self.__building)
        if data in self.__building[index]:
            self.__building[index].remove(data)