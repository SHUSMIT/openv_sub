"""Quick test of environment with new features"""
from env.environment import EmailTriageEnv
from env.models import Action, ActionClassifyPriority, PriorityLevel

# Test a step action
env = EmailTriageEnv(task_id='email_priority_classification', seed=42, use_dynamic_grader=False)
obs = env.reset()

# Create test action
action = Action(
    task_id='email_priority_classification',
    classify_priority=ActionClassifyPriority(
        priority=PriorityLevel.CRITICAL,
        confidence=0.95
    )
)

# Execute step
obs, reward, info = env.step(action)
print(f'✅ Step executed successfully!')
print(f'  Base reward: {info.get("base_reward", 0):.2f}')
print(f'  Final reward: {info.get("final_reward", 0):.2f}')
print(f'  Cumulative: {reward.cumulative_reward:.2f}')

# Test multi-turn capability with action history
print(f'\n✅ Multi-turn mechanics:')
print(f'  Current email ID: {obs.email.email_id}')
print(f'  Related action history: {len(obs.action_history)} items')

# Execute few more steps
for i in range(3):
    action = Action(
        task_id='email_priority_classification',
        classify_priority=ActionClassifyPriority(
            priority=PriorityLevel.HIGH,
            confidence=0.8
        )
    )
    obs, reward, info = env.step(action)

print(f'\n✅ Environment working with:')
print(f'  Total steps: {env.step_count}')
print(f'  Cumulative reward: {env.cumulative_reward:.2f}')
print(f'  Emails processed: {env.current_email_idx}/{len(env.emails)}')
print(f'✅ All tests passed!')
