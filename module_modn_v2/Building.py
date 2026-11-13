from __future__ import annotations

import bisect

from .RoomAddr import RoomAddr
from .guest import Guest


class Building:
    def __init__(self, node_id: int):
        self.__node_id = node_id
        self.__RoomAddr: list[RoomAddr] = []

    @property
    def get_node_id(self) -> int:
        return self.__node_id

    @property
    def get_RoomAddr(self) -> list[RoomAddr]:
        return self.__RoomAddr

    def add_room(self, guest: Guest) -> RoomAddr:
        c, s = guest.guest_id
        a, b = c - 1, s - 1
        room_no = ((a + b) * (a + b + 1)) // 2 + b + 1
        room = RoomAddr(self.__node_id, room_no, guest)
        bisect.insort(self.__RoomAddr, room, key=lambda item: item.room_no)
        guest.assign_room(room)
        return room

    def add_rooms(self, guests: list[Guest]) -> list[RoomAddr]:
        rooms = []
        for guest in guests:
            c, s = guest.guest_id
            a, b = c - 1, s - 1
            room = RoomAddr(self.__node_id, ((a + b) * (a + b + 1)) // 2 + b + 1, guest)
            guest.assign_room(room)
            rooms.append(room)
        self.__RoomAddr.extend(rooms)
        self.__RoomAddr.sort(key=lambda item: item.room_no)
        return rooms

    def remove_guests(self, guest_ids: set[tuple[int, int]]) -> None:
        kept = []
        for room in self.__RoomAddr:
            if room.guest is not None and room.guest.guest_id in guest_ids:
                room.guest.assign_room(None)
                room.assign_guest(None)
            else:
                kept.append(room)
        self.__RoomAddr = kept

    def remove_room(self, room_id: int) -> str:
        index = bisect.bisect_left(self.__RoomAddr, room_id, key=lambda room: room.room_no)
        if index == len(self.__RoomAddr) or self.__RoomAddr[index].room_no != room_id:
            return "This room not exist"
        room = self.__RoomAddr.pop(index)
        if room.guest is not None:
            room.guest.assign_room(None)
        room.assign_guest(None)
        return "Deletion Succeed"

