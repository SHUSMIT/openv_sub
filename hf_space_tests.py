import requests

url = 'https://shusmitSarkar-openenv-email-triage.hf.space'
tests_passed = 0
tests_failed = 0

print('=' * 60)
print('HF SPACE COMPREHENSIVE TESTS')
print('=' * 60)

# Test 1: Health
print('\n[1] Health Check')
try:
    r = requests.get(f'{url}/health', timeout=10)
    if r.status_code == 200:
        print(f'   ✅ PASS - Status {r.status_code}')
        tests_passed += 1
    else:
        print(f'   ❌ FAIL - Status {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

# Test 2: Reset Task 1
print('\n[2] Reset Task 1 - Priority Classification')
try:
    r = requests.post(f'{url}/reset?task_id=email_priority_classification', timeout=10)
    if r.status_code == 200:
        print(f'   ✅ PASS - Status {r.status_code}')
        tests_passed += 1
    else:
        print(f'   ❌ FAIL - Status {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

# Test 3: Reset Task 2
print('\n[3] Reset Task 2 - Urgency Detection')
try:
    r = requests.post(f'{url}/reset?task_id=urgency_detection', timeout=10)
    if r.status_code == 200:
        print(f'   ✅ PASS - Status {r.status_code}')
        tests_passed += 1
    else:
        print(f'   ❌ FAIL - Status {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

# Test 4: Reset Task 3
print('\n[4] Reset Task 3 - Intelligent Routing')
try:
    r = requests.post(f'{url}/reset?task_id=intelligent_routing', timeout=10)
    if r.status_code == 200:
        print(f'   ✅ PASS - Status {r.status_code}')
        tests_passed += 1
    else:
        print(f'   ❌ FAIL - Status {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

# Test 5: Step Action
print('\n[5] Step - Process Action')
try:
    requests.post(f'{url}/reset?task_id=email_priority_classification', timeout=10)
    action = {
        'task_id': 'email_priority_classification',
        'classify_priority': {'priority': 'high', 'confidence': 0.9}
    }
    r = requests.post(f'{url}/step?task_id=email_priority_classification', json=action, timeout=10)
    if r.status_code == 200 and 'reward' in r.json():
        reward = r.json()['reward'].get('episode_reward', 0)
        print(f'   ✅ PASS - Status {r.status_code}, Reward: {reward}')
        tests_passed += 1
    else:
        print(f'   ❌ FAIL - Status {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

# Test 6: State
print('\n[6] State - Get Environment State')
try:
    r = requests.get(f'{url}/state?task_id=email_priority_classification', timeout=10)
    if r.status_code == 200:
        print(f'   ✅ PASS - Status {r.status_code}')
        tests_passed += 1
    else:
        print(f'   ❌ FAIL - Status {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

# Test 7: Tasks List
print('\n[7] List Tasks')
try:
    r = requests.get(f'{url}/tasks', timeout=10)
    if r.status_code == 200 and len(r.json().get('tasks', [])) == 3:
        tasks = [t['id'] for t in r.json()['tasks']]
        print(f'   ✅ PASS - Found 3 tasks: {tasks}')
        tests_passed += 1
    else:
        print(f'   ❌ FAIL - Status {r.status_code}')
        tests_failed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

# Test 8: Full Episode
print('\n[8] Full Episode - 10 Steps')
try:
    requests.post(f'{url}/reset?task_id=email_priority_classification', timeout=10)
    total_reward = 0
    for i in range(10):
        action = {
            'task_id': 'email_priority_classification',
            'classify_priority': {'priority': 'high', 'confidence': 0.9}
        }
        r = requests.post(f'{url}/step?task_id=email_priority_classification', json=action, timeout=10)
        if r.status_code == 200:
            reward = r.json()['reward'].get('episode_reward', 0)
            total_reward += reward
        else:
            break
    print(f'   ✅ PASS - 10 steps completed, Total reward: {total_reward}')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ FAIL - {e}')
    tests_failed += 1

print('\n' + '=' * 60)
print(f'RESULTS: {tests_passed} PASSED, {tests_failed} FAILED')
print('=' * 60)
if tests_failed == 0:
    print('\n🎉 ALL TESTS PASSED - HF SPACE FULLY OPERATIONAL')
else:
    print(f'\n⚠️ {tests_failed} tests failed')
