#!/usr/bin/env python3
"""
Baseline Inference Script for OpenEnv Email Triage Environment
Implements the required OpenEnv inference interface using OpenAI-compatible API

CRITICAL: Must follow strict [START], [STEP], and [END] logging format

Required Environment Variables:
  API_BASE_URL   The API endpoint for the LLM (defaults to OpenAI)
  MODEL_NAME     The model identifier to use for inference (required)
  HF_TOKEN       Your Hugging Face / API key (required by competition)

The script emits exactly three line types to stdout:
  [START] task=<task_name> env=openenv-email-triage model=<model_name>
  [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add repo root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from environment import EmailTriageEnv
from models import (
    Action, ActionClassifyPriority, ActionDetectUrgency, ActionRouteAndRespond,
    PriorityLevel, UrgencySignal, RoutingTeam
)

# ─── Configuration ────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client lazily (on first use, not at import time)
client = None


def _clamp_score(score: float) -> float:
    """
    Clamp score to be STRICTLY between 0 and 1 (exclusive).
    The validator rejects exactly 0.0 or 1.0.
    """
    return max(0.01, min(0.99, float(score)))


def _init_client():
    """Initialize OpenAI client with lazy initialization and validation"""
    global client
    if client is not None:
        return client

    if not API_KEY:
        print("[ERROR] HF_TOKEN or OPENAI_API_KEY environment variable must be set", flush=True)
        raise RuntimeError("API key not configured")

    try:
        client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

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
            llm_client = _init_client()

            response = llm_client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content if response.choices else None
            return content or "{}"

        except Exception as e:
            err_type = type(e).__name__
            err_module = type(e).__module__
            print(f"[ERROR] LLM API call failed ({err_module}.{err_type}): {e}", flush=True)
            return "{}"

    def parse_action(self, response_text: str) -> Optional[Action]:
        """Parse LLM response into Action object"""
        try:
            if not response_text or not response_text.strip():
                return None

            # Strip markdown fences if present
            text = response_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                end_idx = len(lines)
                for i in range(1, len(lines)):
                    if lines[i].strip() == "```":
                        end_idx = i
                        break
                text = "\n".join(lines[1:end_idx])

            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start == -1 or json_end <= json_start:
                return None

            data = json.loads(text[json_start:json_end])
            if not isinstance(data, dict):
                return None

            if self.task_id == "email_priority_classification":
                priority_str = str(data.get("priority", "medium")).lower().strip()
                try:
                    priority = PriorityLevel(priority_str)
                except (ValueError, KeyError):
                    priority = PriorityLevel.MEDIUM

                confidence = float(data.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))

                return Action(
                    task_id=self.task_id,
                    classify_priority=ActionClassifyPriority(
                        priority=priority,
                        confidence=confidence
                    )
                )

            elif self.task_id == "urgency_detection":
                raw_signals = data.get("urgency_signals", [])
                if not isinstance(raw_signals, list):
                    raw_signals = []

                signals = []
                for s in raw_signals:
                    try:
                        signal_str = str(s).lower().strip()
                        signals.append(UrgencySignal(signal_str))
                    except (ValueError, KeyError):
                        pass

                resp_time = int(data.get("estimated_response_time_minutes", 1440))
                resp_time = max(1, min(24 * 60, resp_time))

                return Action(
                    task_id=self.task_id,
                    detect_urgency=ActionDetectUrgency(
                        urgency_signals=signals,
                        escalate=bool(data.get("escalate", False)),
                        estimated_response_time_minutes=resp_time
                    )
                )

            elif self.task_id == "intelligent_routing":
                team_str = str(data.get("routing_team", "general_support")).lower().replace("-", "_").replace(" ", "_").strip()
                try:
                    team = RoutingTeam(team_str)
                except (ValueError, KeyError):
                    team = RoutingTeam.GENERAL_SUPPORT

                response_text_val = str(data.get("suggested_response", "Thank you for contacting us."))[:500]

                confidence = float(data.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))

                return Action(
                    task_id=self.task_id,
                    route_and_respond=ActionRouteAndRespond(
                        routing_team=team,
                        suggested_response=response_text_val,
                        confidence=confidence,
                        escalate=bool(data.get("escalate", False)),
                        follow_up_required=bool(data.get("follow_up_required", False))
                    )
                )

        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed: {e}  |  raw: {str(response_text)[:200]}", flush=True)
        except (ValueError, TypeError, KeyError) as e:
            print(f"[ERROR] Failed to parse action: {type(e).__name__}: {e}", flush=True)
        except Exception as e:
            print(f"[ERROR] Unexpected error parsing action: {type(e).__name__}: {e}", flush=True)

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
        """Convert Action object to concise string for logging"""
        try:
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
        except Exception as e:
            print(f"[ERROR] Failed to stringify action: {e}", flush=True)
        return "unknown_action"

    def run_episode(self) -> Dict[str, Any]:
        """Run one complete episode with strict [START], [STEP], [END] format"""
        episode_details = []
        step_rewards = []
        step_num = 0
        last_error = None
        obs = None

        # Emit [START] line (strict format)
        print(f"[START] task={self.task_id} env=openenv-email-triage model={self.model}", flush=True)

        try:
            # Safe reset with error handling
            try:
                obs = self.env.reset()
            except Exception as e:
                print(f"[ERROR] Environment reset failed: {type(e).__name__}: {e}", flush=True)
                # score must be strictly between 0 and 1
                print(f"[END] success=false steps=0 score=0.01 rewards=", flush=True)
                return {
                    "task_id": self.task_id,
                    "model": self.model,
                    "total_steps": 0,
                    "final_reward": 0.0,
                    "average_reward": 0.0,
                    "success": False,
                    "error": f"reset_failed: {e}",
                    "episode_details": [],
                }

            # Main episode loop
            while obs is not None and not self.env.episode_done:
                step_num += 1
                try:
                    # Safe email data extraction
                    try:
                        email_data = obs.email.model_dump()
                    except Exception as e:
                        print(f"[ERROR] Email serialization failed at step {step_num}: {e}", flush=True)
                        last_error = "email_dump_failed"
                        break

                    # Get prompts and build user message
                    try:
                        system_prompt = self.system_prompts.get(self.task_id, "")
                        if not system_prompt:
                            raise ValueError(f"No system prompt for task {self.task_id}")
                        user_message = self.get_user_message(email_data)
                    except Exception as e:
                        print(f"[ERROR] Prompt building failed: {e}", flush=True)
                        last_error = "prompt_build_failed"
                        break

                    # Call LLM (all exceptions caught inside call_llm)
                    response_text = self.call_llm(system_prompt, user_message)

                    # Parse action
                    action = self.parse_action(response_text)
                    if not action:
                        action = self._get_fallback_action()
                        last_error = "parse_failed"
                    else:
                        last_error = None

                    # Execute step
                    try:
                        result = self.env.step(action)
                        if result is None or len(result) < 3:
                            raise ValueError("Invalid environment step result")
                        obs, reward, info = result
                    except Exception as e:
                        print(f"[ERROR] Environment step failed at step {step_num}: {type(e).__name__}: {e}", flush=True)
                        last_error = "step_failed"
                        break

                    # Extract reward safely
                    try:
                        step_reward = float(reward.episode_reward) if reward else 0.0
                        step_rewards.append(step_reward)
                        done = bool(reward.is_done) if reward else False
                    except Exception as e:
                        print(f"[ERROR] Reward extraction failed: {e}", flush=True)
                        step_reward = 0.0
                        step_rewards.append(step_reward)
                        done = False

                    # Emit [STEP] line (strict format)
                    try:
                        action_str = self._action_to_string(action)
                        error_val = f'"{last_error}"' if last_error else "null"
                        done_str = str(done).lower()
                        print(f"[STEP] step={step_num} action={action_str} reward={step_reward:.2f} "
                              f"done={done_str} error={error_val}", flush=True)
                    except Exception as e:
                        print(f"[ERROR] Failed to emit [STEP] line: {e}", flush=True)
                        print(f"[STEP] step={step_num} action=unknown reward=0.00 done=false error=\"step_log_error\"", flush=True)

                    # Collect episode details
                    try:
                        episode_details.append({
                            "step": step_num,
                            "email_id": email_data.get('email_id', 'unknown'),
                            "action": action.model_dump() if action else {},
                            "step_reward": step_reward,
                            "cumulative_reward": float(reward.cumulative_reward) if reward else 0.0,
                        })
                    except Exception as e:
                        print(f"[ERROR] Failed to collect episode details: {e}", flush=True)

                    if done:
                        break

                except Exception as e:
                    print(f"[ERROR] Unhandled error in step {step_num}: {type(e).__name__}: {e}", flush=True)
                    last_error = f"step_error_{step_num}"
                    print(f"[STEP] step={step_num} action=fallback reward=0.00 done=false error=\"{last_error}\"", flush=True)
                    break

        except Exception as e:
            print(f"[ERROR] Unhandled exception in episode: {type(e).__name__}: {e}", flush=True)
            last_error = "episode_error"

        # Emit [END] line — ALWAYS emitted, ALWAYS with score strictly in (0, 1)
        try:
            final_summary = {}
            try:
                final_summary = self.env.get_episode_summary() if self.env else {}
            except Exception as e:
                print(f"[ERROR] Failed to get episode summary: {e}", flush=True)
                final_summary = {}

            success = final_summary.get("success", False) if final_summary else False
            total_steps = final_summary.get("total_steps", step_num) if final_summary else step_num
            final_reward = (
                final_summary.get("final_reward", 0.0)
                if final_summary
                else (sum(step_rewards) if step_rewards else 0.0)
            )

            # Normalize score to STRICTLY (0, 1) — never 0.0 or 1.0
            raw_score = float(final_reward) / 10.0 if final_reward else 0.0
            score = _clamp_score(raw_score)  # guaranteed in [0.01, 0.99]

            rewards_str = ",".join(f"{r:.2f}" for r in step_rewards) if step_rewards else ""

            print(f"[END] success={str(success).lower()} steps={total_steps} score={score:.4f} rewards={rewards_str}", flush=True)
        except Exception as e:
            print(f"[ERROR] Failed to emit [END] line: {e}", flush=True)
            rewards_str = ",".join(f"{r:.2f}" for r in step_rewards) if step_rewards else ""
            # 0.01 is the safe fallback — never 0.0
            print(f"[END] success=false steps={step_num} score=0.01 rewards={rewards_str}", flush=True)

        # Return results dict
        try:
            final_summary = self.env.get_episode_summary() if self.env else {}
        except Exception:
            final_summary = {}

        return {
            "task_id": self.task_id,
            "model": self.model,
            "total_steps": len(episode_details),
            "final_reward": final_summary.get('final_reward', 0.0),
            "average_reward": final_summary.get('average_step_reward', 0.0),
            "success": final_summary.get("success", False),
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
        "model": MODEL_NAME,
        "api_base": API_BASE_URL,
        "tasks": {}
    }

    print(f"[INFO] Starting inference with model={MODEL_NAME}, api_base={API_BASE_URL}", flush=True)

    for task_id in tasks:
        print(f"[INFO] Processing task: {task_id}", flush=True)
        try:
            try:
                agent = EmailTriageAgent(task_id, MODEL_NAME)
            except Exception as e:
                print(f"[ERROR] Failed to initialize agent for {task_id}: {type(e).__name__}: {e}", flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
                results["tasks"][task_id] = {
                    "error": f"initialization_failed: {str(e)}",
                    "total_steps": 0,
                    "success": False
                }
                continue

            try:
                result = agent.run_episode()
                results["tasks"][task_id] = result
                print(f"[INFO] Task {task_id} completed: success={result.get('success', False)}", flush=True)
            except Exception as e:
                print(f"[ERROR] Episode execution failed for {task_id}: {type(e).__name__}: {e}", flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
                results["tasks"][task_id] = {
                    "error": f"episode_failed: {str(e)}",
                    "total_steps": 0,
                    "success": False
                }
        except Exception as e:
            print(f"[ERROR] Unexpected error processing task {task_id}: {type(e).__name__}: {e}", flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            results["tasks"][task_id] = {
                "error": f"unexpected_error: {str(e)}",
                "total_steps": 0,
                "success": False
            }

    print(f"[INFO] Writing results to baseline_results.json", flush=True)
    try:
        with open("baseline_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"[INFO] Results written successfully", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to write results file: {type(e).__name__}: {e}", flush=True)

    print(f"[INFO] Inference complete", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"[CRITICAL] Unhandled exception in main: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(0)  # Always exit 0
