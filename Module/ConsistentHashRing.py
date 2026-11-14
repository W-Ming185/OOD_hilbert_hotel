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

    def _node_position(self, text):      # separate method so tests can override it
        return int.from_bytes(hashlib.sha256(text.encode('utf-8')).digest()[:8], byteorder='big')
    
    def add_node(self,building,salt):
        node = VNode(building)
        j = building.get_Vnode_rank          # count BEFORE adding -> j = 0..V-1
        building.add_vnode(node)
        node_id = building.get_node_id
        node.assign_node_seq(j)
        position_on_ring = self._node_position(f"node:{node_id}:{j}{salt}")

        node.assign_hash_key(position_on_ring)
        # tie-break on (position, node_id, j) as the brief requires
        bisect.insort(self.__list, node, key=lambda x: (x.get_hash_key, x.get_building.get_node_id, x.get_node_seq))
        return node

    def remove_node(self, building):
        all_vnode = building.get_Vnode
        for vnode in all_vnode:
            self.__list.remove(vnode)

        return all_vnode

    def get_vnode_for_guest(self,hash_value): #binary search treeได้
        if not self.__list:
            return None
        index = bisect.bisect_left(self.__list, hash_value, key=lambda x: x.get_hash_key)
        if index >= len(self.__list):
            index = 0
        return self.__list[index]

    def prev_vnode(self,vnode):
        index = self.__list.index(vnode)
        return self.__list[index-1]

    def next_vnode(self,vnode):
        index = self.__list.index(vnode)
        return self.__list[(index+1) % len(self.__list)]