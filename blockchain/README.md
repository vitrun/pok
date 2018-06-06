# A simple blockchain

### Requirements
* python 3.6

### Install
* pip install -r requirements.txt


### Concepts
#### Transaction
* Sends msg from one address to another

#### Block
* Collection of transactions, together with meta fields

#### Node
* A HTTP server that:
* Accepts new transactions and validates it
* Mines by putting all the pending transactions into a block
* Syncs transactions and blocks with peer nodes

#### Chain
* A list of blocks

#### Consensus
* Always choose the longest chain

#### Wallet
* Creates and submits new transactions to seed nodes
* Generates private keys and addresses
