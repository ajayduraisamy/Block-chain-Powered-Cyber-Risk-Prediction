// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MyContract {
    struct User {
        address wallet;
        string name;
    }

    struct Policy {
        uint256 riskScore;
        string riskLevel;
    }

    mapping(address => User) public users;
    mapping(address => Policy[]) public userPolicies;

    function registerUser(address _wallet, string memory _name) public {
        users[_wallet] = User(_wallet, _name);
    }

    function getUser(address _wallet) public view returns (string memory) {
        return users[_wallet].name;
    }

    // NEW: Store a policy
    function storePolicy(uint256 _riskScore, string memory _riskLevel) public {
        userPolicies[msg.sender].push(Policy(_riskScore, _riskLevel));
    }

    function getPolicies(address _user) public view returns (Policy[] memory) {
        return userPolicies[_user];
    }
}
