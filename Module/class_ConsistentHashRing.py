import hashlib

class ConsistentHashRing:
    def __int__(self,Vnode):
        self.__list = []
    @property
    def get_Vnode(self):
        return self.__Vnode
    
    def add_node(self,building):
        node = VNode(building)
        rank = building.add_vnode(node)
        node_id = building.get_node_id()
        node.assign_node_seq(rank)
        text = f"{node_id}:{rank}"
        salt = "ball"
        combined_text = f"{text}{salt}"
        hash_obj = hashlib.sha256(combined_text.encode('utf-8'))

        bin_64bit = hash_obj.digest()[:8]
        position_on_ring = int.from_bytes(bin_64bit, byteorder='big')

        node.assign_hash_key(position_on_ring)

        pass
    def remove_node(self):
        pass