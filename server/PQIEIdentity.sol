// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PQIE Identity Contract
 * @dev Smart contract for Post-Quantum Identity Encryption on Ethereum
 */
contract PQIEIdentity {
    struct IdentityRecord {
        string did;
        string publicKey;
        string documentHash;
        uint256 timestamp;
        bool active;
        address owner;
    }
    
    mapping(string => IdentityRecord) public identities;
    mapping(address => string[]) public ownerToDids;
    
    event IdentityCreated(string indexed did, address indexed owner);
    event IdentityUpdated(string indexed did);
    event IdentityRevoked(string indexed did);
    
    function createIdentity(
        string memory did,
        string memory publicKey,
        string memory documentHash
    ) public {
        require(identities[did].timestamp == 0, "Identity already exists");
        
        identities[did] = IdentityRecord({
            did: did,
            publicKey: publicKey,
            documentHash: documentHash,
            timestamp: block.timestamp,
            active: true,
            owner: msg.sender
        });
        
        ownerToDids[msg.sender].push(did);
        emit IdentityCreated(did, msg.sender);
    }
    
    function updateIdentity(
        string memory did,
        string memory newDocumentHash
    ) public {
        require(identities[did].owner == msg.sender, "Not owner");
        require(identities[did].active, "Identity not active");
        
        identities[did].documentHash = newDocumentHash;
        identities[did].timestamp = block.timestamp;
        
        emit IdentityUpdated(did);
    }
    
    function revokeIdentity(string memory did) public {
        require(identities[did].owner == msg.sender, "Not owner");
        
        identities[did].active = false;
        identities[did].timestamp = block.timestamp;
        
        emit IdentityRevoked(did);
    }
    
    function getIdentity(string memory did) public view returns (
        string memory,
        string memory,
        string memory,
        uint256,
        bool,
        address
    ) {
        IdentityRecord memory record = identities[did];
        return (
            record.did,
            record.publicKey,
            record.documentHash,
            record.timestamp,
            record.active,
            record.owner
        );
    }
    
    function getOwnerDids(address owner) public view returns (string[] memory) {
        return ownerToDids[owner];
    }
}
