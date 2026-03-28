from web3 import Web3
from config import GANACHE_URL, CONTRACT_ABI, CONTRACT_ADDRESS
import sys

# --- SCRIPT SETUP ---
# This script lets the data owner grant or revoke access
# for a specific AI agent (another address).
#
# Usage: 
# python admin.py grant <dataset_id> <agent_address>
# python admin.py revoke <dataset_id> <agent_address>
# --------------------

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    print("🔴 FAILED to connect to Ganache.")
    sys.exit()

# Get the owner account (Account 0 in Ganache)
# This is the account that deployed the contract.
owner_account = w3.eth.accounts[0]
w3.eth.default_account = owner_account

# Connect to the smart contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def grant_access(dataset_id, agent_address):
    print(f"🔑 Granting access for '{dataset_id}' to agent: {agent_address}...")
    try:
        # Call the 'grantAccess' function in the smart contract
        tx_hash = contract.functions.grantAccess(dataset_id, agent_address).transact()
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"  - SUCCESS: Access granted. (Tx: {receipt.transactionHash.hex()})")
    except Exception as e:
        print(f"  - FAILED: {e}")

def revoke_access(dataset_id, agent_address):
    print(f"🚫 Revoking access for '{dataset_id}' from agent: {agent_address}...")
    try:
        # Call the 'revokeAccess' function
        tx_hash = contract.functions.revokeAccess(dataset_id, agent_address).transact()
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"  - SUCCESS: Access revoked. (Tx: {receipt.transactionHash.hex()})")
    except Exception as e:
        print(f"  - FAILED: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python admin.py <grant|revoke> <dataset_id> <agent_address>")
        sys.exit()

    action = sys.argv[1].lower()
    dataset_id = sys.argv[2]
    agent_address_str = sys.argv[3]

    # Check if the address is valid
    if not w3.is_address(agent_address_str):
        print(f"🔴 ERROR: Invalid agent address: {agent_address_str}")
        sys.exit()

    agent_address = w3.to_checksum_address(agent_address_str)

    if action == "grant":
        grant_access(dataset_id, agent_address)
    elif action == "revoke":
        revoke_access(dataset_id, agent_address)
    else:
        print(f"🔴 ERROR: Unknown action '{action}'. Use 'grant' or 'revoke'.")