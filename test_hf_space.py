#!/usr/bin/env python3
"""Test HuggingFace Space endpoints"""

import requests
import json
import sys

# HF Space URL
BASE_URL = "https://shusmitSarkar-openenv-email-triage.hf.space"

print("=" * 70)
print("HF SPACE ENDPOINT TESTS")
print("=" * 70)

tests_passed = 0
tests_failed = 0

# Test 1: Health check
print("\n[TEST 1] Health Check")
print("-" * 70)
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"✅ Status: {resp.status_code}")
    data = resp.json()
    print(f"   Status: {data.get('status')}")
    print(f"   Service: {data.get('service')}")
    tests_passed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 2: Reset endpoint (easy task)
print("\n[TEST 2] Reset Endpoint - Easy Task")
print("-" * 70)
try:
    resp = requests.post(
        f"{BASE_URL}/reset",
        json={"task_id": "email_priority_classification"},
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        obs = data.get('observation', {})
        print(f"✅ Status: {resp.status_code}")
        print(f"   Email ID: {obs.get('current_email', {}).get('email_id', 'N/A')}")
        print(f"   Subject: {obs.get('current_email', {}).get('subject', 'N/A')[:50]}...")
        tests_passed += 1
    else:
        print(f"❌ Status: {resp.status_code}")
        print(f"   Response: {resp.text}")
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 3: Reset for medium task
print("\n[TEST 3] Reset Endpoint - Medium Task")
print("-" * 70)
try:
    resp = requests.post(
        f"{BASE_URL}/reset",
        json={"task_id": "urgency_detection"},
        timeout=10
    )
    if resp.status_code == 200:
        print(f"✅ Status: {resp.status_code}")
        tests_passed += 1
    else:
        print(f"❌ Status: {resp.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 4: Reset for hard task
print("\n[TEST 4] Reset Endpoint - Hard Task")
print("-" * 70)
try:
    resp = requests.post(
        f"{BASE_URL}/reset",
        json={"task_id": "intelligent_routing"},
        timeout=10
    )
    if resp.status_code == 200:
        print(f"✅ Status: {resp.status_code}")
        tests_passed += 1
    else:
        print(f"❌ Status: {resp.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 5: Get tasks list
print("\n[TEST 5] List Tasks")
print("-" * 70)
try:
    resp = requests.get(f"{BASE_URL}/tasks", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        tasks = data.get('tasks', [])
        print(f"✅ Status: {resp.status_code}")
        print(f"   Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"     - {task['id']} ({task['difficulty']}): {task['name'][:40]}")
        tests_passed += 1
    else:
        print(f"❌ Status: {resp.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 6: Step endpoint
print("\n[TEST 6] Step Endpoint")
print("-" * 70)
try:
    # Reset first
    reset_resp = requests.post(
        f"{BASE_URL}/reset",
        json={"task_id": "email_priority_classification"},
        timeout=10
    )
    
    # Create action
    action = {
        "action_type": "classify",
        "priority": "high",
        "reasoning": "Test action"
    }
    
    step_resp = requests.post(
        f"{BASE_URL}/step",
        json={"task_id": "email_priority_classification", "action": action},
        timeout=10
    )
    
    if step_resp.status_code == 200:
        step_data = step_resp.json()
        reward = step_data.get('reward', {})
        print(f"✅ Status: {step_resp.status_code}")
        print(f"   Reward value: {reward.get('value', 'N/A')}")
        print(f"   Done: {step_data.get('info', {}).get('done', 'N/A')}")
        tests_passed += 1
    else:
        print(f"❌ Status: {step_resp.status_code}")
        print(f"   Response: {step_resp.text}")
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 7: State endpoint
print("\n[TEST 7] State Endpoint")
print("-" * 70)
try:
    resp = requests.get(
        f"{BASE_URL}/state",
        params={"task_id": "email_priority_classification"},
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        state = data.get('state', {})
        print(f"✅ Status: {resp.status_code}")
        print(f"   Episode step: {state.get('episode_step', 'N/A')}")
        print(f"   Cumulative reward: {state.get('cumulative_reward', 'N/A')}")
        tests_passed += 1
    else:
        print(f"❌ Status: {resp.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 8: Full episode (5 steps)
print("\n[TEST 8] Full Episode - 5 Steps")
print("-" * 70)
try:
    # Reset
    requests.post(
        f"{BASE_URL}/reset",
        json={"task_id": "email_priority_classification"},
        timeout=10
    )
    
    # Run 5 steps
    step_count = 0
    total_reward = 0
    for i in range(5):
        action = {
            "action_type": "classify",
            "priority": ["low", "medium", "high", "critical"][i % 4],
            "reasoning": f"Step {i+1}"
        }
        
        step_resp = requests.post(
            f"{BASE_URL}/step",
            json={"task_id": "email_priority_classification", "action": action},
            timeout=10
        )
        
        if step_resp.status_code == 200:
            step_data = step_resp.json()
            reward = step_data.get('reward', {}).get('value', 0)
            total_reward += reward
            step_count += 1
        else:
            break
    
    print(f"✅ Completed {step_count} steps")
    print(f"   Total reward: {total_reward:.2f}")
    if step_count >= 3:
        tests_passed += 1
    else:
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Test 9: All three tasks work
print("\n[TEST 9] All Three Tasks Full Reset")
print("-" * 70)
try:
    all_ok = True
    for task_id in ["email_priority_classification", "urgency_detection", "intelligent_routing"]:
        resp = requests.post(
            f"{BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=10
        )
        if resp.status_code != 200:
            all_ok = False
            print(f"   ❌ {task_id}: Status {resp.status_code}")
        else:
            print(f"   ✅ {task_id}: OK")
    
    if all_ok:
        tests_passed += 1
    else:
        tests_failed += 1
except Exception as e:
    print(f"❌ FAILED: {e}")
    tests_failed += 1

# Summary
print("\n" + "=" * 70)
print(f"RESULTS: {tests_passed} PASSED, {tests_failed} FAILED")
print("=" * 70)

sys.exit(0 if tests_failed == 0 else 1)
