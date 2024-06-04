import hashlib
import random
import copy


LEFT = "left"
RIGHT = "right"


def get_hash(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
        # return (hashlib.sha256(data.encode('utf-8')).hexdigest())[0:4]

def ensure_even_list(data: list):
    if len(data) % 2 == 1:
        data.append(copy.copy(data[-1]))


class MerkleTreeNode:
    def __init__(self, hash: str=None, left=None, right=None) -> None:
        self.left = left
        self.right = right
        self.parent = None

        if left is not None and right is not None and hash is None:
            self.hash = get_hash(left.hash + right.hash)
        elif hash is not None: 
            self.hash = hash
        else:
            raise ValueError("value error")
    
    def __copy__(self):
        return MerkleTreeNode(hash=self.hash, left=self.left, right=self.right)
    
    def __str__(self, level=0):
        ret = "\t" * level + self.hash + "\n"

        if self.left is not None:
            ret += self.left.__str__(level + 1)

        if self.right is not None:
            ret += self.right.__str__(level + 1)
        
        return ret


class MerkleTree:
    def __init__(self, hashes: list) -> None:
        if len(hashes) == 0:
            return

        self.generate_tree(hashes=hashes.copy())

    def generate_tree(self, hashes):
        if len(hashes) == 0:
            return

        self.hashes = hashes
        self.leafs = [MerkleTreeNode(hash=hash) for hash in hashes]
        nodes = self.leafs
        ensure_even_list(nodes)

        while len(nodes) > 1:
            parent_nodes = []
            
            ensure_even_list(nodes)
            for i in range(0, len(nodes), 2):
                parent_nodes.append(MerkleTreeNode(left=nodes[i], right=nodes[i + 1]))
                nodes[i].parent = parent_nodes[-1]
                nodes[i + 1].parent = parent_nodes[-1]
            
            nodes = parent_nodes
        
        self.root = nodes[0]

    def __str__(self):
        return self.root.__str__()


    def generate_proof(self, hash: str):
        if len(self.hashes) == 0:
            return

        leaf_id = self.hashes.index(hash)
        node = self.leafs[leaf_id]
        proof = []
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
    data = [str(random.random())  for _ in range(pow(2, height))]
    hashes = [get_hash(data=d) for d in data]

    tree = MerkleTree(hashes=hashes)
    # print(tree)
    # print(f"root hash = {tree.root.hash}")

    hash = hashes[5777]
    proof = tree.generate_proof(hash=hash)
    # for step in proof: print(step)
    
    print("inclusion success:", check_proof(hash=hash, proof=proof, root_hash=tree.root.hash))
    print("inclusion fail:", check_proof(hash=get_hash(data="ghtjd"), proof=proof, root_hash=tree.root.hash))

    proof[0] = (proof[0][0], RIGHT if proof[0][1] == LEFT else LEFT)
    print("inclusion fail:", check_proof(hash=hash, proof=proof, root_hash=tree.root.hash))

if __name__ == "__main__":
    main()


