#!/usr/bin/env python3
"""
Baseline Inference Script for OpenEnv Email Triage Environment
Uses OpenAI-compatible API (supports OpenAI, Groq, or any OpenAI-compatible provider)

CRITICAL: Must follow strict [START], [STEP], and [END] logging format

Environment Variables:
  OPENAI_API_KEY        - OpenAI API key (for OpenAI models)
  GROQ_API_KEY          - Groq API key (for Groq models - FREE!)
  MODEL_NAME            - Model identifier (gpt-4, mixtral-8x7b-32768, etc.)
  API_BASE_URL          - API endpoint (defaults to OpenAI)

Examples:
  # OpenAI
  export OPENAI_API_KEY="sk-..." && export MODEL_NAME="gpt-4" && python inference.py

  # Groq (FREE!)
  export GROQ_API_KEY="gsk-..." && export MODEL_NAME="mixtral-8x7b-32768" && \\
  export API_BASE_URL="https://api.groq.com/openai/v1" && python inference.py
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add repo root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from env.environment import EmailTriageEnv
from env.models import (
    Action, ActionClassifyPriority, ActionDetectUrgency, ActionRouteAndRespond,
    PriorityLevel, UrgencySignal, RoutingTeam
)

# ─── Configuration ────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

is_groq = "groq.com" in API_BASE_URL or (GROQ_API_KEY and not OPENAI_API_KEY)
api_key = GROQ_API_KEY if is_groq else OPENAI_API_KEY

if not api_key:
    print("[ERROR] Neither OPENAI_API_KEY nor GROQ_API_KEY environment variable set")
    print("\nUsage:")
    print("  OpenAI:  export OPENAI_API_KEY='sk-...' && python inference.py")
    print("  Groq:    export GROQ_API_KEY='gsk-...' && export API_BASE_URL='https://api.groq.com/openai/v1' && python inference.py")
    sys.exit(1)

# Initialize OpenAI-compatible client
# For Groq we pass base_url; for OpenAI we use the default
if API_BASE_URL != "https://api.openai.com/v1":
    client = OpenAI(api_key=api_key, base_url=API_BASE_URL)
else:
    client = OpenAI(api_key=api_key)

provider = "Groq" if is_groq else "OpenAI"
# ──────────────────────────────────────────────────────────────────────────────


class EmailTriageAgent:
    """AI Agent for email triage using OpenAI-compatible API"""

    def __init__(self, task_id: str, model_name: str):
        self.task_id = task_id
        self.model = model_name
        self.env = EmailTriageEnv(task_id=task_id, seed=42)

        self.system_prompts = {
            "email_priority_classification": (
                "You are an expert email triage system. Your task is to classify incoming "
                "customer support emails into 4 priority levels:\n"
                "- CRITICAL (0): Immediate attention required, production issues, angry customers\n"
                "- HIGH (1): Urgent but not breaking, billing issues, technical problems\n"
                "- MEDIUM (2): Normal workflow, can wait a few hours\n"
                "- LOW (3): Can wait, informational requests, feedback\n\n"
                "Respond with ONLY a JSON object (no markdown, no extra text):\n"
                '{"priority": "critical|high|medium|low", "confidence": 0.0-1.0, "reasoning": "brief explanation"}'
            ),
            "urgency_detection": (
                "You are an expert at detecting urgency signals in customer emails.\n\n"
                "Detect any of these signals:\n"
                "DEADLINE, COMPLAINT, URGENT_KEYWORD, REPEAT_CONTACT, VIP_CUSTOMER, SERVICE_OUTAGE, PAYMENT_ISSUE, NONE\n\n"
                "Respond with ONLY a JSON object (no markdown, no extra text):\n"
                '{"urgency_signals": ["signal1"], "escalate": true, "estimated_response_time_minutes": 60, "reasoning": "brief"}'
            ),
            "intelligent_routing": (
                "You are an expert email routing system. Route emails to one of:\n"
                "billing, technical_support, sales, general_support, escalation, feedback\n\n"
                "Respond with ONLY a JSON object (no markdown, no extra text):\n"
                '{"routing_team": "billing", "suggested_response": "...", "confidence": 0.9, "escalate": false, "follow_up_required": false, "reasoning": "brief"}'
            ),
        }

    def get_user_message(self, email_data: Dict[str, Any]) -> str:
        """Build user message for the email"""
        return (
            f"Subject: {email_data['subject']}\n"
            f"Sender: {email_data['sender']}\n"
            f"Body: {email_data['body']}\n\n"
            f"Context:\n"
            f"- Sender history: {email_data.get('sender_history', 0)} previous emails\n"
            f"- Is reply: {email_data.get('is_reply', False)}\n"
            f"- Attachments: {email_data.get('attachments', 0)}\n"
            f"- Customer value: {email_data.get('customer_lifetime_value', 0):.1%}"
        )

    def call_llm(self, system_prompt: str, user_message: str) -> str:
        """Call the LLM via OpenAI-compatible chat completions API"""
        try:
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content or "{}"
        except Exception as e:
            print(f"[ERROR] LLM API call failed: {e}")
            return "{}"

    def parse_action(self, response_text: str) -> Optional[Action]:
        """Parse LLM response into Action object"""
        try:
            # Strip markdown fences if present
            text = response_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                return None

            data = json.loads(text[json_start:json_end])

            if self.task_id == "email_priority_classification":
                priority = PriorityLevel(data["priority"].lower())
                return Action(
                    task_id=self.task_id,
                    classify_priority=ActionClassifyPriority(
                        priority=priority,
                        confidence=float(data.get("confidence", 0.5))
                    )
                )

            elif self.task_id == "urgency_detection":
                raw_signals = data.get("urgency_signals", [])
                signals = []
                for s in raw_signals:
                    try:
                        signals.append(UrgencySignal(s.lower()))
                    except ValueError:
                        pass
                return Action(
                    task_id=self.task_id,
                    detect_urgency=ActionDetectUrgency(
                        urgency_signals=signals,
                        escalate=bool(data.get("escalate", False)),
                        estimated_response_time_minutes=int(data.get("estimated_response_time_minutes", 1440))
                    )
                )

            elif self.task_id == "intelligent_routing":
                team_str = data["routing_team"].lower().replace("-", "_").replace(" ", "_")
                team = RoutingTeam(team_str)
                response_text_val = str(data.get("suggested_response", "Thank you for contacting us."))[:500]
                return Action(
                    task_id=self.task_id,
                    route_and_respond=ActionRouteAndRespond(
                        routing_team=team,
                        suggested_response=response_text_val,
                        confidence=float(data.get("confidence", 0.5)),
                        escalate=bool(data.get("escalate", False)),
                        follow_up_required=bool(data.get("follow_up_required", False))
                    )
                )

        except Exception as e:
            print(f"[ERROR] Failed to parse action: {e}  |  raw: {response_text[:200]}")

        return None

    def _get_fallback_action(self) -> Action:
        """Generate fallback action when parsing fails"""
        if self.task_id == "email_priority_classification":
            return Action(
                task_id=self.task_id,
                classify_priority=ActionClassifyPriority(
                    priority=PriorityLevel.MEDIUM,
                    confidence=0.5
                )
            )
        elif self.task_id == "urgency_detection":
            return Action(
                task_id=self.task_id,
                detect_urgency=ActionDetectUrgency(
                    urgency_signals=[],
                    escalate=False,
                    estimated_response_time_minutes=1440
                )
            )
        else:
            return Action(
                task_id=self.task_id,
                route_and_respond=ActionRouteAndRespond(
                    routing_team=RoutingTeam.GENERAL_SUPPORT,
                    suggested_response="Thank you for contacting us. We will assist you shortly.",
                    confidence=0.5,
                    escalate=False,
                    follow_up_required=False
                )
            )

    def _action_to_string(self, action: Action) -> str:
        """Convert Action object to concise string representation for logging"""
        if action.classify_priority:
            return (f"classify_priority(priority={action.classify_priority.priority},"
                   f"confidence={action.classify_priority.confidence:.2f})")
        elif action.detect_urgency:
            signals = ",".join([s.value for s in action.detect_urgency.urgency_signals])
            return (f"detect_urgency(signals=[{signals}],"
                   f"escalate={str(action.detect_urgency.escalate).lower()})")
        elif action.route_and_respond:
            resp_preview = action.route_and_respond.suggested_response[:30].replace("\n", " ")
            return (f"route_and_respond(team={action.route_and_respond.routing_team},"
                   f"response='{resp_preview}...')")
        return "unknown_action"

    def run_episode(self) -> Dict[str, Any]:
        """Run one complete episode with strict [START], [STEP], [END] format"""
        obs = self.env.reset()
        episode_details = []
        step_rewards = []
        step_num = 0
        last_error = None

        # Emit [START] line (strict format)
        print(f"[START] task={self.task_id} env=openenv-email-triage model={self.model}", flush=True)

        try:
            while not self.env.episode_done:
                step_num += 1
                email_data = obs.email.model_dump()

                system_prompt = self.system_prompts[self.task_id]
                user_message = self.get_user_message(email_data)

                response_text = self.call_llm(system_prompt, user_message)

                action = self.parse_action(response_text)
                if not action:
                    action = self._get_fallback_action()
                    last_error = "parse_failed"

                obs, reward, info = self.env.step(action)

                step_reward = reward.episode_reward
                step_rewards.append(step_reward)
                done = reward.is_done

                # Emit [STEP] line (strict format)
                action_str = self._action_to_string(action)
                error_val = f'"{last_error}"' if last_error else "null"
                done_str = str(done).lower()
                print(f"[STEP] step={step_num} action={action_str} reward={step_reward:.2f} "
                      f"done={done_str} error={error_val}", flush=True)

                episode_details.append({
                    "step": step_num,
                    "email_id": email_data['email_id'],
                    "action": action.model_dump(),
                    "step_reward": step_reward,
                    "cumulative_reward": reward.cumulative_reward,
                })

                last_error = None

        except Exception as e:
            last_error = str(e)

        # Emit [END] line (strict format)
        final_summary = self.env.get_episode_summary()
        success = final_summary.get("success", False)
        total_steps = final_summary.get("total_steps", step_num)
        rewards_str = ",".join(f"{r:.2f}" for r in step_rewards)

        print(f"[END] success={str(success).lower()} steps={total_steps} rewards={rewards_str}", flush=True)

        return {
            "task_id": self.task_id,
            "model": self.model,
            "total_steps": total_steps,
            "final_reward": final_summary.get('final_reward', 0.0),
            "average_reward": final_summary.get('average_step_reward', 0.0),
            "success": success,
            "episode_details": episode_details,
        }


def main():
    """Run baseline evaluation on all tasks"""
    tasks = [
        "email_priority_classification",
        "urgency_detection",
        "intelligent_routing",
    ]

    results = {
        "timestamp": datetime.now().isoformat(),
        "provider": provider,
        "model": MODEL_NAME,
        "api_base": API_BASE_URL,
        "tasks": {}
    }

    for task_id in tasks:
        try:
            agent = EmailTriageAgent(task_id, MODEL_NAME)
            result = agent.run_episode()
            results["tasks"][task_id] = result
        except Exception as e:
            results["tasks"][task_id] = {"error": str(e)}
            import traceback
            traceback.print_exc()

    # Write results to file (not stdout - keep stdout clean)
    with open("baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
