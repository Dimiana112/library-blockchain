import json
import os
from web3 import Web3

# ==========================================
# 1. Ganache Setup
# ==========================================
RPC_URL = "http://127.0.0.1:7545"
ADMIN_ADDRESS = Web3.to_checksum_address("0x2111E952d41346E72D9a2Bca147Ef0aECC7925AD")
PRIVATE_KEY = "0xc428070295ce6ae37a68b1a008ae694ddd569f70e891f1b7693bd4ca407a5110"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def deploy_contract(json_file, contract_name):
    if not w3.is_connected():
        print("Error: Failed to connect to Ganache!")
        return None

    if not os.path.exists(json_file):
        print(f"Error: Could not find '{json_file}'.")
        return None

    with open(json_file, 'r') as f:
        artifact = json.load(f)
    
    abi = artifact.get('abi')
    if not abi:
        print(f"Error: No 'abi' found in {json_file}")
        return None

    
    bytecode = None
    if 'bytecode' in artifact:
        bytecode = artifact['bytecode']
        if isinstance(bytecode, dict) and 'object' in bytecode:
            bytecode = bytecode['object']
    elif 'bin' in artifact:
        bytecode = artifact['bin']
    elif 'data' in artifact and 'bytecode' in artifact['data']:
        bytecode = artifact['data']['bytecode']['object']

    if not bytecode:
        print(f"Error: Could not find 'bytecode' or 'bin' in {json_file}")
        return None

  
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(ADMIN_ADDRESS)

    print(f"Deploying {contract_name}...")
    transaction = Contract.constructor().build_transaction({
        'chainId': w3.eth.chain_id,
        'gasPrice': w3.eth.gas_price,
        'from': ADMIN_ADDRESS,
        'nonce': nonce
    })

    try:  
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"[{contract_name}] Deployed at: {tx_receipt.contractAddress}\n")
        return tx_receipt.contractAddress
        
    except Exception as e:
        print(f"Transaction Error: {e}")
        return None

if __name__ == "__main__":
    print("=== Starting Deployment ===\n")
    
    coin_address = deploy_contract('LibraryCoin.json', 'LibraryCoin')
    core_address = deploy_contract('LibraryCore.json', 'LibraryCore')
    
    if core_address and coin_address:
        config_data = {
            "LibraryCoin": coin_address,
            "LibraryCore": core_address,
            "AdminAddress": ADMIN_ADDRESS
        }
        
        with open('app_config.json', 'w') as f:
            json.dump(config_data, f, indent=4)
            
        print("=====================================================")
        print("SUCCESS: Configuration saved to 'app_config.json'")
        print(f"CoreContract Address: {core_address}")
        print("=====================================================")
