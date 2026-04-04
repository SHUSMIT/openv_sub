#!/usr/bin/env python3
"""
Local validation script - Tests environment without OpenAI API
Verifies OpenEnv spec compliance and basic functionality
"""

import sys
import json
from typing import Dict, Any

from env.environment import EmailTriageEnv
from env.models import (
    Action, ActionClassifyPriority, ActionDetectUrgency, ActionRouteAndRespond,
    PriorityLevel, UrgencySignal, RoutingTeam
)
from env.tasks.definitions import get_task_config, TASK_CONFIGS
from env.graders.task_graders import EmailPriorityGrader, UrgencyDetectionGrader, IntelligentRoutingGrader


def test_task_configs() -> bool:
    """Test that all tasks have proper configs"""
    print("\n" + "="*60)
    print("TEST: Task Configurations")
    print("="*60)

    expected_tasks = ["email_priority_classification", "urgency_detection", "intelligent_routing"]

    for task_id in expected_tasks:
        config = get_task_config(task_id)
        if not config:
            print(f"FAIL Task {task_id} missing config")
            return False

        required_keys = ["name", "description", "difficulty", "emails_per_episode", "max_steps"]
        for key in required_keys:
            if key not in config:
                print(f"FAIL Task {task_id} missing key: {key}")
                return False

        print(f"PASS {task_id}: {config['name']} ({config['difficulty']})")

    print(f"\nTotal tasks: {len(TASK_CONFIGS)}")
    return True


def test_environment_init() -> bool:
    """Test environment initialization"""
    print("\n" + "="*60)
    print("TEST: Environment Initialization")
    print("="*60)

    for task_id in ["email_priority_classification", "urgency_detection", "intelligent_routing"]:
        try:
            env = EmailTriageEnv(task_id=task_id, seed=42)
            print(f"PASS {task_id} initialized")
        except Exception as e:
            print(f"FAIL {task_id} failed: {e}")
            return False

    return True


def test_reset() -> bool:
    """Test reset() endpoint"""
    print("\n" + "="*60)
    print("TEST: Reset Endpoint")
    print("="*60)

    env = EmailTriageEnv("email_priority_classification", seed=42)
    obs = env.reset()

    if not obs:
        print("FAIL Reset returned None")
        return False

    if not obs.email:
        print("FAIL Observation missing email")
        return False

    if obs.task_id != "email_priority_classification":
        print(f"FAIL Task ID mismatch: {obs.task_id}")
        return False

    print(f"PASS Reset successful")
    print(f"  - Email ID: {obs.email.email_id}")
    print(f"  - Subject: {obs.email.subject[:50]}...")
    print(f"  - Task: {obs.task_id}")

    return True


