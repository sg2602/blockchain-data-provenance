import ipfshttpclient
import hashlib
from web3 import Web3
from config import GANACHE_URL, CONTRACT_ABI, CONTRACT_ADDRESS
import sys
import os

# --- SCRIPT SETUP ---
# This script is for the DATA OWNER (Account 0)
# It uploads a file to IPFS and registers it on the blockchain.
#
# Usage:
# python agent.py <dataset_id> <path_to_file>
#
# Example:
# python agent.py diabetes_v3 dataset.csv
# --------------------

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    print("🔴 FAILED to connect to Ganache.")
    sys.exit()

# Set the default account (Account 0) as the "Data Owner"
owner_account = w3.eth.accounts[0]
w3.eth.default_account = owner_account
print(f"🔗 Connected to Ganache as Owner: {owner_account}")

# Connect to the smart contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Connect to IPFS
try:
    client = ipfshttpclient.connect()
    print("Successfully connected to IPFS node.")
except Exception as e:
    print(f"🔴 FAILED to connect to IPFS: {e}")
    print("Please ensure IPFS Desktop is running.")
    sys.exit()


def register_dataset_with_ipfs(dataset_id, file_path):
    """
    Uploads a file to IPFS and registers its hashes on the blockchain.
    """
    if not os.path.exists(file_path):
        print(f"🔴 ERROR: File not found at '{file_path}'")
        return

    print(f"\n> Registering '{dataset_id}' from file '{file_path}'...")
    
    # 1. Upload to IPFS
    print(f"  - Uploading {file_path} to IPFS...")
    try:
        res = client.add(file_path)
        ipfs_cid = res['Hash']
        print(f"  - SUCCESS: File uploaded to IPFS. CID: {ipfs_cid}")
    except Exception as e:
        print(f"  - FAILED IPFS Upload: {e}")
        return

    # 2. Calculate SHA-256 hash
    print("  - Calculating SHA-256 hash...")
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            sha256_hash = hashlib.sha256(data).hexdigest()
            # Convert hex string to bytes32 for Solidity
            sha256_hash_bytes = bytes.fromhex(sha256_hash)
        print(f"  - Calculated SHA-256 hash: {sha256_hash}")
    except Exception as e:
        print(f"  - FAILED Hash Calculation: {e}")
        return

    # 3. Register on Blockchain
    print("  - Registering hashes on blockchain...")
    try:
        tx_hash = contract.functions.registerDataset(
            dataset_id,
            ipfs_cid,
            sha256_hash_bytes
        ).transact()
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"  - SUCCESS: All records stored on-chain. (Tx: {receipt.transactionHash.hex()})")
        print(f"  - Data Owner {owner_account} is automatically granted access.")
        
    except Exception as e:
        print(f"  - FAILED Blockchain Registration: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python agent.py <dataset_id> <path_to_file>")
        print("Example: python agent.py diabetes_v3 dataset.csv")
        sys.exit()

    dataset_id = sys.argv[1]
    file_path = sys.argv[2]
    
    register_dataset_with_ipfs(dataset_id, file_path)