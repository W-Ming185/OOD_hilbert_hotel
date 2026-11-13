from __future__ import annotations

from .Building import Building


class HashMod:
    """Mod-N building selector; insertion order defines each building's slot."""

    def __init__(self):
        self.__buildings: list[Building] = []

    @property
    def get_buildings(self) -> list[Building]:
        return self.__buildings

    @property
    def get_no_building(self) -> int:
        return len(self.__buildings)

    @property
    def no_building(self) -> int:
        return len(self.__buildings)

    def add_building(self, building: Building) -> None:
        if any(item.get_node_id == building.get_node_id for item in self.__buildings):
            raise ValueError(f"Building {building.get_node_id} already exists")
        self.__buildings.append(building)

    def remove_building(self, node_id: int) -> Building | None:
        for index, building in enumerate(self.__buildings):
            if building.get_node_id == node_id:
                return self.__buildings.pop(index)
        return None

    def calculate_index(self, hash_value: int) -> int:
        if not self.__buildings:
            raise ValueError("Cannot select a building when none exist")
        return hash_value % len(self.__buildings)

    def get_building(self, hash_value: int) -> Building:
        return self.__buildings[self.calculate_index(hash_value)]
