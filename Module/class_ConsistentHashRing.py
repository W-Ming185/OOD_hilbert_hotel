import hashlib
import bisect
from vnode import VNode

class ConsistentHashRing:
    def __init__(self,vnode_size):
        self.__list = []
        self.__vnode_size = vnode_size
    @property
    def get_Vnode(self):
        return self.__list
    @property
    def get_vnode_size(self):
        return self.__vnode_size
    
    def add_node(self,building):
        node = VNode(building)
        building.add_vnode(node)
        rank = building.get_Vnode_rank
        node_id = building.get_node_id
        node.assign_node_seq(rank)
        text = f"{node_id}:{rank}"
        salt = "ball"
        combined_text = f"{text}{salt}"
        hash_obj = hashlib.sha256(combined_text.encode('utf-8'))

        bin_64bit = hash_obj.digest()[:8]
        position_on_ring = int.from_bytes(bin_64bit, byteorder='big')

        node.assign_hash_key(position_on_ring)
        bisect.insort(self.__list, node, key=lambda x: x.get_hash_key())
        return node


        pass
    def remove_node(self, building):
        all_vnode = building.get_Vnode
        for vnode in all_vnode:
            self.__list.remove(vnode)

        return all_vnode
