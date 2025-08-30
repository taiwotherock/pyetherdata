# import dependencies
#

from web3 import Web3, HTTPProvider
from ethdecode import extract_data
from hexbytes import HexBytes

# instantiate a web3 remote provider

#w3 = Web3(HTTPProvider(''))

# request the latest block number
#ending_blocknumber = w3.eth.block_number

# latest block number minus 100 blocks
#starting_blocknumber = ending_blocknumber - 100 

# filter through blocks and look for transactions involving this address
#blockchain_address = "0x16db2fcc2bd501a1518654cfa44ab2a93dd36ffc"

# create an empty dictionary we will add transaction data to
tx_dictionary = {}

def fetchTransaction(wallet_address, chainEndpoint):
    print(wallet_address + " " + chainEndpoint)
    w3 = Web3(HTTPProvider(chainEndpoint))
    ending_blocknumber = w3.eth.block_number
    starting_blocknumber = ending_blocknumber - 1000
    return getTransactions(starting_blocknumber, ending_blocknumber, wallet_address,w3)



def getTransactions(start, end, address,w3):
    
  
    print(f"Started filtering through block number {start} to {end} for transactions involving {address}...")

    for block_number in range(start, end + 1):
            block = w3.eth.get_block(block_number, full_transactions=True)
            print('no txn ' + str(block_number) + " " + str(len(block["transactions"])) )
            
            ik =0
            wallet_addr = address[2:]
            print("wallet_addr " + wallet_addr)
            for tx in block.transactions:
                #print(tx)
                #decodetran(tx["input"])
                #extract_data(tx["input"])
                ik = ik + 1
                txHash = HexBytes(tx["blockHash"])
                
                txInput = HexBytes(tx["input"])
                #0xb167c51a789d4d7f7eab44af026104d8858929b3|0x16db2fcc2bd501a1518654cfa44ab2a93dd36ffc
                if(txInput.hex().find(wallet_addr) > 0 ):
                    print(str(ik) + '  txHash: ' + txHash.hex())
                    print('hash: ' + HexBytes(tx["hash"]).hex() )
                    print('from: ' + HexBytes(tx["r"]).hex() )
                    print('to: ' + HexBytes(tx["s"]).hex() )
                    print(txInput.hex())
                    print(tx)
                    return HexBytes(tx["hash"]).hex()
    return ""
                
              


#getTransactions(starting_blocknumber, ending_blocknumber, blockchain_address)

#getTransactions(30384884, 30384884, blockchain_address)

30384884