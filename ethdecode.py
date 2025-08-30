from web3 import Web3
from eth_abi import decode
import json

# Your input data
input_data = '0x1fad948c00000000000000000000000000000000000000000000000000000000000000400000000000000000000000006bbe1aa3f85fa0489b3eb07229868ae8bad4c11400000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000020000000000000000000000000b167c51a789d4d7f7eab44af026104d8858929b300000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000000100be0000000000000000000000000000000000000000000000000000000000012a3e000000000000000000000000000000000000000000000000000000000001750000000000000000000000000000000000000000000000000000000000002255b2000000000000000000000000000000000000000000000000000000000022551000000000000000000000000000000000000000000000000000000000000002a00000000000000000000000000000000000000000000000000000000000000360000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e4b61d27f6000000000000000000000000036cbd53842c5426634e7929541ec2318f3dcf7e000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000044a9059cbb00000000000000000000000016db2fcc2bd501a1518654cfa44ab2a93dd36ffc00000000000000000000000000000000000000000000000000000000000186a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000957cea357b5ac0639f89f9e378a1f03aa5005c0a250000000000000000000000000000000000000000000000000000000068bbdf440000000000000000000000000000000000000000000000000000000068b2a4c4efd2a83620746e2c62626e5a72e02554021e34193a0b1e04e38a425b8ea07d8032e233b3e3d3821d0212a1ecb0927621d575d9e17bb76d48fceb4e7c9eee47a11c0000000000000000000000000000000000000000000000000000000000000000000000000000000000004106bbf03eabab3b1c02e0564497c62d7d31e84d3078507a112325cdec1ebb24d4214216b0adbd5fc585395a6d9f3f28c5c3492e9c136dfd3b72f6f457e62135921c00000000000000000000000000000000000000000000000000000000000000'


def decode_ethereum_input(input_data):
    """Decode Ethereum transaction input data"""

    if isinstance(input_data, bytes):
        # Option 1: Convert bytes to string
        input_data = input_data.hex()
    
    # Remove 0x prefix
    if input_data.startswith('0x'):
        input_data = input_data[2:]
    
    # Extract function selector (first 4 bytes = 8 hex chars)
    function_selector = input_data[:8]
    print(f"Function Selector: 0x{function_selector}")
    
    # Common function selectors
    function_signatures = {
        '1fad948c': 'multicall(bytes[],address)',
        'b61d27f6': 'execute(address,uint256,bytes)',
        'a9059cbb': 'transfer(address,uint256)',
        # Add more as needed
    }
    
    if function_selector in function_signatures:
        print(f"Function: {function_signatures[function_selector]}")
    
    # Extract parameters (remaining data)
    params_data = input_data[8:]
    
    # Decode based on function selector
    if function_selector == '1fad948c':  # multicall
        return decode_multicall(params_data)
    elif function_selector == 'b61d27f6':  # execute
        return decode_execute(params_data)
    elif function_selector == 'a9059cbb':  # transfer
        return decode_transfer(params_data)
    else:
        print(f"Unknown function selector: {function_selector}")
        return None

def decode_multicall(params_data):
    """Decode multicall function parameters"""
    print("\n=== MULTICALL DECODE ===")
    
    # Convert hex to bytes for decoding
    data_bytes = bytes.fromhex(params_data)
    
    try:
        # Multicall typically has: (bytes[] calldata, address target)
        # First try to decode the structure
        
        # Read first 32 bytes (offset to calldata array)
        calldata_offset = int.from_bytes(data_bytes[0:32], 'big')
        print(f"Calldata offset: {calldata_offset}")
        
        # Read second 32 bytes (target address)
        target_address = '0x' + data_bytes[32:64].hex()[-40:]  # Last 20 bytes for address
        print(f"Target address: {target_address}")
        
        # Read array length at offset
        array_length = int.from_bytes(data_bytes[calldata_offset:calldata_offset+32], 'big')
        print(f"Number of calls: {array_length}")
        
        # Decode each call in the array
        calls = []
        current_offset = calldata_offset + 32  # Skip array length
        
        for i in range(array_length):
            # Read offset to this call's data
            call_offset = int.from_bytes(data_bytes[current_offset:current_offset+32], 'big')
            current_offset += 32
            
            # Read call data length
            actual_call_offset = calldata_offset + call_offset
            call_data_length = int.from_bytes(data_bytes[actual_call_offset:actual_call_offset+32], 'big')
            
            # Extract call data
            call_data = data_bytes[actual_call_offset+32:actual_call_offset+32+call_data_length]
            call_hex = '0x' + call_data.hex()
            
            print(f"\nCall {i+1}:")
            print(f"  Data length: {call_data_length}")
            print(f"  Call data: {call_hex}")
            
            # Try to decode this inner call
            inner_decode = decode_ethereum_input(call_hex)
            calls.append({
                'data': call_hex,
                'decoded': inner_decode
            })
        
        return {
            'function': 'multicall',
            'target_address': target_address,
            'calls': calls
        }
        
    except Exception as e:
        print(f"Error decoding multicall: {e}")
        return None

