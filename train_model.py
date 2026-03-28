import ipfshttpclient
import hashlib
from web3 import Web3
from config import GANACHE_URL, CONTRACT_ABI, CONTRACT_ADDRESS
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import os

# --- SCRIPT SETUP ---
# This script acts as the "AI AGENT" (Account 1)
# It must ask the smart contract for permission before
# it can get the data and train the model.
# --------------------

# --- AI AGENT IDENTITY ---
# We use Account 1 from Ganache as our AI agent
# Account 0 is the "Data Owner"
AGENT_ACCOUNT_INDEX = 1

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
if not w3.is_connected():
    print("🔴 FAILED to connect to Ganache.")
    sys.exit()

# Set the default account for this script
try:
    agent_account = w3.eth.accounts[AGENT_ACCOUNT_INDEX]
    w3.eth.default_account = agent_account
except IndexError:
    print(f"🔴 ERROR: Account {AGENT_ACCOUNT_INDEX} not found in Ganache.")
    print("Please ensure Ganache is running and has at least 2 accounts.")
    sys.exit()

print(f"🔗 Connected to Ganache as AI Agent: {agent_account}")

# Connect to the smart contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Connect to IPFS
try:
    client = ipfshttpclient.connect()
    print("Successfully connected to IPFS node.")
except Exception as e:
    print(f"🔴 FAILED to connect to IPFS: {e}")
    sys.exit()


def verify_and_fetch_dataset(dataset_id, save_as):
    """
    The AI Agent's main security function.
    1. Asks the contract for permission and hashes.
    2. If successful, downloads from IPFS.
    3. Verifies the downloaded file's hash.
    4. Saves the file and returns the path.
    """
    print(f"\n> Agent {agent_account} attempting to access '{dataset_id}'...")
    
    # 1. Ask contract for permission and data
    try:
        print("  - Asking contract for authorization and data hashes...")
        # This function call will FAIL if agent is not on the accessList
        ipfs_cid, on_chain_hash_bytes = contract.functions.getDatasetHashes(dataset_id).call()
        on_chain_hash = on_chain_hash_bytes.hex()
        print("  - AUTHORIZATION GRANTED.")
        print(f"  - Official IPFS CID: {ipfs_cid}")
        print(f"  - Official Hash: {on_chain_hash}")
        
    except Exception as e:
        print("  - 🔴 AUTHORIZATION DENIED.")
        print(f"  - Error: {e}")
        return None

    # 2. Download file from IPFS
    try:
        print(f"  - Downloading file from IPFS (CID: {ipfs_cid})...")
        data = client.cat(ipfs_cid)
        print("  - Download complete.")
    except Exception as e:
        print(f"  - 🔴 FAILED IPFS Download: {e}")
        return None
        
    # 3. Verify file integrity
    print("  - Verifying file integrity...")
    downloaded_hash = hashlib.sha256(data).hexdigest()
    print(f"  - Downloaded File Hash: {downloaded_hash}")
    
    if downloaded_hash == on_chain_hash:
        print("  - RESULT: VERIFIED ✅ File integrity confirmed.")
    else:
        print("  - 🔴 RESULT: TAMPERING DETECTED 🛑 Hashes do not match.")
        return None
        
    # 4. Save the verified file
    try:
        with open(save_as, 'wb') as f:
            f.write(data)
        print(f"  - Verified data saved to '{save_as}'")
        return save_as
    except Exception as e:
        print(f"  - 🔴 FAILED to save file: {e}")
        return None


# --- Main ML Pipeline ---
if __name__ == "__main__":
    UNIQUE_ID = 'diabetes_v3' # The ID of the dataset we want to train on
    
    print("\n--- ML PIPELINE INITIATED (Secure Edition) ---")
    print(f"\nSTEP 1: SECURE DATA SOURCING & VERIFICATION")
    
    verified_file_path = verify_and_fetch_dataset(
        UNIQUE_ID, 
        save_as="verified_training_data.csv"
    )

    if verified_file_path:
        print("\nSTEP 2: MODEL TRAINING")
        print(f"  - Training on data from '{verified_file_path}'...")
        try:
            features_list = ['Glucose', 'BloodPressure', 'BMI', 'Age']
            target_col = 'Outcome'
            cols_to_use = features_list + [target_col]
            
            df = pd.read_csv(verified_file_path, usecols=cols_to_use, encoding='latin-1', engine='python')
            
            X = df[features_list]
            y = df[target_col]
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            model = LogisticRegression(max_iter=200)
            model.fit(X_train, y_train)
            
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            
            print(f"  - Model training complete. Achieved accuracy: {accuracy:.2f}")

        except Exception as e:
            print(f"\nERROR DURING MODEL TRAINING")
            print(f"  - The file was verified, but the ML code failed.")
            print(f"  - Error: {e}")
    else:
        print("\n-------------------------------------------")
        print("SECURITY ALERT: PIPELINE HALTED")
        print("  - Data verification failed or agent is not authorized.")
        print("-------------------------------------------")

    print("\n--- ML PIPELINE FINISHED ---")