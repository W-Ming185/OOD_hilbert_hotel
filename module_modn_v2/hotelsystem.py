from __future__ import annotations

import bisect
import hashlib
import time

from .Building import Building
from .CSVExport import CSVExporter
from .Report import Report
from .class_modn import HashMod
from .guest import Guest


class HotelSystem:
    def __init__(self, salt: str = "0"):
        self.__buildings: dict[int, Building] = {}
        self.__guest: list[Guest] = []
        self.__guest_ids: set[tuple[int, int]] = set()
        self.__hashmod = HashMod()
        self.__salt = str(salt)
        self.__last_migration: list[dict] = []
        self.__last_guest_count = 0

    @property
    def hashmod(self) -> HashMod:
        return self.__hashmod

    @property
    def guest(self) -> list[Guest]:
        return self.__guest

    @property
    def buildings(self) -> dict[int, Building]:
        return self.__buildings

    @property
    def last_migration(self) -> list[dict]:
        return list(self.__last_migration)

    @property
    def last_migration_count(self) -> int:
        return len(self.__last_migration)

    @property
    def last_migration_rate(self):
        from decimal import Decimal
        if self.__last_guest_count == 0:
            return None
        return Decimal(self.last_migration_count) / Decimal(self.__last_guest_count)

    @property
    def guest_data_list(self) -> list[tuple]:
        return [(g.guest_id, g.get_room.room_no, g.get_hash_value, g.get_room.node_id)
                for g in self.__guest if g.get_room is not None]

    def print_guest(self) -> None:
        print("-----------------\nID,ROOM_NO,HASH")
        for row in self.guest_data_list:
            print(row)
        print("-----------------")

    def initialize_system(self, building_ids: list[int], channel_guest_counts: dict[int, int]) -> None:
        """Initialize from explicit node IDs and per-channel counts (sequences start at 1)."""
        if self.__buildings or self.__guest:
            raise ValueError("System is already initialized")
        if not building_ids or len(set(building_ids)) != len(building_ids):
            raise ValueError("Provide at least one unique building ID")
        if any(not isinstance(count, int) or isinstance(count, bool) or count < 0
               for count in channel_guest_counts.values()):
            raise ValueError("Channel guest counts must be non-negative integers")
        for node_id in building_ids:
            result = self.add_building(node_id)
            if not isinstance(result, Building):
                raise ValueError(str(result))
        for channel_id, count in channel_guest_counts.items():
            if not isinstance(channel_id, int) or isinstance(channel_id, bool) or channel_id < 1:
                raise ValueError("Channel IDs must be positive integers")
            if count:
                self.add_guest_batch(channel_id, 1, count)

    def guest_dup_check(self, c: int, s: int) -> bool:
        return (c, s) in self.__guest_ids

    def hashmod_check(self) -> bool:
        return self.__hashmod.get_no_building > 0

    @staticmethod
    def _validate_guest_id(c: int, s: int) -> None:
        if isinstance(c, bool) or isinstance(s, bool) or not isinstance(c, int) or not isinstance(s, int):
            raise TypeError("Guest IDs must be integers")
        if c < 1 or s < 1:
            raise ValueError("Guest IDs must be positive integers")

    def _record_no_migration(self) -> None:
        self.__last_guest_count = len(self.__guest)
        self.__last_migration = []

    def _hash_guest(self, c: int, s: int) -> int:
        payload = f"guest:{c}:{s}{self.__salt}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")

    def add_guest_single(self, c: int, s: int):
        self._validate_guest_id(c, s)
        if not self.hashmod_check():
            return "Cannot Insert Guest: No Building To Insert"
        if self.guest_dup_check(c, s):
            return "This id is already exist"
        guest = Guest(c, s, self._hash_guest(c, s))
        building = self.__hashmod.get_building(guest.get_hash_value)
        building.add_room(guest)
        bisect.insort(self.__guest, guest, key=lambda item: item.guest_id)
        self.__guest_ids.add(guest.guest_id)
        return "Add Guest Succeed"

    def add_guest_batch(self, c: int, s_start: int, n: int):
        self._validate_guest_id(c, s_start)
        if isinstance(n, bool) or not isinstance(n, int):
            raise TypeError("Batch size must be an integer")
        if n < 0:
            raise ValueError("Batch size must be non-negative")
        if not self.hashmod_check():
            return "Cannot Insert Guest: No Building To Insert"
        ids = [(c, s) for s in range(s_start, s_start + n)]
        if any(guest_id in self.__guest_ids for guest_id in ids):
            return "There is some guest in this range already"
        new_guests = [Guest(c, seat, self._hash_guest(c, seat)) for _, seat in ids]
        by_building: dict[int, list[Guest]] = {}
        for guest in new_guests:
            building = self.__hashmod.get_building(guest.get_hash_value)
            by_building.setdefault(building.get_node_id, []).append(guest)
        for node_id, guests in by_building.items():
            self.__buildings[node_id].add_rooms(guests)
        self.__guest = sorted([*self.__guest, *new_guests], key=lambda item: item.guest_id)
        self.__guest_ids.update(guest.guest_id for guest in new_guests)
        return "Add Batch Succeed"

    def remove_guest(self, c: int, s: int):
        target = (c, s)
        for index, guest in enumerate(self.__guest):
            if guest.guest_id == target:
                room = guest.get_room
                if room is not None:
                    self.__buildings[room.node_id].remove_room(room.room_no)
                self.__guest.pop(index)
                self.__guest_ids.remove(target)
                return "Removal Succeed"
        return "This id does not exist for removal"

    def add_building(self, node_id: int):
        if isinstance(node_id, bool) or not isinstance(node_id, int):
            raise TypeError("Building ID must be an integer")
        if node_id in self.__buildings:
            self._record_no_migration()
            return f"Building {node_id} already exists."
        building = Building(node_id)
        self.__buildings[node_id] = building
        self.__hashmod.add_building(building)
        self.__last_guest_count = len(self.__guest)
        self.__last_migration = self.migration(list(self.__guest))
        return building

    def remove_building(self, node_id: int):
        if node_id not in self.__buildings:
            self._record_no_migration()
            return f"{node_id} is not exist."
        if len(self.__buildings) == 1:
            self._record_no_migration()
            return "This is The Last Building"
        old_building = self.__buildings[node_id]
        self.__last_guest_count = len(self.__guest)
        self.__hashmod.remove_building(node_id)
        self.__last_migration = self.migration(list(self.__guest))
        del self.__buildings[node_id]
        return old_building

    def search_guest_location(self, c: int, s: int):
        target = (c, s)
        index = bisect.bisect_left(self.__guest, target, key=lambda guest: guest.guest_id)
        if index < len(self.__guest) and self.__guest[index].guest_id == target:
            room = self.__guest[index].get_room
            return (room.node_id, room.room_no) if room else "guest_id not found"
        return "guest_id not found"

    def migration(self, guest_list: list[Guest]) -> list[dict]:
        moves = []
        for guest in guest_list:
            room = guest.get_room
            if room is None:
                continue
            old_id = room.node_id
            new_building = self.__hashmod.get_building(guest.get_hash_value)
            if new_building.get_node_id == old_id:
                continue
            moves.append((guest, old_id, new_building.get_node_id, room.room_no))
        by_old: dict[int, set[tuple[int, int]]] = {}
        by_new: dict[int, list[Guest]] = {}
        for guest, old_id, new_id, _ in moves:
            by_old.setdefault(old_id, set()).add(guest.guest_id)
            by_new.setdefault(new_id, []).append(guest)
        for node_id, guest_ids in by_old.items():
            self.__buildings[node_id].remove_guests(guest_ids)
        for node_id, guests in by_new.items():
            self.__buildings[node_id].add_rooms(guests)
        return [{"channel_id": guest.guest_id[0], "sequence_id": guest.guest_id[1],
                 "old_node_id": old_id, "new_node_id": new_id, "room_no": room_no}
                for guest, old_id, new_id, room_no in moves]

    def search_guest_by_room_id_and_building_id(self, node_id: int, room_no: int):
        building = self.__buildings.get(node_id)
        if building is None:
            return "NodeID not found"
        index = bisect.bisect_left(building.get_RoomAddr, room_no, key=lambda room: room.room_no)
        if index == len(building.get_RoomAddr) or building.get_RoomAddr[index].room_no != room_no:
            return "RoomNo not found"
        guest = building.get_RoomAddr[index].guest
        return guest.guest_id if guest is not None else "RoomNo not found"

    def show_occupied_room(self):
        if not self.__buildings:
            return "No existing building yet"
        return [room for building in sorted(self.__buildings.values(), key=lambda item: item.get_node_id)
                for room in building.get_RoomAddr]

    def show_load_balance_report(self):
        return Report.load_balance(list(self.__buildings.values()), len(self.__guest))

    def run_benchmark(self):
        result = {"guest_count": len(self.__guest), "building_count": len(self.__buildings)}
        if not self.__guest:
            result.update({"search_1000_avg_seconds": None, "sorted_room_listing_seconds": None})
            return result
        search_ids = [guest.guest_id for guest in self.__guest]
        start = time.perf_counter()
        for index in range(1_000):
            self.search_guest_location(*search_ids[index % len(search_ids)])
        result["search_1000_avg_seconds"] = (time.perf_counter() - start) / 1_000
        start = time.perf_counter()
        self.show_occupied_room()
        result["sorted_room_listing_seconds"] = time.perf_counter() - start
        return result

    def export_guest_csv(self, filename: str = "guest.csv") -> None:
        data = [{"channel_id": guest.guest_id[0], "sequence_id": guest.guest_id[1],
                 "node_id": guest.get_room.node_id, "room_no": guest.get_room.room_no}
                for guest in self.__guest if guest.get_room is not None]
        CSVExporter.write_csv(filename, data,
                              ["channel_id", "sequence_id", "node_id", "room_no"])

    def export_migration_csv(self, filename: str, history: list[dict] | None = None) -> None:
        rows = self.__last_migration if history is None else history
        fields = ["channel_id", "sequence_id", "old_node_id", "new_node_id", "room_no"]
        CSVExporter.write_csv(filename, rows, fields)

    def export_experiment_csv(self, filename: str = "experiment.csv") -> None:
        data = [{"guest_count": len(self.__guest), "building_count": len(self.__buildings)}]
        CSVExporter.write_csv(filename, data, ["guest_count", "building_count"])
