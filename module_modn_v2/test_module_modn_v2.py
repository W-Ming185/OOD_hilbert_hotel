import unittest
from module_modn_v2.hotelsystem import HotelSystem

IDS = [(1, 1), (2, 1), (1, 2), (3, 1), (2, 2)]

class TestModN(unittest.TestCase):
    def make(self, n=5):
        h = HotelSystem()
        h.set_salt("0")
        for i in range(1, n + 1):
            h.add_building(i)
        for c, s in IDS:
            h.add_guest_single(c, s)
        return h

    def test_mod_n_selection(self):
        h = self.make()
        ids = [b.get_node_id for b in h.hashmod.get_buildings]
        for g in h.guest:
            self.assertEqual(g.get_room.node_id, ids[g.get_hash_value % len(ids)])

    def test_room_numbers(self):
        h = HotelSystem(); h.set_salt("0"); h.add_building(1)
        for c, s in IDS:
            h.add_guest_single(c, s)
        self.assertEqual([h.search_guest_location(i)[1] for i in IDS], [1, 2, 3, 4, 5])

    def test_migration_add_remove(self):
        h = self.make()
        _, hist = h.add_building(6)
        for g in h.guest:
            self.assertEqual(g.get_room.node_id, [1,2,3,4,5,6][g.get_hash_value % 6])
        _, hist = h.remove_building(3)
        for g in h.guest:
            self.assertEqual(g.get_room.node_id, [1,2,4,5,6][g.get_hash_value % 5])
        self.assertEqual(sum(len(b.get_RoomAddr) for b in h.hashmod.get_buildings), len(IDS))

    def test_edge_cases(self):
        h = HotelSystem()
        self.assertIn("Cannot", h.add_guest_single(1, 1))
        h.add_building(1)
        self.assertEqual(h.add_building(1), (None, None))
        self.assertEqual(h.remove_building(1), (None, None))   # last building
        self.assertEqual(h.remove_building(9), (None, None))
        h.add_guest_single(1, 1)
        self.assertEqual(h.add_guest_single(1, 1), "This id is already exist")
        self.assertEqual(h.add_guest_batch(1, 1, 2), "There is some guest in this range already")
        self.assertEqual(h.search_guest_location((5, 5)), "guest_id not found")
        self.assertEqual(h.search_guest_by_room_id_and_building_id(1, 99), "RoomNo Not found")
        self.assertEqual(h.search_guest_by_room_id_and_building_id(7, 1), "NodeID not found")
        self.assertEqual(h.remove_guest(1, 1), "Removal Succeed")
        self.assertEqual(h.remove_guest(1, 1), "This id does not exist for removal")

if __name__ == "__main__":
    unittest.main(verbosity=2)