# Blockchain-Based Data Provenance System

## Overview
This project implements a blockchain-based framework to ensure the integrity and authenticity of machine learning datasets. It prevents data tampering by verifying dataset fingerprints before model training, addressing the "Garbage In, Garbage Out" problem in ML pipelines.

## Key Features
- Secure dataset verification using SHA-256 hashing  
- Storage of dataset fingerprints on blockchain (Ethereum - Ganache)  
- Tamper detection by comparing local dataset with on-chain hash  
- Integration of machine learning pipeline with data verification layer  
- Performance analysis including latency measurement  

## System Architecture
1. Dataset is processed and hashed using SHA-256  
2. Hash is stored on blockchain via a smart contract  
3. Before training, dataset is verified against stored hash  
4. If mismatch is detected, training is blocked  
5. Verified data is used for ML model training  

## Tech Stack
- Python (Data processing and ML pipeline)  
- Solidity (Smart contract)  
- Web3.py (Blockchain interaction)  
- Ganache (Local Ethereum blockchain)  
- Scikit-learn (Machine learning)  

## Project Structure
contracts/           Smart contract for data provenance  
migrations/          Deployment scripts  
admin.py             Admin operations  
agent.py             Blockchain interaction logic  
auditor.py           Data verification module  
train_model.py       ML model training  
measure_latency.py   Performance evaluation  
config.py            Configuration settings  
truffle-config.js    Blockchain configuration  

## How to Run

1. Start Ganache (local blockchain)

2. Deploy smart contract:
truffle migrate

3. Install dependencies:
pip install -r requirements.txt

4. Run the project:
python train_model.py

## Results
- Achieved reliable dataset integrity verification  
- Successfully detected tampered data  
- Demonstrated integration of blockchain with ML pipeline  

## Future Improvements
- Deploy on public blockchain network  
- Optimize gas usage  
- Extend system for large-scale datasets  
- Integrate real-time data pipelines  

## Key Learning
This project demonstrates how blockchain can be used to ensure trust in data-driven systems by securing data provenance in machine learning workflows.
