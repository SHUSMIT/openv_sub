#!/usr/bin/env python3
"""Test /reset endpoint with empty JSON body (as validation script does)"""

import requests
import json
import sys

def test_reset_with_empty_body():
    """Test POST /reset with empty JSON body"""
    
    # Simulate the validation script's curl command:
    # curl -X POST -H "Content-Type: application/json" -d '{}' \
    #   "http://localhost:7860/reset"
    
    test_urls = [
        "http://localhost:7860",
        "http://127.0.0.1:7860",
        "http://localhost:8000",
    ]
    
    for base_url in test_urls:
        try:
            url = f"{base_url}/reset"
            print(f"\n📌 Testing: POST {url}")
            print(f"   Body: {{}}")
            print(f"   Headers: Content-Type: application/json")
            
            response = requests.post(
                url,
                json={},  # Empty JSON body
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Response keys: {list(data.keys())}")
                print(f"   - status: {data.get('status')}")
                if 'observation' in data:
                    obs = data['observation']
                    print(f"   - observation keys: {list(obs.keys())}")
                    print(f"   - email: {obs.get('email', {}).get('subject', 'N/A')[:50]}...")
                    print(f"   - task_id: {obs.get('task_id')}")
                return True
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  Could not connect (server not running on {base_url})")
            continue
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print("\n⚠️  No running server found on common ports")
    print("   To test, start the server: python server.py")
    print("   Or use docker: docker run -p 7860:7860 <image>")
    return False

if __name__ == "__main__":
    success = test_reset_with_empty_body()
    sys.exit(0 if success else 1)
