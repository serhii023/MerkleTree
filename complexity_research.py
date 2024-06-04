import time
import random
import hashlib

from src import BinaryMerkleTree as bmt
from src import SparseMerkleTree as smt
from src import IndexedMerkleTree as imt

def get_hash(data: str) -> str:
        return hashlib.sha3_512(data.encode('utf-8')).hexdigest()
        # return hashlib.sha256(data.encode('utf-8')).hexdigest()
        # return (hashlib.sha256(data.encode('utf-8')).hexdigest())[0:4]

"""TODO: need to test: append new element, generate proof, verify"""


def binary_Merkle_tree_time_example(height: int = 16, repeat=10):
    print("Binary Merkle tree time example")
    size = pow(2, height)


    # test appending element
    total = 0
    for r in range(repeat):
        hashes = [get_hash(str(random.random())) for _ in range(size)]
        
        start = time.time()
        tree = bmt.MerkleTree(hashes=hashes)
        finish = time.time()
        
        total += finish - start
    print(f"Append new element: {total / repeat}s.")

    # chose some tree
    hashes = [get_hash(str(random.random())) for _ in range(size)]
    tree = bmt.MerkleTree(hashes=hashes)

    # test generate proof
    total = 0
    for r in range(repeat):
        hash = random.choice(hashes)
        
        start = time.time()
        proof = tree.generate_proof(hash=hash)
        finish = time.time()
        
        total += finish - start
    print(f"Generate proof: {total / repeat}s.")

    # verify
    total = 0
    for r in range(repeat):
        hash = hashes[random.randint(a=0, b=size - 1)]
        
        start = time.time()
        proof_res = bmt.check_proof(hash=hash, proof=proof, root_hash=tree.root.hash)
        finish = time.time()
        
        total += finish - start
    print(f"Check proof: {total / repeat}s.")
    
    print("")

def sparse_Merkle_tree_time_example(height: int = 16, repeat=10):
    print("Sparse Merkle tree time example")
    size = pow(2, height)

    # Create tree
    tree = smt.SparseMerkleTree(height=height)

    # test appending of element 
    total = 0
    for r in range(repeat):
        hash = get_hash(str(random.random()))
        id = random.randint(a=0, b=size - 1)

        start = time.time()
        tree.add_leaf(hash=hash, id=id)
        finish = time.time()
        
        total += finish - start
    print(f"Append new element: {total / repeat}s.")


    # generate proof
    total = 0
    for r in range(repeat):
        id = random.randint(a=0, b=size - 1)

        start = time.time()
        proof = tree.generate_inclusion_proof(id=id)
        finish = time.time()
    
        total += finish - start
    print(f"Generate proof: {total / repeat}s.")

    # verify
    total = 0
    for r in range(repeat):
        hash = get_hash(str(random.random()))

        start = time.time()
        proof_res = smt.check_proof(hash=hash, proof=proof, root_hash=tree.root.hash)
        finish = time.time()
    
        total += finish - start
    print(f"Check proof: {total / repeat}s.")
    
    print("")

def indexed_Merkle_tree_time_example(height: int = 16, repeat=10):
    print("Indexed Merkle tree time example")
    size = pow(2, height)

    # Create tree
    tree = imt.IndexedMerkleTree(height=height)
    
    # Create some random data
    some_data = [random.randint(a=1, b=pow(2, 10)) for _ in range(size)]

    # test appending of element 
    total = 0
    for r in range(repeat):
        val = random.choice(some_data)

        start = time.time()
        tree.add_leaf(val=val)
        finish = time.time()
        
        total += finish - start
    print(f"Append new element: {total / repeat}s.")


    # generate proof
    total = 0
    for r in range(repeat):
        val = random.choice(some_data)

        start = time.time()
        proof, hash_part = tree.generate_inclusion_proof(val=val)
        finish = time.time()
    
        total += finish - start
    print(f"Generate proof: {total / repeat}s.")

    # verify
    proof, hash_part = tree.generate_inclusion_proof(val=random.choice(some_data))
    total = 0
    for r in range(repeat):
        hash = get_hash(str(random.random()))

        start = time.time()
        proof_res = imt.check_proof(hash=hash, proof=proof, root_hash=tree.root.hash)
        finish = time.time()
    
        total += finish - start
    print(f"Check proof: {total / repeat}s.")
    
    print("")

def main():
    binary_Merkle_tree_time_example(repeat=5)
    sparse_Merkle_tree_time_example(repeat=pow(2, 10))
    indexed_Merkle_tree_time_example(repeat=pow(2, 10) - 2)

if __name__ == "__main__":
    main()


