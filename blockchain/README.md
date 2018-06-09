# MsgChain
A simple block chain holding messages sent from one address to another.


## Requirements
* python 3.6

## Install
* pip install -r requirements.txt


## Concepts
#### Transaction
* Sends msg from one address to another
* Verifies the sender's signature to ensure authentication

#### Key
* Generates private keys and addresses

#### Block
* Collection of transactions, together with nonce, index, hash and previous block's hash

#### Chain
* A list of blocks

#### Consensus
* Proof of Work
* Always choose the longest chain

#### Node
* Accepts new transactions and validates it
* Mines new block by solving a encryption puzzle, difficulty is fixed
* Syncs transactions and blocks with peer nodes

## Usage

### CMD
* `python server.py key` to generate a new key pair
* `python server.py node $port` to start a node with HTTP API
    ```
    python server.py node  8081 --peers=http://localhost:8082
    ```

### API
* `GET /block/` to return all the blocks of the chain
* `POST /block/` to notify a new block
* `GET /chain/height/` to return the height of the chain
* `POST /transaction/` to create a new transaction
    ```
    curl -XPOST 'http://localhost:8081/transaction/' -d'{"sender_addr":"06971e14c6768c1962dece23204d6cf4dd5e085edbcaa08ac00ea1437e6b2c667c05655c4adbcf24a7a86288db3041d103d62a272c6494f32d784a332710bc3c5f","sender_public":"971e14c6768c1962dece23204d6cf4dd5e085edbcaa08ac00ea1437e6b2c667c05655c4adbcf24a7a86288db3041d103d62a272c6494f32d784a332710bc3c5f","recipient_addr":"06971e14c6768c1962dece23204d6cf4dd5e085edbcaa08ac00ea1437e6b2c667c05655c4adbcf24a7a86288db3041d103d62a272c6494f32d784a332710bc3c5f","payload":"hello world","sender_private":"cd4d401fcefbaf245ba79f647a3a65d9b0f468f77bc435f6b8a11157c75ab252"}'
    ```
* `POST /consensus/` to trigger consensus and resolve conflicts
* `POST /mine/` to trigger the mining

