

import json
from web3 import Web3

# ============================================================
# CONFIG
# ============================================================

RPC_URL = "http://127.0.0.1:7545"

with open("../app_config.json", "r") as f:
    config = json.load(f)

CORE_CONTRACT_ADDRESS = config["LibraryCore"]
COIN_CONTRACT_ADDRESS = config["LibraryCoin"]

CORE_ABI_PATH = "../LibraryCore.json"

# LibraryCoin ABI — hardcoded because the JSON in the repo is wrong
COIN_ABI = [
    {"inputs": [{"name": "", "type": "address"}], "name": "balanceOf",
     "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "mint", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
     "name": "transfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "admin",
     "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalSupply",
     "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
]


# ============================================================
# SETUP
# ============================================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def load_contract_from_file(address, abi_path):
    with open(abi_path, "r") as f:
        data = json.load(f)
        abi = data["abi"] if "abi" in data else data
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

core = load_contract_from_file(CORE_CONTRACT_ADDRESS, CORE_ABI_PATH)
coin = w3.eth.contract(
    address=Web3.to_checksum_address(COIN_CONTRACT_ADDRESS),
    abi=COIN_ABI
)


# ============================================================
# FEATURE 1 — Balance Checker
# ============================================================

def check_balance(user_address):
    user_address = Web3.to_checksum_address(user_address)

    eth_wei = w3.eth.get_balance(user_address)
    eth_balance = w3.from_wei(eth_wei, "ether")

    coin_balance = coin.functions.balanceOf(user_address).call()

    print(f"\n--- Balance for {user_address} ---")
    print(f"ETH:          {eth_balance}")
    print(f"LibraryCoin:  {coin_balance}")
    print()


# ===================
if __name__ == "__main__":
    test_address = w3.eth.accounts[0]
    check_balance(test_address)