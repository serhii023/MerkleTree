import hashlib
import random
import time


LEFT = "left"
RIGHT = "right"


def get_hash(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
        # return (hashlib.sha256(data.encode('utf-8')).hexdigest())[0:4]

class IndexedMerkleTreeLeaf:
    def __init__(self, val: int=0, nextId: int=0, nextVal: int=0) -> None:
        self.parent: IndexedMerkleTreeNode = None

        self.change_values(val=val, nextId=nextId, nextVal=nextVal)

    def _update_hash(self):
        self._hash = get_hash(str(self.val) + str(self.nextId) + str(self.nextVal))

        if self.parent is not None:
            self.parent.update_hash()
    
    def change_values(self, nextId: int, nextVal: int, val: int=None):
        if val is not None:
            self._val = val
        
        self._nextId = nextId
        self._nextVal = nextVal

        self._update_hash()

    @property
    def hash(self):
        return self._hash

    @property
    def val(self):
        return self._val

    @property
    def nextId(self):
        return self._nextId

    @property
    def nextVal(self):
        return self._nextVal

    def __str__(self, level=0):
        ret = "\t" * level + self._hash + " <" + str(self.val) + ", " + str(self.nextId) + ", " + str(self.nextVal) + ">" + "\n"
        # ret = "\t" * level + self._hash + "\n"
        
        return ret


class IndexedMerkleTreeNode:
    def __init__(self, left, right) -> None:
        self.parent: IndexedMerkleTreeNode = None

        self.change_values(left=left, right=right)

    def update_hash(self) -> None:
        self._hash = get_hash(self.left.hash + self.right.hash)

        if self.parent is not None:
            self.parent.update_hash()
    
    def change_values(self, left, right) -> None:
        self.left = left
        self.right = right

        self.update_hash()

    @property
    def hash(self) -> str:
        return self._hash
    
    def __str__(self, level=0) -> str:
        ret = "\t" * level + self._hash + "\n"

        ret += self.left.__str__(level + 1)
        ret += self.right.__str__(level + 1)
        
        return ret


class IndexedMerkleTree:
    def __init__(self, height: int) -> None:
        self._height = height
        self._size = pow(2, height)
        
        self._generate_empty_tree(size=self._size)

    def _generate_empty_tree(self, size) -> None:
        self.leafs = [IndexedMerkleTreeLeaf(val=0, nextId=0, nextVal=0) for id in range(size)]
        self._first_empy_leaf_id = 1
        
        # self._update_root()
        nodes = self.leafs

        while len(nodes) > 1:
            parent_nodes = list()
            
            for i in range(0, len(nodes), 2):
                parent_nodes.append(IndexedMerkleTreeNode(left=nodes[i], right=nodes[i + 1]))
                nodes[i].parent = parent_nodes[-1]
                nodes[i + 1].parent = parent_nodes[-1]
            
            nodes = parent_nodes

        self.root = nodes[0]
    
    def add_leaf(self, val: int) -> None:
        if self._first_empy_leaf_id >= self._size:
            raise ValueError("No space")

        leafY = self.leafs[0]
        leafYId = 0
        while not(leafY.nextVal > val or leafY.nextVal == 0):
            leafYId = leafY.nextId
            leafY = self.leafs[leafY.nextId]

        self.leafs[self._first_empy_leaf_id].change_values(val=val, nextVal=leafY.nextVal, nextId=leafY.nextId)
        # self._update_root(changed_leaf_id=self._first_empy_leaf_id)

        leafY.change_values(nextId=self._first_empy_leaf_id, nextVal=val)
        # self._update_root(changed_leaf_id=leafYId)

        self._first_empy_leaf_id += 1

    def __str__(self) -> str:
        return self.root.__str__()
    
    def generate_inclusion_proof(self, val: int) -> list[tuple[str, str]]:
        leaf = self.leafs[0]
        while leaf.nextVal <= val and leaf.nextVal != 0:
            leaf = self.leafs[leaf.nextId]

        # proof_hash = get_hash(str(val) + str(leaf.nextId) + str(leaf.nextVal))
        low_nullifier = (leaf.val, leaf.nextId, leaf.nextVal)

        proof = []
        node = leaf
        while node.parent is not None:
            if node.hash == node.parent.left.hash:
                proof.append((node.parent.right.hash, RIGHT))
            else:
                proof.append((node.parent.left.hash, LEFT))

            node = node.parent

        # return proof, proof_hash
        return proof, low_nullifier

def check_proof(hash: str, proof: list[tuple[str, str]], root_hash: str):
    for (step_hash, step_ord) in proof:
        if step_ord == LEFT:
            hash = get_hash(step_hash + hash)
        
        if step_ord == RIGHT:
            hash = get_hash(hash + step_hash)
        
    return hash == root_hash

def check_inclusion_proof(value: int, node_values: tuple[int, int, int], proof: list[tuple[str, str]], root_hash: str):
    hash = get_hash(str(value) + str(node_values[1]) + str(node_values[2]))

    return check_proof(hash=hash, proof=proof, root_hash=root_hash)

def check_non_inclusion_proof(value: int, node_values: tuple[int, int, int], proof: list[tuple[str, str]], root_hash: str):
    hash = get_hash(str(node_values[0]) + str(node_values[1]) + str(node_values[2]))
    if check_proof(hash=hash, proof=proof, root_hash=root_hash):
        if value > node_values[0]:
            if node_values[0] < node_values[2] or node_values[2] == 0:
                return True
    
    return False

def main():
    print("Print example")
    height = 16
    tree = IndexedMerkleTree(height=height)

    data_piece = 5555

    for _ in range(pow(2, height-7) - 3):
        val = random.random()
        tree.add_leaf(val=val)

    # print(tree)
    # print(f"root hash = {tree.root.hash}")

    inc_proof, inc_node = tree.generate_inclusion_proof(val=data_piece)

    print(f"inclusion fail: {check_inclusion_proof(value=data_piece, node_values=inc_node, proof=inc_proof, root_hash=tree.root.hash)}")
    print(f"non inclusion success: {check_non_inclusion_proof(value=data_piece, node_values=inc_node, proof=inc_proof, root_hash=tree.root.hash)}")
    
    tree.add_leaf(val=data_piece)

    inc_proof, inc_node = tree.generate_inclusion_proof(val=data_piece)

    print(f"inclusion success: {check_inclusion_proof(value=data_piece, node_values=inc_node, proof=inc_proof, root_hash=tree.root.hash)}")
    print(f"non inclusion fail: {check_non_inclusion_proof(value=data_piece, node_values=inc_node, proof=inc_proof, root_hash=tree.root.hash)}")

if __name__ == "__main__":
    main()

