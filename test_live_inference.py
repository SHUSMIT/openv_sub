"""Run a full inference episode on the live deployment"""
import requests
import json
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

BASE_URL = "https://shusmitSarkar-openenv-email-triage.hf.space"

print("=" * 70)
print("RUNNING FULL INFERENCE EPISODE - LIVE DEPLOYMENT")
print("=" * 70)

# Reset environment
print("\n[INIT] Resetting environment...")
payload = {"task_id": "email_priority_classification", "seed": 123}
response = requests.post(f"{BASE_URL}/reset", json=payload, timeout=10, verify=False)
if response.status_code != 200:
    print(f"✗ Reset failed: {response.text[:200]}")
    exit(1)

data = response.json()
observation = data.get('observation', {})
print(f"✓ Environment initialized")
print(f"  Task: {observation.get('task_id')}")

# Run episode
episode_log = []
total_reward = 0.0
max_steps = 5

for step in range(max_steps):
    email = observation.get('email', {})
    email_id = email.get('email_id')
    subject = email.get('subject', '')[:50]
    sender_history = email.get('sender_history', 0)
    clv = email.get('customer_lifetime_value', 0)
    
    print(f"\n[STEP {step + 1}] Processing: {email_id}")
    print(f"  Subject: {subject}...")
    print(f"  Sender History: {sender_history}, CLV: {clv:.2f}")
    
    # Determine action based on email content
    if "CRITICAL" in subject or "URGENT" in subject or clv > 0.9:
        priority = "critical" if clv > 0.9 or "CRITICAL" in subject else "high"
    elif sender_history > 5 or clv > 0.5:
        priority = "high"
    else:
        priority = "medium"
    
    action = {
        "task_id": "email_priority_classification",
        "classify_priority": {
            "priority": priority,
            "confidence": 0.8
        }
    }
    
    # Send action
    response = requests.post(f"{BASE_URL}/step", json=action, timeout=10, verify=False)
    if response.status_code != 200:
        print(f"  ✗ Step failed: {response.text[:200]}")
        break
    
    result = response.json()
    reward = result.get('reward', {})
    episode_reward = reward.get('episode_reward', 0)
    cumulative = reward.get('cumulative_reward', 0)
    done = reward.get('is_done', False)
    
    total_reward += episode_reward
    
    print(f"  Action: Classify as '{priority}'")
    print(f"  Reward: {episode_reward:+.2f} | Cumulative: {cumulative:.2f}")
    
    episode_log.append({
        "step": step + 1,
        "email_id": email_id,
        "priority": priority,
        "reward": episode_reward,
        "cumulative": cumulative
    })
    
    if done:
        print(f"\n✓ Episode complete!")
        break
    
    # Get next observation
    response = requests.get(f"{BASE_URL}/state", timeout=10, verify=False)
    if response.status_code == 200:
        state_data = response.json()
        observation = {
            'task_id': state_data['state']['task_id'],
            'email': state_data['state']['current_email']
        }

# Summary
print("\n" + "=" * 70)
print("EPISODE SUMMARY")
print("=" * 70)
print(f"Total Steps: {len(episode_log)}")
print(f"Final Reward: {total_reward:.2f}")
print(f"Average Reward per Step: {total_reward / len(episode_log):.2f}")
print("\nStep Details:")
for log in episode_log:
    print(f"  step={log['step']} | email={log['email_id']} | priority={log['priority']} | reward={log['reward']:+.2f}")
print("\n✓ Inference test successful!")
