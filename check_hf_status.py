import requests
import time

BASE_URL = "https://shusmitSarkar-openenv-email-triage.hf.space"

print("Checking HF Space status...")
print("=" * 60)

for attempt in range(5):
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Attempt {attempt+1}: Status {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"✅ Space is ONLINE!")
            try:
                data = resp.json()
                print(f"   Service: {data.get('service')}")
                print(f"   Status: {data.get('status')}")
            except:
                pass
            break
        else:
            text = resp.text[:150] if resp.text else "(empty)"
            print(f"   Error: {text}")
    except Exception as e:
        print(f"Attempt {attempt+1}: Connection error - {str(e)[:100]}")
    
    if attempt < 4:
        print(f"   Waiting 15 seconds... (Space may be rebuilding)")
        time.sleep(15)

print("=" * 60)
