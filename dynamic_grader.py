"""
LLM-based dynamic grading for more nuanced evaluation
Uses Claude/GPT to evaluate email handling quality beyond hardcoded ground truth
"""

import os
import json
from typing import Tuple, Dict, Any, Optional
from models import (
    Email, Action, PriorityLevel, RoutingTeam, UrgencySignal,
    ActionClassifyPriority, ActionDetectUrgency, ActionRouteAndRespond
)
from task_graders import normalize_score

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class DynamicLLMGrader:
    """
    LLM-based grader that provides nuanced evaluation of agent actions
    Uses Claude or OpenAI to evaluate responses in context
    Falls back to rule-based scoring if LLM unavailable
    """

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm and (ANTHROPIC_AVAILABLE or OPENAI_AVAILABLE)
        self.api_choice = None
        
        if self.use_llm:
            if os.getenv("ANTHROPIC_API_KEY"):
                self.api_choice = "anthropic"
                self.client = Anthropic()
            elif os.getenv("OPENAI_API_KEY"):
                self.api_choice = "openai"
                openai.api_key = os.getenv("OPENAI_API_KEY")
            else:
                self.use_llm = False

    def _get_llm_evaluation(self, email: Email, action: Action, action_type: str) -> Optional[Dict[str, Any]]:
        """Get LLM-based evaluation of agent action"""
        if not self.use_llm:
            return None

        try:
            if action_type == "priority_classification":
                prompt = self._build_priority_prompt(email, action)
            elif action_type == "urgency_detection":
                prompt = self._build_urgency_prompt(email, action)
            elif action_type == "routing":
                prompt = self._build_routing_prompt(email, action)
            else:
                return None

            if self.api_choice == "anthropic":
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text
            else:  # openai
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    max_tokens=500,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.choices[0].message.content

            # Parse JSON response
            try:
                json_str = result_text[result_text.find('{'):result_text.rfind('}')+1]
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                return None

        except Exception as e:
            print(f"LLM evaluation error: {e}")
            return None

    def _build_priority_prompt(self, email: Email, action: ActionClassifyPriority) -> str:
        """Build prompt for priority classification evaluation"""
        return f"""Evaluate this email priority classification decision.

EMAIL:
Subject: {email.subject}
Body: {email.body}
Sender History (contacts): {email.sender_history}
Customer Value: {email.customer_lifetime_value}
Is Reply: {email.is_reply}
Industry: {email.industry}

AGENT DECISION:
Classified as: {action.priority}
Confidence: {action.confidence}

Provide JSON evaluation:
{{
    "quality_score": 0.0-1.0 (how good is this classification),
    "reasoning": "brief explanation",
    "alternatives_considered": ["other reasonable priorities"],
    "bonus_points": 0.0-0.2 (for exceptional reasoning)
}}"""

    def _build_urgency_prompt(self, email: Email, action: ActionDetectUrgency) -> str:
        """Build prompt for urgency detection evaluation"""
        return f"""Evaluate this urgency signal detection.

EMAIL:
Subject: {email.subject}
Body: {email.body}
Sender History: {email.sender_history}
Is Reply: {email.is_reply}
Scenario: {email.scenario_context or 'normal'}

AGENT DECISION:
Detected Signals: {action.urgency_signals}
Recommend Escalation: {action.escalate}
Response Time Minutes: {action.estimated_response_time_minutes}

Provide JSON evaluation:
{{
    "signal_accuracy": 0.0-1.0,
    "response_time_appropriateness": 0.0-1.0,
    "escalation_decision_quality": 0.0-1.0,
    "overall_quality": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""

    def _build_routing_prompt(self, email: Email, action: ActionRouteAndRespond) -> str:
        """Build prompt for routing decision evaluation"""
        return f"""Evaluate this email routing and response decision.

EMAIL:
Subject: {email.subject}
Body: {email.body}
Sender History: {email.sender_history}
Customer Value: {email.customer_lifetime_value}
Industry: {email.industry}
Previous Action on Related Email: {email.previous_agent_action or 'none'}

AGENT DECISION:
Route To: {action.routing_team}
Suggested Response: {action.suggested_response}
Escalate: {action.escalate}
Follow-up Required: {action.follow_up_required}

Evaluate on:
1. Routing appropriateness (0.0-1.0)
2. Response quality and empathy (0.0-1.0)
3. Escalation decision (0.0-1.0)
4. Follow-up appropriateness (0.0-1.0)

