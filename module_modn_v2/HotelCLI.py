from __future__ import annotations

from .hotelsystem import HotelSystem


class HotelCLI:
    def __init__(self, system: HotelSystem):
        self.__system = system

    @property
    def get_system(self) -> HotelSystem:
        return self.__system

    @staticmethod
    def _read_int(prompt: str) -> int:
        return int(input(f"{prompt}: "))

    def _print_migration_report(self) -> None:
        system = self.__system
        print(f"Guests moved: {system.last_migration_count}")
        if system.last_migration_rate is None:
            print("Migration rate: not calculated (no guests)")
        else:
            print(f"Migration rate: {system.last_migration_rate}")
        for move in system.last_migration:
            print(f"Guest ({move['channel_id']}, {move['sequence_id']}): "
                  f"Building {move['old_node_id']} -> {move['new_node_id']}, "
                  f"room {move['room_no']}")

    def run(self) -> None:
        if not self.__system.buildings:
            self.__system.add_building(1)
        while True:
            print("\n[0] Quit  [1] Add guest  [2] Add building  [3] Remove guest\n"
                  "[4] Remove building  [5] List rooms  [6] Export CSV\n"
                  "[7] Load report  [8] Find guest  [9] Find room")
            choice = input("Enter: ").strip()
            try:
                if choice == "0":
                    return
                if choice == "1":
                    mode = input("[1] Batch [2] Single: ").strip()
                    if mode == "1":
                        print(self.__system.add_guest_batch(self._read_int("c"), self._read_int("s start"), self._read_int("count")))
                    elif mode == "2":
                        print(self.__system.add_guest_single(self._read_int("c"), self._read_int("s")))
                    else:
                        print("Invalid method")
                elif choice == "2":
                    print(self.__system.add_building(self._read_int("Building ID")))
                    self._print_migration_report()
                elif choice == "3":
                    print(self.__system.remove_guest(self._read_int("c"), self._read_int("s")))
                elif choice == "4":
                    print(self.__system.remove_building(self._read_int("Building ID")))
                    self._print_migration_report()
                elif choice == "5":
                    rooms = self.__system.show_occupied_room()
                    if isinstance(rooms, str):
                        print(rooms)
                        continue
                    for room in rooms:
                        print(room.node_id, room.room_no, room.guest.guest_id if room.guest else None)
                elif choice == "6":
                    self.__system.export_guest_csv()
                    print("Export complete")
                elif choice == "7":
                    print(self.__system.show_load_balance_report())
                elif choice == "8":
                    print(self.__system.search_guest_location(self._read_int("c"), self._read_int("s")))
                elif choice == "9":
                    print(self.__system.search_guest_by_room_id_and_building_id(self._read_int("Building ID"), self._read_int("Room number")))
                else:
                    print("Invalid input")
            except (TypeError, ValueError) as error:
                print(f"Invalid input: {error}")


def main() -> None:
    try:
        building_count = int(input("Initial building count N: "))
        channel_count = int(input("Number of channels: "))
        if building_count < 1 or channel_count < 1:
            raise ValueError("Building and channel counts must be positive")
        counts = {channel_id: int(input(f"Guest count for channel {channel_id}: "))
                  for channel_id in range(1, channel_count + 1)}
        system = HotelSystem(salt="0")
        system.initialize_system(list(range(1, building_count + 1)), counts)
    except (TypeError, ValueError) as error:
        print(f"Cannot initialize system: {error}")
        return
    HotelCLI(system).run()


if __name__ == "__main__":
    main()
