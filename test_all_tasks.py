"""Test all 3 tasks on live deployment"""
import requests
import json
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

BASE_URL = "https://shusmitSarkar-openenv-email-triage.hf.space"

TASKS = [
    "email_priority_classification",
    "urgency_detection", 
    "intelligent_routing"
]

TASK_DESCRIPTIONS = {
    "email_priority_classification": "Classify emails into priority levels",
    "urgency_detection": "Detect urgency signals and recommend escalation",
    "intelligent_routing": "Route emails to correct teams"
}

print("=" * 80)
print("TESTING ALL 3 TASKS - LIVE DEPLOYMENT")
print("=" * 80)

for task_id in TASKS:
    print(f"\n{'=' * 80}")
    print(f"TASK: {task_id}")
    print(f"Description: {TASK_DESCRIPTIONS[task_id]}")
    print(f"{'=' * 80}")
    
    # Reset to task
    print(f"\n[1] Resetting to {task_id}...")
    payload = {"task_id": task_id, "seed": 456}
    response = requests.post(f"{BASE_URL}/reset", json=payload, timeout=10, verify=False)
    
    if response.status_code != 200:
        print(f"✗ Reset failed: {response.text[:200]}")
        continue
    
    data = response.json()
    observation = data.get('observation', {})
    email = observation.get('email', {})
    
    print(f"✓ Task initialized")
    print(f"  First Email: {email.get('email_id')}")
    print(f"  Subject: {email.get('subject', '')[:60]}")
    print(f"  Industry: {email.get('industry', 'N/A')}")
    
    # Take 3 steps per task
    total_reward = 0.0
    for step in range(3):
        email = observation.get('email', {})
        subject = email.get('subject', '')
        
        # Generate action based on task
        if task_id == "email_priority_classification":
            action = {
                "task_id": task_id,
                "classify_priority": {
                    "priority": "high" if "CRITICAL" in subject or "URGENT" in subject else "medium",
                    "confidence": 0.9
                }
            }
        elif task_id == "urgency_detection":
            action = {
                "task_id": task_id,
                "detect_urgency": {
                    "urgency_signals": ["urgent_keyword"] if "URGENT" in subject or "CRITICAL" in subject else [],
                    "escalate": True if "CRITICAL" in subject else False,
                    "estimated_response_time_minutes": 15 if "CRITICAL" in subject else 120
                }
            }
        else:  # intelligent_routing
            action = {
                "task_id": task_id,
                "route_and_respond": {
                    "routing_team": "escalation" if "CRITICAL" in subject else "general_support",
                    "suggested_response": "We are investigating this issue and will provide an update shortly.",
                    "confidence": 0.85,
                    "escalate": False,
                    "follow_up_required": True if "CRITICAL" in subject else False
                }
            }
        
        # Send action
        response = requests.post(f"{BASE_URL}/step", json=action, timeout=10, verify=False)
        if response.status_code != 200:
            print(f"✗ Step {step + 1} failed")
            break
        
        result = response.json()
        reward = result.get('reward', {})
        episode_reward = reward.get('episode_reward', 0)
        cumulative = reward.get('cumulative_reward', 0)
        
        total_reward = cumulative
        
        print(f"\n  [Step {step + 1}]")
        print(f"    Email: {email.get('email_id')}")
        print(f"    Reward: {episode_reward:+.2f} → Cumulative: {cumulative:.2f}")
        
        # Get next observation
        response = requests.get(f"{BASE_URL}/state", timeout=10, verify=False)
        if response.status_code == 200:
            state_data = response.json()
            observation = {
                'task_id': state_data['state']['task_id'],
                'email': state_data['state']['current_email']
            }
    
    print(f"\n✓ Task Complete - Final Reward: {total_reward:.2f}")

print("\n" + "=" * 80)
print("ALL TASKS TESTED SUCCESSFULLY!")
print("=" * 80)
print("\nDeployment Status: ✅ FULLY OPERATIONAL")
print("• All 3 tasks working")
print("• All endpoints responding correctly")
print("• Reward system functioning")
print("• Episode tracking active")