Provide JSON:
{{
    "routing_score": 0.0-1.0,
    "response_quality": 0.0-1.0,
    "decision_quality": 0.0-1.0,
    "overall_score": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""

    def grade_priority(self, email: Email, action: Action) -> Tuple[float, Dict[str, Any]]:
        """Grade priority classification with LLM fallback"""
        if not action.classify_priority:
            return normalize_score(-0.25), {"error": "No priority action provided", "used_llm": False}

        llm_eval = self._get_llm_evaluation(email, action.classify_priority, "priority_classification")
        
        if llm_eval:
            quality = llm_eval.get("quality_score", 0.5)
            bonus = llm_eval.get("bonus_points", 0.0)
            final_score = normalize_score(min(1.0, quality + bonus))
            return final_score, {**llm_eval, "used_llm": True, "method": "dynamic_llm"}

        # Fallback to rule-based
        return self._rule_based_priority_grade(email, action.classify_priority)

    def grade_urgency(self, email: Email, action: Action) -> Tuple[float, Dict[str, Any]]:
        """Grade urgency detection with LLM fallback"""
        if not action.detect_urgency:
            return normalize_score(-0.25), {"error": "No urgency action provided", "used_llm": False}

        llm_eval = self._get_llm_evaluation(email, action.detect_urgency, "urgency_detection")
        
        if llm_eval:
            overall = llm_eval.get("overall_quality", 0.5)
            return normalize_score(overall), {**llm_eval, "used_llm": True, "method": "dynamic_llm"}

        # Fallback
        return self._rule_based_urgency_grade(email, action.detect_urgency)

    def grade_routing(self, email: Email, action: Action) -> Tuple[float, Dict[str, Any]]:
        """Grade routing decision with LLM fallback"""
        if not action.route_and_respond:
            return normalize_score(-0.25), {"error": "No routing action provided", "used_llm": False}

        llm_eval = self._get_llm_evaluation(email, action.route_and_respond, "routing")
        
        if llm_eval:
            overall = llm_eval.get("overall_score", 0.5)
            return normalize_score(overall), {**llm_eval, "used_llm": True, "method": "dynamic_llm"}

        # Fallback
        return self._rule_based_routing_grade(email, action.route_and_respond)

    def _rule_based_priority_grade(self, email: Email, action: ActionClassifyPriority) -> Tuple[float, Dict[str, Any]]:
        """Fallback rule-based priority grading using email features"""
        score = 0.0
        
        # Heuristic scoring
        if "CRITICAL" in email.subject or "CRITICAL" in email.body:
            if action.priority == PriorityLevel.CRITICAL:
                score = 1.0
            elif action.priority == PriorityLevel.HIGH:
                score = 0.5
            else:
                score = 0.0
        
        elif email.customer_lifetime_value > 0.8 and email.sender_history > 10:
            if action.priority == PriorityLevel.HIGH:
                score = 0.9
            elif action.priority in [PriorityLevel.CRITICAL, PriorityLevel.MEDIUM]:
                score = 0.5
            else:
                score = 0.2
        
        elif email.sender_history == 0:
            if action.priority == PriorityLevel.LOW:
                score = 0.8
            elif action.priority == PriorityLevel.MEDIUM:
                score = 0.5
            else:
                score = 0.2
        
        else:
            score = 0.6  # Default reasonable classification
        
        # Confidence penalty
        if action.confidence < 0.5:
            score *= 0.7
        
        return normalize_score(score), {"method": "rule_based", "used_llm": False, "score": score}

    def _rule_based_urgency_grade(self, email: Email, action: ActionDetectUrgency) -> Tuple[float, Dict[str, Any]]:
        """Fallback rule-based urgency grading"""
        score = 0.5
        
        # Check for obvious urgency signals
        has_urgency_keywords = any(kw in email.subject.upper() + email.body.upper() 
                                  for kw in ["URGENT", "CRITICAL", "EMERGENCY", "ASAP"])
        has_escalation_signals = email.is_reply and email.sender_history > 10
        
        if has_urgency_keywords or has_escalation_signals:
            if action.escalate:
                score = 0.9
            else:
                score = 0.4
        else:
            if not action.escalate:
                score = 0.8
            else:
                score = 0.5
        
        return normalize_score(score), {"method": "rule_based", "used_llm": False}

    def _rule_based_routing_grade(self, email: Email, action: ActionRouteAndRespond) -> Tuple[float, Dict[str, Any]]:
        """Fallback rule-based routing grading"""
        score = 0.6
        
        # Industry-based routing expectations
        if email.industry == "healthcare" and action.routing_team in [RoutingTeam.TECHNICAL_SUPPORT, RoutingTeam.ESCALATION]:
            score = 0.8
        elif email.industry == "finance" and action.routing_team in [RoutingTeam.ESCALATION, RoutingTeam.BILLING]:
            score = 0.8
        
        # Response quality
        if len(action.suggested_response) > 50 and len(action.suggested_response) < 500:
            score += 0.1
        
        return normalize_score(score), {"method": "rule_based", "used_llm": False, "score": score}
