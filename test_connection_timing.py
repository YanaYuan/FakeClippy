#!/usr/bin/env python3
"""
Test connection behavior for the Flask API to verify it properly closes connections
"""

import time
import requests
import json

def test_connection_timing(url):
    """Test how long it takes for the connection to close after receiving data"""
    
    print(f"Testing connection timing for: {url}")
    print("=" * 60)
    
    # Test data - simple message
    test_message = {
        "messages": [
            {"role": "user", "content": "Hello! Please respond with a simple greeting."}
        ]
    }
    
    start_time = time.time()
    print(f"[{time.time() - start_time:.2f}s] Starting request...")
    
    try:
        response = requests.post(
            f"{url}/api/chat",
            json=test_message,
            stream=True,
            timeout=10
        )
        
        print(f"[{time.time() - start_time:.2f}s] Response received, status: {response.status_code}")
        
        # Read all data
        all_data = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                print(f"[{time.time() - start_time:.2f}s] Received: {line_str[:100]}...")
                all_data += line_str + "\n"
                
                # Check for completion
                if 'done": true' in line_str:
                    print(f"[{time.time() - start_time:.2f}s] Stream marked as done")
                    break
        
        # Connection should close here
        connection_close_time = time.time()
        print(f"[{connection_close_time - start_time:.2f}s] Stream reading completed")
        
        # Test if we can detect when the connection actually closes
        try:
            # Try to read more data (should fail if connection is closed)
            extra = response.content
            print(f"[{time.time() - start_time:.2f}s] WARNING: Connection still open, got extra data")
        except:
            print(f"[{time.time() - start_time:.2f}s] Connection properly closed")
            
        total_time = time.time() - start_time
        print(f"\nTotal time: {total_time:.2f}s")
        print("=" * 60)
        
        return total_time
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Connection Timing Test")
    print("This script tests how quickly connections close after data is received")
    print()
    
    # Test local Flask server (if running)
    print("Testing local Flask server:")
    local_time = test_connection_timing("http://localhost:5001")
    
    print("\n" + "="*80 + "\n")
    
    # Test deployed version (replace with your Vercel URL)
    vercel_url = input("Enter your Vercel deployment URL (or press Enter to skip): ").strip()
    if vercel_url:
        if not vercel_url.startswith('http'):
            vercel_url = 'https://' + vercel_url
        print(f"Testing Vercel deployment:")
        vercel_time = test_connection_timing(vercel_url)
        
        if local_time and vercel_time:
            print(f"\nComparison:")
            print(f"Local Flask:  {local_time:.2f}s")
            print(f"Vercel Flask: {vercel_time:.2f}s")
            print(f"Difference:   {abs(vercel_time - local_time):.2f}s")
    
    print("\nTest completed!")
