pragma solidity ^0.5.0;

import 'OpenZeppelin/openzeppelin-contracts@2.3.0/contracts/math/SafeMath.sol';
import "../../interfaces/IPriceOracleGetter.sol";

interface ISortedOracles {
    function medianRate(address) external view returns (uint256, uint256);
    function medianTimestamp(address) external view returns (uint256);
}

interface IRegistry {
    function getAddressForOrDie(bytes32) external view returns (address);
}

contract UsingRegistry {
    bytes32 constant GOLD_TOKEN_REGISTRY_ID = keccak256(abi.encodePacked("GoldToken"));
    bytes32 constant SORTED_ORACLES_REGISTRY_ID = keccak256(abi.encodePacked("SortedOracles"));

    IRegistry constant public registry = IRegistry(0x000000000000000000000000000000000000ce10);

    function getGoldToken() internal view returns (address) {
        return registry.getAddressForOrDie(GOLD_TOKEN_REGISTRY_ID);
    }

    function getSortedOracles() internal view returns (ISortedOracles) {
        return ISortedOracles(registry.getAddressForOrDie(SORTED_ORACLES_REGISTRY_ID));
    }
}

/// @title CeloProxyPriceProvider
/// @author Moola
/// @notice Proxy smart contract to get the price of an asset from a price source, with Celo SortedOracles
///         smart contracts as the only option
contract CeloProxyPriceProvider is IPriceOracleGetter, UsingRegistry {
    using SafeMath for uint256;

    /// @notice Gets an asset price by address
    /// @param _asset The asset address
    function getAssetPrice(address _asset) public view returns(uint256) {
        if (_asset == getGoldToken()) {
            return 1 ether;
        }
        uint256 _price;
        uint256 _divisor;
        ISortedOracles _oracles = getSortedOracles();
        (_price, _divisor) = _oracles.medianRate(_asset);
        require(_price > 0, "Reported price is 0");
        uint _reportTime = _oracles.medianTimestamp(_asset);
        require(block.timestamp.sub(_reportTime) < 10 minutes, "Reported price is older than 10 minutes");
        return _divisor.mul(1 ether).div(_price);
    }

    /// @dev Return the value of the given input as CELO per unit, multiplied by 2**112.
    /// @param token The ERC-20 token to check the value.
    function getCELOPx(address token) external view returns (uint) {
        uint unscaledPrice = getAssetPrice(token);
        uint px = (unscaledPrice * 2**112) / 10**18;
        require(px != 0, 'no px');
        return px;
    }
}
