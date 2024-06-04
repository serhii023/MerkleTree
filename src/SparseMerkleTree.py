import hashlib
import random


LEFT = "left"
RIGHT = "right"


def get_hash(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
        # return (hashlib.sha256(data.encode('utf-8')).hexdigest())[0:4]

class SparseMerkleTreeLeaf:
    def __init__(self, hash: str=None, id: int=None) -> None:
        self.parent: SparseMerkleTreeNode = None    
        self.id: int = id
        
        self.set_hash(hash=hash)

    def set_hash(self, hash: str):
        self._raw_hash = hash
        self._hash = get_hash(hash + str(self.id))

        if self.parent is not None:
            self.parent.update_hash()

    @property
    def hash(self):
        return self._hash

    def __str__(self, level=0):
        ret = "\t" * level + self._hash + " <---> " + str(self.id) + "\n"

        return ret

class SparseMerkleTreeNode:
    def __init__(self, hash: str=None, left=None, right=None) -> None:
        self.left: SparseMerkleTreeNode = left
        self.right: SparseMerkleTreeNode = right
        self.parent: SparseMerkleTreeNode = None
        
        self.update_hash()

    @property
    def hash(self):
        return self._hash

    def update_hash(self):
        self._hash = get_hash(self.left.hash + self.right.hash)
        
        if self.parent is not None:
            self.parent.update_hash()

    def change_values(self, left, right) -> None:
        self.left = left
        self.right = right

        self.update_hash()

    def __str__(self, level=0):
        ret = "\t" * level + self._hash + "\n"

        if self.left is not None:
            ret += self.left.__str__(level + 1)

        if self.right is not None:
            ret += self.right.__str__(level + 1)
        
        return ret


class SparseMerkleTree:
    def __init__(self, height: int) -> None:
        self._height = height
        self._size = pow(2, height)
        
        self._generate_empty_tree(size=self._size)

    def _generate_empty_tree(self, size) -> None:
        self.leafs = [SparseMerkleTreeLeaf(hash="", id=id) for id in range(size)]
        
        nodes = self.leafs

        while len(nodes) > 1:
            parent_nodes = list()
            
            for i in range(0, len(nodes), 2):
                parent_nodes.append(SparseMerkleTreeNode(left=nodes[i], right=nodes[i + 1]))
                nodes[i].parent = parent_nodes[-1]
                nodes[i + 1].parent = parent_nodes[-1]
            
            nodes = parent_nodes
        
        self.root = nodes[0]
    
    def add_leaf(self, hash, id) -> None:
        if id >= self._size:
            raise ValueError(f"index {id} is out of range")

        self.leafs[id].set_hash(hash=hash)

    def __str__(self):
        return self.root.__str__()
    
    def generate_inclusion_proof(self, id: int):
        if id >= self._size:
            raise ValueError(f"index {id} out of range")
        
        proof = []
        
        node = self.leafs[id]
        while node.parent is not None:
            if node.hash == node.parent.left.hash:
                proof.append((node.parent.right.hash, RIGHT))
            else:
                proof.append((node.parent.left.hash, LEFT))

            node = node.parent

        return proof


def check_proof(hash: str, proof: list[tuple[str, str]], root_hash: str):
    for (step_hash, step_ord) in proof:
        if step_ord == LEFT:
            hash = get_hash(step_hash + hash)
        
        if step_ord == RIGHT:
            hash = get_hash(hash + step_hash)
        
    return hash == root_hash


def main():
    print("Print example")
    height = 16
    data = list()
    for i in range(pow(2, height)):
        if i != 5:
            data.append((get_hash(str(random.random())), i))


    tree = SparseMerkleTree(height=height)
    # print(f"root hash = {tree.root._hash}")

    for hash, id in data:
        tree.add_leaf(hash=hash, id=id)

    raw_hash = get_hash("fff")
    hash = get_hash(raw_hash + str(5))
    non_hash = get_hash(str(5))
    
    proof = tree.generate_inclusion_proof(id=5)
    # print(tree)
    # for step in proof: print(step)
    print(f"inclusion fail: {check_proof(proof=proof, hash=hash, root_hash=tree.root._hash)}")
    print(f"non-inclusion success: {check_proof(proof=proof, hash=non_hash, root_hash=tree.root._hash)}")
    
    tree.add_leaf(hash=raw_hash, id=5)
    print(f"inclusion success: {check_proof(proof=proof, hash=hash, root_hash=tree.root._hash)}")
    print(f"non-inclusion fail: {check_proof(proof=proof, hash=non_hash, root_hash=tree.root._hash)}")

if __name__ == "__main__":
    main()

