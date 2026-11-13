from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .RoomAddr import RoomAddr


class Guest:
    def __init__(self, c: int, s: int, hash_value: int):
        self.__guest_id = (c, s)
        self.__hash_value = hash_value
        self.__room: RoomAddr | None = None

    @property
    def guest_id(self) -> tuple[int, int]:
        return self.__guest_id

    @property
    def get_room(self) -> RoomAddr | None:
        return self.__room

    @property
    def get_hash_value(self) -> int:
        return self.__hash_value

    def assign_room(self, room: RoomAddr | None) -> None:
        self.__room = room
