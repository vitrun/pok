# Merkle Tree
Merkle tree is a tree in which every non-leaf node is labeled with the hash of the labels or values (in case of leaves) of its child nodes. Hash trees allow efficient and secure verification of the contents of large data structures. Hash trees are a generalization of hash lists and hash chains.
![](img/merkle_tree.png)

## Uses
* Check if the data belongs in the merkle tree
* To concisely prove the validity of data being part of a dataset without storing the whole data set
* To ensure the validity of a certain data set being inclusive in a larger data set without 
revealing either the complete data set or its subset.

### Examples
##### P2P download
Before downloading a file on a p2p network, in most cases the top hash is acquired from a trusted source, for instance a friend or a web site that is known to have good recommendations of files to download. When the top hash is available, the hash tree can be received from any non-trusted source, like any peer in the p2p network. Then, the received hash tree is checked against the trusted top hash, and if the hash tree is damaged or fake, another hash tree from another source will be tried until the program finds one that matches the top hash.

##### Bitcoin validation
Suppose we want to prove that transaction C was indeed in the block that formed the header shown above.
![](img/merkle_proof.jpeg)

In addition to the transaction hash C , we also need D, S(A,B), and S(S(E,F),S(G,H)) to form the proof. The verification itself performs the following steps on the proof:

* Hash C and D to produce S(C,D).
* Hash S(A,B) and S(C,D) to produce S(S(A,B),S(C,D)).
* Hash S(S(A,B),S(C,D)) and S(S(E,F),S(G,H)) to produce the root.
* Check that the root is the same as what has been stored previously.

The efficiency here is that we proved a transaction belonged in a block with only 3 accompanying pieces of information (instead of the 7 other transactions that were stored in the block). This efficiency becomes exponentially more pronounced with larger trees.

## Implementation
**Handling odd number**

For the case of Bitcoin, where Merkle Tree is used, in case the number of transactions is odd at some level of the tree then you just copy the element onto the right to form a pair.

**Create a new Merkle Tree from the list of Content**
```python
    tree = MerkleTree(['a', '3', '你'])
```
**Get the Merkle Root of the tree**
```python
    tree.root.val
```
**Verify the entire tree is valid**
```python
    tree.validate()
```
**Verify a specific content in in the tree**
```python
    tree.contains('你', 2)
```

## REF
* https://en.wikipedia.org/wiki/Merkle_tree
* https://brilliant.org/wiki/merkle-tree/
* https://github.com/Blockchain-for-Developers/merkle-tree**