def decode_execute(params_data):
    """Decode execute function parameters"""
    print("\n=== EXECUTE DECODE ===")
    
    data_bytes = bytes.fromhex(params_data)
    
    try:
        # execute(address target, uint256 value, bytes data)
        target = '0x' + data_bytes[12:32].hex()  # Address is in bytes 12-32 of first word
        value = int.from_bytes(data_bytes[32:64], 'big')
        data_offset = int.from_bytes(data_bytes[64:96], 'big')
        
        # Get data length and content
        data_length = int.from_bytes(data_bytes[data_offset:data_offset+32], 'big')
        call_data = data_bytes[data_offset+32:data_offset+32+data_length]
        call_hex = '0x' + call_data.hex()
        
        print(f"Target: {target}")
        print(f"Value: {value} wei")
        print(f"Data: {call_hex}")
        
        # Try to decode the inner call data
        inner_decode = decode_ethereum_input(call_hex)
        
        return {
            'function': 'execute',
            'target': target,
            'value': value,
            'data': call_hex,
            'decoded_data': inner_decode
        }
        
    except Exception as e:
        print(f"Error decoding execute: {e}")
        return None

def decode_transfer(params_data):
    """Decode transfer function parameters"""
    print("\n=== TRANSFER DECODE ===")
    
    data_bytes = bytes.fromhex(params_data)
    
    try:
        # transfer(address to, uint256 amount)
        to_address = '0x' + data_bytes[12:32].hex()  # Address in bytes 12-32
        amount = int.from_bytes(data_bytes[32:64], 'big')
        
        print(f"To: {to_address}")
        print(f"Amount: {amount} (raw)")
        print(f"Amount: {amount / 10**18} ETH (if 18 decimals)")
        
        return {
            'function': 'transfer',
            'to': to_address,
            'amount': amount
        }
        
    except Exception as e:
        print(f"Error decoding transfer: {e}")
        return None

def format_address(hex_str):
    """Format hex string as Ethereum address"""
    if len(hex_str) >= 40:
        return '0x' + hex_str[-40:]
    return '0x' + hex_str.zfill(40)

def analyze_raw_data(input_data):
    """Additional analysis of the raw data"""
    print("\n=== RAW DATA ANALYSIS ===")
    
    # Remove 0x and function selector
    data = input_data[10:]  # Remove 0x and 4-byte selector
    
    # Look for addresses (20-byte patterns that might be addresses)
    print("Potential addresses found:")
    i = 0
    while i < len(data) - 40:
        # Look for patterns that start with zeros (common in address encoding)
        if data[i:i+24] == '0' * 24:  # 12 bytes of zeros
            potential_address = '0x' + data[i+24:i+64]
            if not all(c == '0' for c in data[i+24:i+64]):  # Not all zeros
                print(f"  {potential_address}")
        i += 64  # Move to next 32-byte word
    
    print(f"\nTotal data length: {len(data)} hex chars ({len(data)//2} bytes)")

# Main execution

def extract_data(input_data):
    print("Decoding Ethereum transaction input...")
    print(f"Input data: {input_data[:50]}...{input_data[-50:]}")
    
    result = decode_ethereum_input(input_data)
    
    if result:
        print(f"\n=== FINAL DECODED RESULT ===")
        print(json.dumps(result, indent=2, default=str))
    
    # Additional raw analysis
    analyze_raw_data(input_data)

'''
if __name__ == "__main__":
    print("Decoding Ethereum transaction input...")
    print(f"Input data: {input_data[:50]}...{input_data[-50:]}")
    
    result = decode_ethereum_input(input_data)
    
    if result:
        print(f"\n=== FINAL DECODED RESULT ===")
        print(json.dumps(result, indent=2, default=str))
    
    # Additional raw analysis
    analyze_raw_data()

'''