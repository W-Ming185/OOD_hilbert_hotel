from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .guest import Guest


class RoomAddr:
    def __init__(self, node_id: int, room_no: int, guest: Guest | None = None):
        self.__node_id = node_id
        self.__room_no = room_no
        self.__guest = guest

    @property
    def node_id(self) -> int:
        return self.__node_id

    @property
    def room_no(self) -> int:
        return self.__room_no

    @property
    def guest(self) -> Guest | None:
        return self.__guest

    def assign_guest(self, guest: Guest | None) -> None:
        self.__guest = guest
