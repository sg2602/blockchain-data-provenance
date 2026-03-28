from web3 import Web3
from config import GANACHE_URL, CONTRACT_ABI, CONTRACT_ADDRESS
import sys
from datetime import datetime

# --- SCRIPT SETUP ---
# This script reads the 'DataAccessed' event log from the 
# blockchain to create a tamper-proof audit trail.
#
# Usage: 
# python audit.py <dataset_id>
# --------------------

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    print("🔴 FAILED to connect to Ganache.")
    sys.exit()

# Connect to the smart contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def get_audit_trail(dataset_id):
    print(f"--- 🔍 Audit Trail for '{dataset_id}' ---")
    try:
        # Create a filter for the 'DataAccessed' event
        # We filter by 'datasetId' to only get logs for this file
        event_filter = contract.events.DataAccessed.create_filter(
            fromBlock='earliest',
            argument_filters={'datasetId': dataset_id}
        )

        logs = event_filter.get_all_entries()

        if not logs:
            print("  - No access records found.")
            return

        print(f"  - Found {len(logs)} access record(s):")
        print("-----------------------------------------------------------------")
        print("  Timestamp (UTC)     | Agent Address")
        print("-----------------------------------------------------------------")

        for log in logs:
            # 'args' contains the event data
            agent = log.args.agentAddress
            # 'timestamp' is in the block, not the log args
            ts = w3.eth.get_block(log.blockNumber).timestamp

            # Convert Unix timestamp to human-readable string
            utc_time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {utc_time} | {agent}")

    except Exception as e:
        print(f"  - FAILED to retrieve logs: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audit.py <dataset_id>")
        sys.exit()

    dataset_id = sys.argv[1]
    get_audit_trail(dataset_id)