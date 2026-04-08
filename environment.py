"""
Main OpenEnv EmailTriage Environment with Enhanced Multi-turn Support
Implements the full OpenEnv spec: reset(), step(), state()
Now includes action history tracking and dynamic LLM-based grading
"""

import random
from typing import Tuple, Dict, Any, Optional, List
from datetime import datetime

from models import Email, Action, Observation, Reward, State, PriorityLevel
from definitions import get_emails_for_task, get_task_config
from task_graders import (
    EmailPriorityGrader,
    UrgencyDetectionGrader,
    IntelligentRoutingGrader,
)

try:
    from dynamic_grader import DynamicLLMGrader
except ModuleNotFoundError:
    class DynamicLLMGrader:  # type: ignore[no-redef]
        """Fallback stub used when dynamic grader module is unavailable in deployment."""

        def __init__(self, use_llm: bool = False):
            self.use_llm = False


class EmailTriageEnv:
    """
    Real-world email triage environment for AI agents with multi-turn mechanics.
    Features:
    - 150+ diverse emails across industries
    - Action history tracking for multi-turn consequences
    - Dynamic LLM-based grading for nuanced evaluation
    - Cascade scenarios where wrong decisions affect later emails
    """

    def __init__(self, task_id: str = "email_priority_classification", seed: int = None, use_dynamic_grader: bool = True):
        self.task_id = task_id
        self.seed_value = seed
        self.use_dynamic_grader = use_dynamic_grader

        if seed is not None:
            random.seed(seed)

        self.config = get_task_config(task_id)
        if not self.config:
            raise ValueError(f"Unknown task_id: {task_id}")

        # Initialize graders
        self.priority_grader = EmailPriorityGrader()
        self.urgency_grader = UrgencyDetectionGrader()
        self.routing_grader = IntelligentRoutingGrader()
        
        # Initialize dynamic grader if enabled
        self.dynamic_grader = DynamicLLMGrader(use_llm=use_dynamic_grader) if use_dynamic_grader else None

        # Episode state
        self.emails: List[Email] = []
        self.current_email_idx = 0
        self.step_count = 0
        self.episode_reward = 0.0
        self.cumulative_reward = 0.0
        self.episode_done = False
        self.episode_history: List[Dict[str, Any]] = []
        self.action_cache: Dict[str, Dict[str, Any]] = {}  # Cache actions by email_id for multi-turn refs

        # Initialize episode
        self.reset()

    def reset(self) -> Observation:
        """Reset environment for a new episode."""
        self.step_count = 0
        self.episode_reward = 0.0
        self.cumulative_reward = 0.0
        self.episode_done = False
        self.episode_history = []
        self.action_cache = {}

        self.emails = get_emails_for_task(self.task_id, seed=self.seed_value)
        self.current_email_idx = 0

        return self._get_observation()

    def _get_related_action_history(self, email: Email) -> List[Dict[str, Any]]:
        """Get action history for emails related to current one (multi-turn context)"""
        related_actions = []
        
        # If this email is a reply, include parent action
        if email.parent_email_id and email.parent_email_id in self.action_cache:
            related_actions.append({
                "email_id": email.parent_email_id,
                "relation": "parent_email",
                "action": self.action_cache[email.parent_email_id]
            })
        
        # If part of escalation chain, include chain history
        if email.escalation_chain:
            for chain_id in email.escalation_chain:
                if chain_id in self.action_cache:
                    related_actions.append({
                        "email_id": chain_id,
                        "relation": "escalation_chain",
                        "action": self.action_cache[chain_id]
                    })
        
        return related_actions

    def _get_observation(self) -> Observation:
        """Get current observation with action history"""
        try:
            if self.current_email_idx >= len(self.emails):
                return Observation(
                    email=Email(
                        email_id="episode_complete",
                        sender="system@env.local",
                        subject="Episode Complete",
                        body="No more emails to process",
                        timestamp=datetime.now().timestamp(),
                    ),
                    task_id=self.task_id,
                    step_count=self.step_count,
                    episode_info={
                        "total_emails": len(self.emails),
                        "emails_processed": self.current_email_idx,
                        "cumulative_reward": self.cumulative_reward,
                    },
                    action_history=[]
                )

            current_email = self.emails[self.current_email_idx]
            
            try:
                related_history = self._get_related_action_history(current_email)
            except Exception as e:
                print(f"[WARNING] Failed to get related action history: {e}")
                related_history = []

            return Observation(
                email=current_email,
                task_id=self.task_id,
                step_count=self.step_count,
                episode_info={
                    "total_emails": len(self.emails),
                    "emails_processed": self.current_email_idx,
                    "current_email_idx": self.current_email_idx,
                },
                action_history=related_history
            )
        except Exception as e:
            print(f"[ERROR] Failed to get observation: {type(e).__name__}: {e}")
            # Return a safe default observation
            return Observation(
                email=Email(
                    email_id="error_observation",
                    sender="system@env.local",
                    subject="Error",
                    body="Error generating observation",
                    timestamp=datetime.now().timestamp(),
                ),
                task_id=self.task_id,
                step_count=self.step_count,
                episode_info={"error": str(e)},
                action_history=[]
            )

    def _apply_multi_turn_consequences(self, email: Email, base_reward: float, action: Action) -> float:
        """
        Apply reward multipliers based on multi-turn context and cascade scenarios
        - Good handling of follow-ups after mistakes gets bonus
        - Wrong decisions in cascade scenarios have negative effects
        - VIP handling is critical
        - System outages demand immediate action
        """
        final_reward = base_reward
        
        # VIP Customer Special Handling
        if email.customer_lifetime_value > 0.9 or email.scenario_context == "vip_opportunity":
            if base_reward > 0.8:
                final_reward = base_reward * 1.5  # 50% bonus for excellent VIP handling
            elif base_reward < 0.3:
                final_reward = base_reward * 0.5  # Heavy penalty for poor VIP handling (reputational risk)
        
        # System Outage / Emergency Scenarios
        if "outage" in email.subject.lower() or email.scenario_context and "outage" in email.scenario_context:
            if base_reward > 0.7:
                final_reward = base_reward * 1.4  # Bonus for quick critical response
            else:
                final_reward = base_reward * 0.7  # Penalty for slow critical response
        
        # Security/Compliance - Zero tolerance for wrong handling
        if "security" in email.subject.lower() or "breach" in email.subject.lower() or "vulnerability" in email.subject.lower():
            if base_reward > 0.8:
                final_reward = base_reward * 1.3
            else:
                final_reward = base_reward * 0.4  # Heavy penalty for security mishandling
        
        # Check if this is a follow-up and previous action exists
        if email.parent_email_id and email.parent_email_id in self.action_cache:
            prev_action_data = self.action_cache[email.parent_email_id]
            prev_reward = prev_action_data.get("reward", 0.0)
            
            # If previous was poor, make follow-up more important
            if prev_reward < 0.3:
                if base_reward > 0.7:
                    final_reward = base_reward * 1.3  # Bonus for recovery after previous failure
                else:
                    final_reward = base_reward * 0.7  # Penalty for compounding failure
            elif prev_reward > 0.8 and base_reward < 0.5:
                # Regression after good action  
                final_reward = base_reward * 0.8
        
        # Cascade scenarios: wrong decision affects later emails
        if email.scenario_context and "cascade" in email.scenario_context:
            # Look back for related failures
            for history_item in self.episode_history:
                if "cascade" in history_item.get("email_id", ""):
                    prev_cascade_reward = history_item.get("reward", 0.0)
                    if prev_cascade_reward < 0.5:
                        # Previous poor handling of cascade, this is critical recovery
                        if base_reward > 0.8:
                            final_reward = base_reward * 1.3  # Recovery bonus
                        else:
                            final_reward = base_reward * 0.6  # Compounds problem
        
        # Emergent Complexity: Time-critical scenarios
        if email.scenario_context and "deadline" in email.scenario_context.lower():
            if base_reward > 0.7:
                final_reward = base_reward * 1.2  # Bonus for meeting urgent deadline
            else:
                final_reward = base_reward * 0.8  # Penalty for missing deadline
        
        # Enterprise/Strategic opportunities
        if email.scenario_context and ("enterprise" in email.scenario_context.lower() or "partnership" in email.scenario_context.lower()):
            if base_reward > 0.8:
                final_reward = base_reward * 1.4  # Significant bonus for winning deals
            else:
                final_reward = base_reward * 0.5  # Loss potential is high
        
        return final_reward

    def _get_grading(self, email: Email, action: Action) -> Tuple[float, Dict[str, Any]]:
        """Get grading using dynamic LLM grader if available, else fallback to rule-based"""
        if not self.dynamic_grader or not self.dynamic_grader.use_llm:
            # Use standard graders
            if self.task_id == "email_priority_classification":
                return self.priority_grader.grade(email, action)
            elif self.task_id == "urgency_detection":
                return self.urgency_grader.grade(email, action)
            elif self.task_id == "intelligent_routing":
                return self.routing_grader.grade(email, action)
            else:
                from task_graders import normalize_score
                return normalize_score(0.5), {"error": "Unknown task"}
        
        # Use dynamic LLM grader
        try:
            if self.task_id == "email_priority_classification":
                return self.dynamic_grader.grade_priority(email, action)
            elif self.task_id == "urgency_detection":
                return self.dynamic_grader.grade_urgency(email, action)
            elif self.task_id == "intelligent_routing":
                return self.dynamic_grader.grade_routing(email, action)
            else:
                return 0.0, {"error": "Unknown task"}
        except Exception as e:
            # Fallback to standard graders if LLM fails
            print(f"Dynamic grader error: {e}, falling back to standard grading")
            if self.task_id == "email_priority_classification":
                return self.priority_grader.grade(email, action)
            elif self.task_id == "urgency_detection":
                return self.urgency_grader.grade(email, action)
            elif self.task_id == "intelligent_routing":
                return self.routing_grader.grade(email, action)
            else:
                from task_graders import normalize_score
                return normalize_score(0.5), {"error": "Unknown task"}

    def step(self, action: Action) -> Tuple[Observation, Reward, Dict[str, Any]]:
        """Process agent action and return new observation, reward, and info."""
        try:
            if self.episode_done:
                return self._get_observation(), Reward(
                    episode_reward=0.0,
                    cumulative_reward=self.cumulative_reward,
                    is_done=True,
                    info={"status": "episode_already_done"}
                ), {"status": "episode_already_done"}

            if self.current_email_idx >= len(self.emails):
                self.episode_done = True
                return self._get_observation(), Reward(
                    episode_reward=0.0,
                    cumulative_reward=self.cumulative_reward,
                    is_done=True,
                    info={"status": "episode_complete"}
                ), {"status": "episode_complete"}

            current_email = self.emails[self.current_email_idx]

            # Get grading using dynamic or standard grader
            try:
                base_reward, grading_details = self._get_grading(current_email, action)
            except Exception as e:
                print(f"[WARNING] Grading failed: {type(e).__name__}: {e}, using fallback reward")
                base_reward = 0.5  # Neutral fallback
                grading_details = {"error": str(e), "grading_method": "fallback"}
            
            # Apply multi-turn consequences and cascade effects
            try:
                raw_step_reward = self._apply_multi_turn_consequences(current_email, base_reward, action)
            except Exception as e:
                print(f"[WARNING] Multi-turn consequence calculation failed: {e}, using base reward")
                raw_step_reward = base_reward
            
            step_reward = max(-1.0, min(1.0, float(raw_step_reward)))

            self.step_count += 1
            self.episode_reward = step_reward
            self.cumulative_reward += step_reward
            
            # Clamp cumulative reward to valid range to prevent validation errors
            self.cumulative_reward = max(-10.0, min(10.0, self.cumulative_reward))

            # Cache this action for multi-turn reference
            try:
                self.action_cache[current_email.email_id] = {
                    "action": action.model_dump() if action else {},
                    "reward": step_reward,
                    "raw_reward": raw_step_reward,
                    "grading_details": grading_details,
                    "reward_clipped": step_reward != raw_step_reward,
                }
            except Exception as e:
                print(f"[WARNING] Failed to cache action: {e}")

            # Append to episode history
            try:
                self.episode_history.append({
                    "step": self.step_count,
                    "email_id": current_email.email_id,
                    "action": action.model_dump() if action else {},
                    "base_reward": base_reward,
                    "raw_reward": raw_step_reward,
                    "reward": step_reward,
                    "cumulative_reward": self.cumulative_reward,
                    "grading_details": grading_details,
                    "multi_turn_adjusted": raw_step_reward != base_reward,
                    "reward_clipped": step_reward != raw_step_reward,
                })
            except Exception as e:
                print(f"[WARNING] Failed to record episode history: {e}")

            self.current_email_idx += 1

            max_steps = self.config.get("max_steps", 10)
            self.episode_done = (self.step_count >= max_steps or
                                self.current_email_idx >= len(self.emails))

            next_obs = self._get_observation()

            reward_obj = Reward(
                episode_reward=step_reward,
                cumulative_reward=self.cumulative_reward,
                is_done=self.episode_done,
                breakdown={
                    "base_reward": base_reward,
                    "multi_turn_adjustment": raw_step_reward - base_reward,
                    "clip_adjustment": step_reward - raw_step_reward,
                    "final_reward": step_reward
                },
                info={
                    "grading_details": grading_details,
                    "emails_remaining": max(0, len(self.emails) - self.current_email_idx),
                    "max_steps": max_steps,
                    "multi_turn_adjusted": raw_step_reward != base_reward,
                    "reward_clipped": step_reward != raw_step_reward,
                }
            )

            info = {
                "step": self.step_count,
                "task_id": self.task_id,
                "episode_done": self.episode_done,
                "grading_details": grading_details,
                "base_reward": base_reward,
                "raw_final_reward": raw_step_reward,
                "final_reward": step_reward,
            }

            return next_obs, reward_obj, info
        
        except Exception as e:
            print(f"[ERROR] Unhandled exception in step(): {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Return safe default values on critical failure
            return (
                self._get_observation(),
                Reward(
                    episode_reward=0.0,
                    cumulative_reward=self.cumulative_reward,
                    is_done=False,
                    info={"error": str(e)}
                ),
                {"error": str(e), "step": self.step_count}
            )

    def state(self) -> State:
        """Return current environment state (read-only snapshot)."""
        current_email = None
        if self.current_email_idx < len(self.emails):
            current_email = self.emails[self.current_email_idx]

        return State(
            task_id=self.task_id,
            episode_step=self.step_count,
            emails_processed=self.current_email_idx,
            cumulative_reward=self.cumulative_reward,
            episode_complete=self.episode_done,
            current_email=current_email,
            metadata={
                "total_emails_in_episode": len(self.emails),
                "max_steps": self.config.get("max_steps", 10),
                "episode_history": self.episode_history,
                "task_config": self.config,
            }
        )

    def get_episode_summary(self) -> Dict[str, Any]:
        """Get summary statistics for completed episode"""
        try:
            status = "episode_complete" if self.episode_done else "episode_in_progress"
            step_count = max(1, self.step_count)  # Avoid division by zero
            
            return {
                "task_id": self.task_id,
                "total_steps": self.step_count,
                "final_reward": float(self.cumulative_reward),
                "average_step_reward": float(self.cumulative_reward) / step_count,
                "emails_processed": self.current_email_idx,
                "episode_history": self.episode_history if self.episode_history else [],
                "success": float(self.cumulative_reward) > 0.5 * step_count,
                "episode_complete": self.episode_done,
                "status": status,
            }
        except Exception as e:
            print(f"[WARNING] Error generating episode summary: {type(e).__name__}: {e}")
            return {
                "task_id": self.task_id,
                "total_steps": self.step_count,
                "final_reward": 0.0,
                "average_step_reward": 0.0,
                "emails_processed": self.current_email_idx,
                "episode_history": [],
                "success": False,
                "episode_complete": self.episode_done,
                "status": "error_generating_summary",
                "error": str(e),
            }


__all__ = ["EmailTriageEnv"]
