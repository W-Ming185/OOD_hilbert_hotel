"""
import random
from Module.guest import Guest
from Module.RoomAddr import RoomAddr
from Module.CSVExporter import CSVExporter
from Module.hotelsystem import HotelSystem


def generate_test_data(n=100):
    guests = []
    for i in range(n):
        channel_id = i
        seat_id = random.randint(1, 50)
        hash_value = f"hash_{i:04d}"

        guest = Guest(channel_id, seat_id, hash_value)

        node_id = i // 20          # 5 nodes for 100 guests
        room_no = f"R{i % 20 + 1:03d}"  # e.g. R001..R020
        room = RoomAddr(node_id, room_no, guest)
        room.assign_guest(guest)
        guest.assign_room(room)

        guests.append(guest)

    return guests

def export_guest_csv(self):
    data = []
    for value in self.__guest:
        c, s = value.guest_id
        node_id = value.get_room.node_id
        room_no = value.get_room.room_no
        data.append({
            "channel_id": c,
            "seat_id": s,
            "node_id": node_id,
            "room_no": room_no,
        })

    CSVExporter.write_csv(
        "guest.csv", data,
        fieldnames=["channel_id", "seat_id", "node_id", "room_no"]
    )

if __name__ == "__main__":
    hotel = HotelSystem()
    test_guests = generate_test_data(100)
    export_guest_csv(test_guests)
    print("guest.csv written with", len(test_guests), "rows")

"""