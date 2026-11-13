import hashlib
import bisect
from Module.vnode import VNode
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
        bisect.insort(self.__list, node, key=lambda x: x.get_hash_key)
        return node

    def remove_node(self, building):
        all_vnode = building.get_Vnode
        for vnode in all_vnode:
            self.__list.remove(vnode)

        return all_vnode

    def get_vnode_for_guest(self,hash_value): #binary search treeได้
        index = bisect.bisect_left(self.__list, hash_value, key=lambda x: x.get_hash_key)
        if index >= len(self.__list):
            index = 0
        return self.__list[index]

    def prev_vnode(self,vnode):
        index = self.__list.index(vnode)
        return self.__list[index-1]

    def next_vnode(self,vnode):
        index = self.__list.index(vnode)
        return self.__list[index+1 % len(self.__list)]    