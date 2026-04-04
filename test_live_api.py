"""Test the live HuggingFace deployment"""
import requests
import json
from time import sleep
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

BASE_URL = "https://shusmitSarkar-openenv-email-triage.hf.space"

print("=" * 70)
print("TESTING LIVE API ENDPOINTS")
print("=" * 70)

# Test 1: Health Check
print("\n[1] Testing /health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=10, verify=False)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)[:200]}")

# Test 2: Reset
print("\n[2] Testing /reset endpoint...")
try:
    payload = {"task_id": "email_priority_classification", "seed": 42}
    response = requests.post(f"{BASE_URL}/reset", json=payload, timeout=10, verify=False)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Reset successful")
        email = data.get('observation', {}).get('email', {})
        print(f"  - Email ID: {email.get('email_id', 'N/A')}")
        print(f"  - Subject: {email.get('subject', 'N/A')[:60]}")
        print(f"  - Sender: {email.get('sender', 'N/A')[:40]}")
        print(f"  - Customer Value: {email.get('customer_lifetime_value', 'N/A')}")
    else:
        print(f"✗ Error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)[:200]}")

# Test 3: Get State
print("\n[3] Testing /state endpoint...")
try:
    response = requests.get(f"{BASE_URL}/state", timeout=10, verify=False)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        state = data.get('state', {})
        print(f"✓ State retrieved")
        print(f"  - Task: {state.get('task_id', 'N/A')}")
        print(f"  - Step: {state.get('episode_step', 'N/A')}")
        print(f"  - Cumulative Reward: {state.get('cumulative_reward', 'N/A')}")
        print(f"  - Emails Processed: {state.get('emails_processed', 'N/A')}")
    else:
        print(f"✗ Error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)[:200]}")

# Test 4: Step with action
print("\n[4] Testing /step endpoint with action...")
try:
    action = {
        "task_id": "email_priority_classification",
        "classify_priority": {
            "priority": "high",
            "confidence": 0.85
        }
    }
    response = requests.post(f"{BASE_URL}/step", json=action, timeout=10, verify=False)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        reward = data.get('reward', {})
        print(f"✓ Step successful")
        print(f"  - Episode Reward: {reward.get('episode_reward', 'N/A')}")
        print(f"  - Cumulative Reward: {reward.get('cumulative_reward', 'N/A')}")
        print(f"  - Done: {reward.get('is_done', 'N/A')}")
        print(f"  - Breakdown: {json.dumps(reward.get('breakdown', {}), indent=4)}")
    else:
        print(f"✗ Error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {str(e)[:200]}")

print("\n" + "=" * 70)
print("API testing complete!")
print("=" * 70)
