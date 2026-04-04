#!/usr/bin/env python3
"""
Quick manual test of inference script (without OpenAI calls)
Tests the action parsing and reward logic
"""

from environment import EmailTriageEnv
from models import (
    Action, ActionClassifyPriority, ActionDetectUrgency, ActionRouteAndRespond,
    PriorityLevel, UrgencySignal, RoutingTeam
)


def test_inference_logic():
    """Test inference logic without OpenAI API"""
    print("\n" + "="*60)
    print("Testing Inference Logic")
    print("="*60 + "\n")

    tasks = [
        ("email_priority_classification", "Priority Classification"),
        ("urgency_detection", "Urgency Detection"),
        ("intelligent_routing", "Intelligent Routing"),
    ]

    for task_id, task_name in tasks:
        print(f"\n--- {task_name} ---\n")

        env = EmailTriageEnv(task_id, seed=42)
        obs = env.reset()

        print(f"Email: {obs.email.email_id}")
        print(f"Subject: {obs.email.subject}")

        if task_id == "email_priority_classification":
            action = Action(
                task_id=task_id,
                classify_priority=ActionClassifyPriority(
                    priority=PriorityLevel.HIGH,
                    confidence=0.85
                )
            )
        elif task_id == "urgency_detection":
            action = Action(
                task_id=task_id,
                detect_urgency=ActionDetectUrgency(
                    urgency_signals=[UrgencySignal.COMPLAINT],
                    escalate=False,
                    estimated_response_time_minutes=1440
                )
            )
        else:
            action = Action(
                task_id=task_id,
                route_and_respond=ActionRouteAndRespond(
                    routing_team=RoutingTeam.GENERAL_SUPPORT,
                    suggested_response="Thank you for contacting us.",
                    confidence=0.7,
                    escalate=False,
                    follow_up_required=False
                )
            )

        obs_new, reward, info = env.step(action)

        print(f"\nReward: {reward.episode_reward:.3f}")
        print(f"Grading Details: {info['grading_details']}")

    print("\n" + "="*60)
    print("Inference logic test complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_inference_logic()
