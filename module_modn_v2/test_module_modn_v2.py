"""Mod-N correctness checks based on sections 4, 7.1 and 9.2 of the brief."""

import csv
import unittest
from decimal import Decimal
from pathlib import Path

from module_modn_v2.HotelCLI import HotelCLI
from module_modn_v2.hotelsystem import HotelSystem


GUEST_IDS_FROM_BRIEF = [(1, 1), (2, 1), (1, 2), (3, 1), (2, 2)]


class TestModuleModnV2(unittest.TestCase):
    def test_modn_selects_by_hash_remainder_and_preserves_building_order(self):
        hotel = HotelSystem(salt="0")
        for node_id in [1, 2, 3, 4, 5]:
            hotel.add_building(node_id)
        for guest_id in GUEST_IDS_FROM_BRIEF:
            hotel.add_guest_single(*guest_id)

        building_ids = [building.get_node_id for building in hotel.hashmod.get_buildings]
        self.assertEqual(building_ids, [1, 2, 3, 4, 5])
        for guest in hotel.guest:
            expected = building_ids[guest.get_hash_value % len(building_ids)]
            self.assertEqual(guest.get_room.node_id, expected)

        reopened = HotelSystem(salt="0")
        for node_id in [1, 2, 3, 4, 5]:
            reopened.add_building(node_id)
        for guest_id in GUEST_IDS_FROM_BRIEF:
            reopened.add_guest_single(*guest_id)
        self.assertEqual([g.get_hash_value for g in hotel.guest],
                         [g.get_hash_value for g in reopened.guest])

        hotel.remove_building(3)
        self.assertEqual([b.get_node_id for b in hotel.hashmod.get_buildings], [1, 2, 4, 5])

    def test_room_number_examples_and_unique_addresses(self):
        hotel = HotelSystem(salt="0")
        hotel.add_building(1)
        for guest_id in GUEST_IDS_FROM_BRIEF:
            hotel.add_guest_single(*guest_id)
        actual = [hotel.search_guest_location(*guest_id)[1] for guest_id in GUEST_IDS_FROM_BRIEF]
        self.assertEqual(actual, [1, 2, 3, 4, 5])
        self.assertEqual(len(actual), len(set(actual)))
        for guest_id in GUEST_IDS_FROM_BRIEF:
            node_id, room_no = hotel.search_guest_location(*guest_id)
            self.assertEqual(hotel.search_guest_by_room_id_and_building_id(node_id, room_no), guest_id)

    def test_room_listing_order_and_load_counts(self):
        hotel = HotelSystem(salt="0")
        for node_id in [3, 1, 2]:
            hotel.add_building(node_id)
        for guest_id in GUEST_IDS_FROM_BRIEF:
            hotel.add_guest_single(*guest_id)
        rooms = hotel.show_occupied_room()
        actual_order = [(room.node_id, room.room_no) for room in rooms]
        self.assertEqual(actual_order, sorted(actual_order))
        report = hotel.show_load_balance_report()
        self.assertEqual(sum(count for _, count in report["counts"]), len(hotel.guest))
        self.assertEqual([node_id for node_id, _ in report["counts"]], [3, 1, 2])

    def test_adding_guests_keeps_existing_rooms_stable(self):
        hotel = HotelSystem(salt="0")
        hotel.add_building(1)
        hotel.add_building(2)
        for guest_id in [(1, 1), (2, 1)]:
            hotel.add_guest_single(*guest_id)
        before = {guest_id: hotel.search_guest_location(*guest_id) for guest_id in [(1, 1), (2, 1)]}
        hotel.add_guest_single(1, 2)
        hotel.add_guest_single(3, 1)
        self.assertEqual({guest_id: hotel.search_guest_location(*guest_id) for guest_id in before}, before)

    def test_duplicate_guest_and_partial_batch_rejection_are_atomic(self):
        hotel = HotelSystem(salt="0")
        hotel.add_building(1)
        hotel.add_guest_single(1, 2)
        before = hotel.guest_data_list
        self.assertEqual(hotel.add_guest_single(1, 2), "This id is already exist")
        self.assertEqual(hotel.add_guest_batch(1, 1, 2), "There is some guest in this range already")
        self.assertEqual(hotel.guest_data_list, before)
        self.assertEqual(hotel.add_guest_batch(1, 3, 0), "Add Batch Succeed")
        self.assertEqual(hotel.guest_data_list, before)

    def test_add_remove_building_reports_exact_modn_migrations(self):
        # N=5 is one of the specified Mod-N experiment settings in section 7.1.
        hotel = HotelSystem(salt="0")
        for node_id in [1, 2, 3, 4, 5]:
            hotel.add_building(node_id)
        for guest_id in GUEST_IDS_FROM_BRIEF:
            hotel.add_guest_single(*guest_id)

        before_add = {g.guest_id: (g.get_hash_value, g.get_room.node_id, g.get_room.room_no)
                      for g in hotel.guest}
        hotel.add_building(6)
        add_order = [1, 2, 3, 4, 5, 6]
        expected_add = {}
        for guest_id, (hash_value, old_node, room_no) in before_add.items():
            new_node = add_order[hash_value % len(add_order)]
            if new_node != old_node:
                expected_add[guest_id] = (old_node, new_node, room_no)
        actual_add = {(row["channel_id"], row["sequence_id"]):
                      (row["old_node_id"], row["new_node_id"], row["room_no"])
                      for row in hotel.last_migration}
        self.assertEqual(actual_add, expected_add)
        self.assertEqual(hotel.last_migration_count, len(expected_add))
        self.assertEqual(len(hotel.guest), len(GUEST_IDS_FROM_BRIEF))
        self.assertEqual(hotel.last_migration_rate,
                         Decimal(hotel.last_migration_count) / Decimal(len(GUEST_IDS_FROM_BRIEF)))

        before_remove = {g.guest_id: (g.get_hash_value, g.get_room.node_id, g.get_room.room_no)
                         for g in hotel.guest}
        hotel.remove_building(3)
        remove_order = [1, 2, 4, 5, 6]
        expected_remove = {}
        for guest_id, (hash_value, old_node, room_no) in before_remove.items():
            new_node = remove_order[hash_value % len(remove_order)]
            if new_node != old_node:
                expected_remove[guest_id] = (old_node, new_node, room_no)
        actual_remove = {(row["channel_id"], row["sequence_id"]):
                         (row["old_node_id"], row["new_node_id"], row["room_no"])
                         for row in hotel.last_migration}
        self.assertEqual(actual_remove, expected_remove)
        self.assertEqual(hotel.last_migration_count, len(expected_remove))
        self.assertEqual(len(hotel.guest), len(GUEST_IDS_FROM_BRIEF))
        self.assertTrue(all(g.get_room.room_no == before_remove[g.guest_id][2] for g in hotel.guest))

    def test_edge_cases_search_report_and_csv(self):
        empty_system = HotelSystem(salt="0")
        self.assertIn("No Building", empty_system.add_guest_single(1, 1))

        hotel = HotelSystem(salt="0")
        hotel.add_building(1)
        hotel.add_guest_single(1, 1)
        before = hotel.guest_data_list
        self.assertIn("already exists", hotel.add_building(1))
        self.assertEqual(hotel.guest_data_list, before)
        self.assertIn("not exist", hotel.remove_building(4))
        self.assertEqual(hotel.last_migration_count, 0)
        self.assertEqual(hotel.guest_data_list, before)
        self.assertEqual(hotel.remove_building(1), "This is The Last Building")
        self.assertEqual(hotel.guest_data_list, before)
        self.assertEqual(hotel.remove_guest(2, 2), "This id does not exist for removal")
        self.assertEqual(hotel.search_guest_location(2, 2), "guest_id not found")
        self.assertEqual(hotel.search_guest_by_room_id_and_building_id(1, 5), "RoomNo not found")
        self.assertEqual(hotel.search_guest_by_room_id_and_building_id(4, 1), "NodeID not found")
        old_location = hotel.search_guest_location(1, 1)
        self.assertEqual(hotel.remove_guest(1, 1), "Removal Succeed")
        self.assertEqual(hotel.search_guest_location(1, 1), "guest_id not found")
        self.assertEqual(hotel.add_guest_single(1, 1), "Add Guest Succeed")
        self.assertEqual(hotel.search_guest_location(1, 1), old_location)
        benchmark = hotel.run_benchmark()
        self.assertEqual(benchmark["guest_count"], 1)
        self.assertEqual(benchmark["building_count"], 1)
        self.assertEqual(benchmark["search_1000_avg_seconds"] is not None, True)

        empty_hotel = HotelSystem(salt="0")
        empty_hotel.add_building(1)
        report = empty_hotel.show_load_balance_report()
        self.assertEqual(report["counts"], [(1, 0)])
        self.assertEqual(report["total"], 0)
        self.assertIsNone(empty_hotel.last_migration_rate)
        self.assertEqual(empty_hotel.remove_building(1), "This is The Last Building")
        self.assertIn(1, empty_hotel.buildings)
        self.assertEqual(HotelCLI(HotelSystem()).get_system.guest, [])

        output = Path(__file__).with_name("_test_guests.csv")
        try:
            hotel.export_guest_csv(str(output))
            with output.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), len(hotel.guest))
            self.assertEqual(list(rows[0]), ["channel_id", "sequence_id", "node_id", "room_no"])
        finally:
            output.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
