// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DataProvenance {
    
    struct DatasetRecord {
        string ipfsCid;
        bytes32 sha256Hash;
        address owner;
        bool exists;
    }

    mapping(string => DatasetRecord) public records;
    mapping(string => mapping(address => bool)) public accessList;

    event DataAccessed(
        string indexed datasetId,
        address indexed agentAddress,
        uint timestamp
    );

    modifier onlyDataOwner(string memory _id) {
        require(records[_id].owner == msg.sender, "Caller is not the data owner");
        _;
    }

    modifier isAuthorized(string memory _id) {
        require(accessList[_id][msg.sender], "Agent is not authorized for this dataset");
        _;
    }

    function registerDataset(string memory _id, string memory _ipfsCid, bytes32 _sha256Hash) public {
        require(!records[_id].exists, "Dataset ID already exists");

        records[_id] = DatasetRecord({
            ipfsCid: _ipfsCid,
            sha256Hash: _sha256Hash,
            owner: msg.sender,
            exists: true
        });
        
        accessList[_id][msg.sender] = true;
    }

    function grantAccess(string memory _id, address _agentAddress) public onlyDataOwner(_id) {
        accessList[_id][_agentAddress] = true;
    }

    function revokeAccess(string memory _id, address _agentAddress) public onlyDataOwner(_id) {
        accessList[_id][_agentAddress] = false;
    }
    
    // --- FUNCTION 1: THE "SECURITY CAMERA" (Write-Only) ---
    // We call this with .transact()
    function logAccess(string memory _id) public isAuthorized(_id) {
        emit DataAccessed(_id, msg.sender, block.timestamp);
    }
    
    // --- FUNCTION 2: THE "BOUNCER" (Read-Only) ---
    // We call this with .call()
    function getHashes_READONLY(string memory _id) 
        public 
        view // <-- This "view" keyword is the bug fix
        isAuthorized(_id) 
        returns (string memory, bytes32) 
    {
        require(records[_id].exists, "Dataset does not exist");
        return (records[_id].ipfsCid, records[_id].sha256Hash);
    }
}