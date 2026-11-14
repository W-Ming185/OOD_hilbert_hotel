import csv
import os
import tempfile
import unittest
from Module.hotelsystem import HotelSystem
from unittest import mock
from Module.ConsistentHashRing import ConsistentHashRing

METHODS = ["consistent", "modn"]
BRIEF_IDS = [(1, 1), (2, 1), (1, 2), (3, 1), (2, 2)]    # room_no must be 1,2,3,4,5

def make(method, n=5, v=8, guests_per_channel=40, channels=3):
    h = HotelSystem(method)
    h.set_salt("0")
    h.set_vnode_size(v)
    for i in range(1, n + 1):
        h.add_building(i)
    for c in range(1, channels + 1):
        h.add_guest_batch(c, 1, guests_per_channel)
    return h

def where(h):
    return {g.guest_id: g.get_room.node_id for g in h.guest}

def rooms(h):
    return {g.guest_id: g.get_room.room_no for g in h.guest}

class TestBothMethods(unittest.TestCase):
    def test_room_number_examples(self):
        for m in METHODS:
            with self.subTest(m):
                h = HotelSystem(m); h.set_salt("0"); h.set_vnode_size(4); h.add_building(1)
                for g in BRIEF_IDS:
                    h.add_guest_single(*g)
                self.assertEqual([h.search_guest_location(g)[1] for g in BRIEF_IDS], [1, 2, 3, 4, 5])

    def test_add_building_only_moves_to_new_building_and_rooms_stay(self):
        for m in METHODS:
            with self.subTest(m):
                h = make(m)
                before_w, before_r = where(h), rooms(h)
                _, hist = h.add_building(6)
                after_w = where(h)
                moved = {k for k in before_w if before_w[k] != after_w[k]}
                self.assertEqual(len(hist or []), len(moved))              # reported == real
                self.assertEqual(len(h.last_migration), len(moved))
                self.assertEqual(rooms(h), before_r)                       # room_no unchanged
                self.assertEqual(len(h.guest), 120)                        # nobody lost
                if m == "consistent":
                    self.assertTrue(all(after_w[k] == 6 for k in moved))   # only INTO the new building

    def test_remove_building_only_moves_its_guests_for_consistent(self):
        h = make("consistent")
        before = where(h)
        _, hist = h.remove_building(3)
        after = where(h)
        moved = {k for k in before if before[k] != after[k]}
        self.assertEqual(moved, {k for k in before if before[k] == 3})
        self.assertEqual(len(hist or []), len(moved))
        self.assertTrue(all(node != 3 for node in after.values()))

    def test_modn_uses_hash_mod_n_in_insertion_order(self):
        h = make("modn")
        order = [b.get_node_id for b in h.hashmod.get_buildings]
        self.assertEqual(order, [1, 2, 3, 4, 5])
        for g in h.guest:
            self.assertEqual(g.get_room.node_id, order[g.get_hash_value % 5])
        h.remove_building(2)
        order = [b.get_node_id for b in h.hashmod.get_buildings]
        self.assertEqual(order, [1, 3, 4, 5])
        for g in h.guest:
            self.assertEqual(g.get_room.node_id, order[g.get_hash_value % 4])

    def test_same_hash_for_both_methods(self):
        a, b = make("consistent"), make("modn")
        self.assertEqual([g.get_hash_value for g in a.guest], [g.get_hash_value for g in b.guest])

    def test_edge_cases(self):
        for m in METHODS:
            with self.subTest(m):
                h = HotelSystem(m); h.set_salt("0"); h.set_vnode_size(4)
                h.add_guest_single(1, 1)                                   # no building -> no crash
                self.assertEqual(len(h.guest), 0)
                h.add_building(1)
                self.assertEqual(h.add_building(1), (None, None))          # duplicate building
                self.assertEqual(h.remove_building(9), (None, None))       # missing building
                self.assertEqual(h.remove_building(1), (None, None))       # last building
                h.add_guest_single(1, 1)
                self.assertEqual(h.add_guest_single(1, 1), "This id is already exist")
                n = len(h.guest)
                h.add_guest_batch(1, 1, 3)                                 # overlaps -> whole batch rejected
                self.assertEqual(len(h.guest), n)
                self.assertEqual(h.add_guest_batch(1, 5, 0), "Add Batch Succeed")   # n = 0 -> no change
                h.add_guest_single(0, 1)                                   # invalid id -> rejected
                self.assertEqual(len(h.guest), n)
                self.assertEqual(h.search_guest_location((9, 9)), "guest_id not found")
                self.assertEqual(h.search_guest_by_room_id_and_building_id(1, 999), "RoomNo Not found")
                self.assertEqual(h.search_guest_by_room_id_and_building_id(7, 1), "NodeID not found")
                self.assertEqual(h.remove_guest(1, 1), "Removal Succeed")
                self.assertEqual(h.remove_guest(1, 1), "This id does not exist for removal")
                self.assertEqual(h.search_guest_location((1, 1)), "guest_id not found")
                self.assertTrue(all(x[1] == 0 for x in h.show_load_balance_report()))   # K = 0 -> zeros, no crash

    def test_csv_rows_match_guests_and_migrations(self):
        for m in METHODS:
            with self.subTest(m):
                h = make(m)
                h.add_building(6)
                with tempfile.TemporaryDirectory() as d:
                    g, mg = os.path.join(d, "g.csv"), os.path.join(d, "m.csv")
                    h.export_guest_csv(g); h.export_migration_csv(mg)
                    with open(g, encoding="utf-8", newline="") as f:
                        rows = list(csv.DictReader(f))
                    self.assertEqual(len(rows), len(h.guest))
                    self.assertEqual(list(rows[0]), ["channel_id", "sequence_id", "node_id", "room_no"])
                    with open(mg, encoding="utf-8", newline="") as f:
                        self.assertEqual(len(list(csv.DictReader(f))), len(h.last_migration))

    def test_same_salt_gives_same_result_after_restart(self):
        for m in METHODS:
            with self.subTest(m):
                self.assertEqual(where(make(m)), where(make(m)))