def test_priority_classification() -> bool:
    """Test Task 1: Priority Classification"""
    print("\n" + "="*60)
    print("TEST: Task 1 - Priority Classification")
    print("="*60)

    env = EmailTriageEnv("email_priority_classification", seed=42)
    obs = env.reset()

    action = Action(
        task_id="email_priority_classification",
        classify_priority=ActionClassifyPriority(
            priority=PriorityLevel.HIGH,
            confidence=0.85
        )
    )

    try:
        obs_new, reward, info = env.step(action)

        if reward.episode_reward is None:
            print("FAIL Reward missing episode_reward")
            return False

        if not (-1.0 <= reward.episode_reward <= 1.0):
            print(f"FAIL Reward out of range: {reward.episode_reward}")
            return False

        print(f"PASS Step successful")
        print(f"  - Reward: {reward.episode_reward:.3f}")
        print(f"  - Cumulative: {reward.cumulative_reward:.3f}")
        print(f"  - Done: {reward.is_done}")
        print(f"  - Grading: {info['grading_details']}")

        return True
    except Exception as e:
        print(f"FAIL Step failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_urgency_detection() -> bool:
    """Test Task 2: Urgency Detection"""
    print("\n" + "="*60)
    print("TEST: Task 2 - Urgency Detection")
    print("="*60)

    env = EmailTriageEnv("urgency_detection", seed=42)
    obs = env.reset()

    action = Action(
        task_id="urgency_detection",
        detect_urgency=ActionDetectUrgency(
            urgency_signals=[UrgencySignal.COMPLAINT, UrgencySignal.VIP_CUSTOMER],
            escalate=True,
            estimated_response_time_minutes=60
        )
    )

    try:
        obs_new, reward, info = env.step(action)

        if not (-1.0 <= reward.episode_reward <= 1.0):
            print(f"FAIL Reward out of range: {reward.episode_reward}")
            return False

        print(f"PASS Step successful")
        print(f"  - Reward: {reward.episode_reward:.3f}")
        print(f"  - Cumulative: {reward.cumulative_reward:.3f}")

        return True
    except Exception as e:
        print(f"FAIL Step failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intelligent_routing() -> bool:
    """Test Task 3: Intelligent Routing"""
    print("\n" + "="*60)
    print("TEST: Task 3 - Intelligent Routing")
    print("="*60)

    env = EmailTriageEnv("intelligent_routing", seed=42)
    obs = env.reset()

    action = Action(
        task_id="intelligent_routing",
        route_and_respond=ActionRouteAndRespond(
            routing_team=RoutingTeam.ESCALATION,
            suggested_response="Thank you for contacting us. We'll assist immediately.",
            confidence=0.9,
            escalate=True,
            follow_up_required=True
        )
    )

    try:
        obs_new, reward, info = env.step(action)

        if not (-1.0 <= reward.episode_reward <= 1.0):
            print(f"FAIL Reward out of range: {reward.episode_reward}")
            return False

        print(f"PASS Step successful")
        print(f"  - Reward: {reward.episode_reward:.3f}")
        print(f"  - Cumulative: {reward.cumulative_reward:.3f}")

        return True
    except Exception as e:
        print(f"FAIL Step failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_episode() -> bool:
    """Test complete episode"""
    print("\n" + "="*60)
    print("TEST: Full Episode")
    print("="*60)

    env = EmailTriageEnv("email_priority_classification", seed=42)
    obs = env.reset()

    step_count = 0
    total_reward = 0.0

    while not env.episode_done and step_count < 10:
        action = Action(
            task_id="email_priority_classification",
            classify_priority=ActionClassifyPriority(
                priority=PriorityLevel.MEDIUM,
                confidence=0.5
            )
        )

        obs, reward, info = env.step(action)
        total_reward += reward.episode_reward
        step_count += 1

    summary = env.get_episode_summary()

    print(f"PASS Episode complete")
    print(f"  - Steps: {step_count}")
    print(f"  - Final Reward: {summary['final_reward']:.3f}")
    print(f"  - Average Reward: {summary['average_step_reward']:.3f}")
    print(f"  - Success: {summary['success']}")

    return True


def test_state_endpoint() -> bool:
    """Test state() endpoint"""
    print("\n" + "="*60)
    print("TEST: State Endpoint")
    print("="*60)

    env = EmailTriageEnv("email_priority_classification", seed=42)
    obs = env.reset()

    action = Action(
        task_id="email_priority_classification",
        classify_priority=ActionClassifyPriority(
            priority=PriorityLevel.HIGH,
            confidence=0.85
        )
    )
    obs, reward, info = env.step(action)

    state = env.state()

    if not state:
        print("FAIL State returned None")
        return False

    if state.episode_step != 1:
        print(f"FAIL Episode step mismatch: {state.episode_step}")
        return False

    if state.emails_processed != 1:
        print(f"FAIL Emails processed mismatch: {state.emails_processed}")
        return False

    print(f"PASS State endpoint successful")
    print(f"  - Episode Step: {state.episode_step}")
    print(f"  - Emails Processed: {state.emails_processed}")
    print(f"  - Cumulative Reward: {state.cumulative_reward:.3f}")
    print(f"  - Episode Complete: {state.episode_complete}")

    return True


def test_determinism() -> bool:
    """Test that same seed produces same results"""
    print("\n" + "="*60)
    print("TEST: Determinism (Same Seed)")
    print("="*60)

    env1 = EmailTriageEnv("email_priority_classification", seed=999)
    obs1 = env1.reset()
    email_id_1 = obs1.email.email_id

    env2 = EmailTriageEnv("email_priority_classification", seed=999)
    obs2 = env2.reset()
    email_id_2 = obs2.email.email_id

    if email_id_1 != email_id_2:
        print(f"FAIL Same seed produced different emails: {email_id_1} vs {email_id_2}")
        return False

    print(f"PASS Determinism verified")
    print(f"  - Both runs started with: {email_id_1}")

    return True


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print(" OPENENV EMAIL TRIAGE - LOCAL VALIDATION ".center(60))
    print("=" * 60)

    tests = [
        ("Task Configurations", test_task_configs),
        ("Environment Initialization", test_environment_init),
        ("Reset Endpoint", test_reset),
        ("Task 1: Priority Classification", test_priority_classification),
        ("Task 2: Urgency Detection", test_urgency_detection),
        ("Task 3: Intelligent Routing", test_intelligent_routing),
        ("Full Episode", test_full_episode),
        ("State Endpoint", test_state_endpoint),
        ("Determinism", test_determinism),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\nEXCEPTION in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status:6} {name}")

    print("\n" + "-"*60)
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll validation tests passed!")
        print("Environment is ready for deployment.")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed.")
        print("Please fix errors before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
