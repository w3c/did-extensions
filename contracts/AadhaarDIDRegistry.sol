// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AadhaarDIDRegistry
 * @dev Smart contract for managing DIDs on Ethereum blockchain
 * @author Aadhaar KYC System
 */
contract AadhaarDIDRegistry {
    struct DIDEntry {
        address controller;
        string docHash; // IPFS CID of DID Document
        uint256 created;
        uint256 updated;
        bool active;
        string citizenId; // Link to citizen data
    }
    
    mapping(string => DIDEntry) public didEntries;
    mapping(address => string[]) public controllerDIDs;
    mapping(string => bool) public aadhaarKYCStatus; // Track KYC status
    
    address public owner;
    uint256 public totalDIDs;
    
    event DIDRegistered(string indexed did, address indexed controller, string docHash, string citizenId, uint256 timestamp);
    event DIDUpdated(string indexed did, address indexed controller, string docHash, uint256 timestamp);
    event DIDDeactivated(string indexed did, address indexed controller, uint256 timestamp);
    event KYCStatusUpdated(string indexed citizenId, bool approved, uint256 timestamp);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Register a new DID
     * @param did The DID identifier
     * @param controller The controller address
     * @param docHash IPFS hash of DID document
     * @param citizenId Citizen identifier
     */
    function registerDID(
        string memory did, 
        address controller, 
        string memory docHash,
        string memory citizenId
    ) public {
        require(didEntries[did].controller == address(0), "DID already exists");
        require(controller != address(0), "Invalid controller address");
        require(bytes(citizenId).length > 0, "Citizen ID required");
        
        didEntries[did] = DIDEntry({
            controller: controller,
            docHash: docHash,
            created: block.timestamp,
            updated: block.timestamp,
            active: true,
            citizenId: citizenId
        });
        
        controllerDIDs[controller].push(did);
        totalDIDs++;
        
        emit DIDRegistered(did, controller, docHash, citizenId, block.timestamp);
    }
    
    /**
     * @dev Update DID document hash
     * @param did The DID identifier
     * @param newDocHash New IPFS hash
     */
    function updateDID(string memory did, string memory newDocHash) public {
        require(didEntries[did].controller != address(0), "DID not found");
        require(msg.sender == didEntries[did].controller, "Only controller can update");
        require(didEntries[did].active, "DID is deactivated");
        
        didEntries[did].docHash = newDocHash;
        didEntries[did].updated = block.timestamp;
        
        emit DIDUpdated(did, msg.sender, newDocHash, block.timestamp);
    }
    
    /**
     * @dev Deactivate a DID
     * @param did The DID identifier
     */
    function deactivateDID(string memory did) public {
        require(didEntries[did].controller != address(0), "DID not found");
        require(msg.sender == didEntries[did].controller, "Only controller can deactivate");
        
        didEntries[did].active = false;
        didEntries[did].updated = block.timestamp;
        
        emit DIDDeactivated(did, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Update KYC status (only owner/government)
     * @param citizenId Citizen identifier
     * @param approved KYC approval status
     */
    function updateKYCStatus(string memory citizenId, bool approved) public onlyOwner {
        aadhaarKYCStatus[citizenId] = approved;
        emit KYCStatusUpdated(citizenId, approved, block.timestamp);
    }
    
    /**
     * @dev Get DID information
     * @param did The DID identifier
     */
    function getDID(string memory did) public view returns (
        address controller,
        string memory docHash,
        uint256 created,
        uint256 updated,
        bool active,
        string memory citizenId
    ) {
        DIDEntry storage entry = didEntries[did];
        return (entry.controller, entry.docHash, entry.created, entry.updated, entry.active, entry.citizenId);
    }
    
    /**
     * @dev Get all DIDs for a controller
     * @param controller Controller address
     */
    function getControllerDIDs(address controller) public view returns (string[] memory) {
        return controllerDIDs[controller];
    }
    
    /**
     * @dev Check if DID is active
     * @param did The DID identifier
     */
    function isDIDActive(string memory did) public view returns (bool) {
        return didEntries[did].active;
    }
    
    /**
     * @dev Check KYC status
     * @param citizenId Citizen identifier
     */
    function isKYCApproved(string memory citizenId) public view returns (bool) {
        return aadhaarKYCStatus[citizenId];
    }
    
    /**
     * @dev Get total number of registered DIDs
     */
    function getTotalDIDs() public view returns (uint256) {
        return totalDIDs;
    }
    
    /**
     * @dev Transfer ownership
     * @param newOwner New owner address
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Invalid new owner");
        owner = newOwner;
    }
}