NODE_POS = {"node:1:0": 20, "node:2:0": 50, "node:3:0": 80, "node:4:0": 35, "node:5:0": 20}
GUEST_POS = {(1, i + 1): p for i, p in enumerate([10, 20, 25, 35, 50, 70, 90])}
INITIAL = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3, 7: 1}      # guest s -> building (brief section 9.1)

def fixed_ring_system():
    h = HotelSystem("consistent"); h.set_vnode_size(1)
    for b in (1, 2, 3):
        h.add_building(b)
    for s in range(1, 8):
        h.add_guest_single(1, s)
    return h

def owners(h):
    return {s: h.search_guest_location((1, s))[0] for s in range(1, 8)}

class TestFixedRing(unittest.TestCase):
    def setUp(self):
        p1 = mock.patch.object(ConsistentHashRing, "_node_position", lambda self, t: NODE_POS[t])
        p2 = mock.patch.object(HotelSystem, "_hash_guest", lambda self, c, s: GUEST_POS[(c, s)])
        p1.start(); p2.start(); self.addCleanup(p1.stop); self.addCleanup(p2.stop)

    def test_initial_lookup_boundary_between_and_wraparound(self):
        # 20 and 50 sit exactly on a building point, 25/35/70 are between points, 90 wraps to A
        self.assertEqual(owners(fixed_ring_system()), INITIAL)

    def test_add_D_moves_two_and_rooms_stay(self):
        h = fixed_ring_system()
        rooms_before = rooms(h)
        _, hist = h.add_building(4)
        self.assertEqual(owners(h), {1: 1, 2: 1, 3: 4, 4: 4, 5: 2, 6: 3, 7: 1})
        self.assertEqual(len(hist), 2)
        self.assertEqual(rooms(h), rooms_before)

    def test_remove_B_moves_three_and_rooms_stay(self):
        h = fixed_ring_system()
        rooms_before = rooms(h)
        _, hist = h.remove_building(2)
        self.assertEqual(owners(h), {1: 1, 2: 1, 3: 3, 4: 3, 5: 3, 6: 3, 7: 1})
        self.assertEqual(len(hist), 3)
        self.assertEqual(rooms(h), rooms_before)

    def test_virtual_node_collision_uses_node_id_order(self):
        h = fixed_ring_system()
        h.add_building(5)                       # also at position 20 -> ties with building 1
        self.assertEqual(owners(h), INITIAL)    # tie-break (position, node_id, j): building 1 wins
        self.assertEqual(len(h.last_migration), 0)
        

class TestGuestAdditionAndRooms(unittest.TestCase):
    def test_adding_guests_never_moves_existing(self):
        for m in METHODS:
            with self.subTest(m):
                h = make(m)
                w, r = where(h), rooms(h)
                h.add_guest_batch(1, 41, 20)    # existing channel
                h.add_guest_batch(9, 1, 20)     # new channel
                w2, r2 = where(h), rooms(h)
                self.assertTrue(all(w2[k] == w[k] and r2[k] == r[k] for k in w))
                self.assertEqual(len(h.guest), 160)

    def test_room_numbers_unique_for_different_ids(self):
        h = make("consistent", n=1, v=4, guests_per_channel=60, channels=10)   # one building -> all rooms in it
        nums = [g.get_room.room_no for g in h.guest]
        self.assertEqual(len(nums), len(set(nums)))
        self.assertEqual(h.search_guest_location((4, 3))[1], 18)               # a=3,b=2 -> (5*6)//2+2+1

if __name__ == "__main__":
    unittest.main(verbosity=2)
