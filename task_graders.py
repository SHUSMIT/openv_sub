"""
Task graders - evaluate agent performance with deterministic scoring
"""

from typing import Dict, Tuple, List, Any
from models import (
    Email, Action, PriorityLevel, RoutingTeam, UrgencySignal,
    ActionClassifyPriority, ActionDetectUrgency, ActionRouteAndRespond
)


class EmailPriorityGrader:
    """
    Grader for Task 1: Email Priority Classification
    """

    def __init__(self):
        self.priority_ground_truth = self._build_ground_truth()

    def _build_ground_truth(self) -> Dict[str, PriorityLevel]:
        return {
            "billing_001": PriorityLevel.HIGH,
            "tech_001": PriorityLevel.CRITICAL,
            "general_001": PriorityLevel.LOW,
            "escalation_001": PriorityLevel.CRITICAL,
            "payment_001": PriorityLevel.HIGH,
            "feedback_001": PriorityLevel.LOW,
            "outage_001": PriorityLevel.CRITICAL,
            "complaint_001": PriorityLevel.HIGH,
            "info_001": PriorityLevel.LOW,
            "dataexport_001": PriorityLevel.MEDIUM,
        }

    def grade(self, email: Email, action: Action) -> Tuple[float, Dict[str, Any]]:
        if not action.classify_priority:
            return -0.25, {"error": "No classification action provided"}

        ground_truth = self.priority_ground_truth.get(email.email_id, PriorityLevel.MEDIUM)
        predicted = action.classify_priority.priority

        priority_order = [
            PriorityLevel.CRITICAL,
            PriorityLevel.HIGH,
            PriorityLevel.MEDIUM,
            PriorityLevel.LOW,
        ]

        try:
            truth_idx = priority_order.index(ground_truth)
            pred_idx = priority_order.index(predicted)
            distance = abs(truth_idx - pred_idx)

            if distance == 0:
                reward = 1.0
            elif distance == 1:
                reward = 0.5
            else:
                reward = 0.0

            reward = max(-0.25, reward - (1 - action.classify_priority.confidence) * 0.2)

            return reward, {
                "ground_truth": ground_truth,
                "predicted": predicted,
                "distance": distance,
                "confidence": action.classify_priority.confidence,
            }
        except (ValueError, AttributeError) as e:
            return -0.25, {"error": str(e)}


class UrgencyDetectionGrader:
    """
    Grader for Task 2: Urgency & Escalation Detection
    """

    def __init__(self):
        self.urgency_ground_truth = self._build_ground_truth()

    def _build_ground_truth(self) -> Dict[str, List[UrgencySignal]]:
        return {
            "billing_001": [UrgencySignal.COMPLAINT, UrgencySignal.PAYMENT_ISSUE],
            "tech_001": [UrgencySignal.SERVICE_OUTAGE, UrgencySignal.VIP_CUSTOMER],
            "general_001": [UrgencySignal.NONE],
            "escalation_001": [
                UrgencySignal.REPEAT_CONTACT, UrgencySignal.DEADLINE,
                UrgencySignal.COMPLAINT
            ],
            "payment_001": [UrgencySignal.PAYMENT_ISSUE],
            "feedback_001": [UrgencySignal.NONE],
            "outage_001": [UrgencySignal.SERVICE_OUTAGE, UrgencySignal.VIP_CUSTOMER],
            "complaint_001": [UrgencySignal.COMPLAINT, UrgencySignal.VIP_CUSTOMER],
            "info_001": [UrgencySignal.NONE],
            "dataexport_001": [UrgencySignal.DEADLINE],
        }

    def grade(self, email: Email, action: Action) -> Tuple[float, Dict[str, Any]]:
        if not action.detect_urgency:
            return -0.25, {"error": "No urgency detection action provided"}

        ground_truth_signals = self.urgency_ground_truth.get(email.email_id, [UrgencySignal.NONE])
        predicted_signals = action.detect_urgency.urgency_signals or [UrgencySignal.NONE]

        reward = 0.0
        details = {
            "ground_truth_signals": ground_truth_signals,
            "predicted_signals": predicted_signals,
        }

        truth_set = set(ground_truth_signals)
        predicted_set = set(predicted_signals)

        correct_detections = len(truth_set & predicted_set)
        missed_signals = len(truth_set - predicted_set)
        false_positives = len(predicted_set - truth_set)

        reward += min(1.0, correct_detections * 0.3)
        reward -= missed_signals * 0.2
        reward -= false_positives * 0.1

        should_escalate = len(ground_truth_signals) >= 2 or UrgencySignal.DEADLINE in ground_truth_signals
        if action.detect_urgency.escalate == should_escalate:
            reward += 0.3
        else:
            reward -= 0.2

        if len(ground_truth_signals) == 0:
            ideal_response_minutes = 24 * 60
        elif UrgencySignal.SERVICE_OUTAGE in ground_truth_signals:
            ideal_response_minutes = 15
        elif UrgencySignal.DEADLINE in ground_truth_signals:
            ideal_response_minutes = 60
        elif len(ground_truth_signals) >= 2:
            ideal_response_minutes = 120
        else:
            ideal_response_minutes = 24 * 60

        time_diff = abs(action.detect_urgency.estimated_response_time_minutes - ideal_response_minutes)
        if time_diff <= 60:
            reward += 0.2
        elif time_diff <= 240:
            reward += 0.1
        else:
            reward -= 0.1

        details["correct_detections"] = correct_detections
        details["missed_signals"] = missed_signals
        details["false_positives"] = false_positives
        details["escalation_correct"] = action.detect_urgency.escalate == should_escalate

        return max(-0.5, min(1.0, reward)), details


class IntelligentRoutingGrader:
    """
    Grader for Task 3: Intelligent Email Routing & Response
    """

    def __init__(self):
        self.routing_ground_truth = self._build_ground_truth()

    def _build_ground_truth(self) -> Dict[str, Dict[str, Any]]:
        return {
            "billing_001": {
                "team": RoutingTeam.BILLING,
                "should_escalate": False,
                "response_min_length": 50,
                "response_max_length": 300,
                "should_followup": True,
            },
            "tech_001": {
                "team": RoutingTeam.ESCALATION,
                "should_escalate": True,
                "response_min_length": 100,
                "response_max_length": 250,
                "should_followup": True,
            },
            "general_001": {
                "team": RoutingTeam.SALES,
                "should_escalate": False,
                "response_min_length": 80,
                "response_max_length": 300,
                "should_followup": False,
            },
            "escalation_001": {
                "team": RoutingTeam.ESCALATION,
                "should_escalate": True,
                "response_min_length": 100,
                "response_max_length": 200,
                "should_followup": False,
            },
            "payment_001": {
                "team": RoutingTeam.BILLING,
                "should_escalate": True,
                "response_min_length": 80,
                "response_max_length": 200,
                "should_followup": True,
            },
            "feedback_001": {
                "team": RoutingTeam.FEEDBACK,
                "should_escalate": False,
                "response_min_length": 50,
                "response_max_length": 200,
                "should_followup": False,
            },
            "outage_001": {
                "team": RoutingTeam.ESCALATION,
                "should_escalate": True,
                "response_min_length": 100,
                "response_max_length": 250,
                "should_followup": True,
            },
            "complaint_001": {
                "team": RoutingTeam.ESCALATION,
                "should_escalate": True,
                "response_min_length": 100,
                "response_max_length": 300,
                "should_followup": True,
            },
            "info_001": {
                "team": RoutingTeam.GENERAL_SUPPORT,
                "should_escalate": False,
                "response_min_length": 100,
                "response_max_length": 300,
                "should_followup": False,
            },
            "dataexport_001": {
                "team": RoutingTeam.TECHNICAL_SUPPORT,
                "should_escalate": False,
                "response_min_length": 80,
                "response_max_length": 250,
                "should_followup": True,
            },
        }

    def grade(self, email: Email, action: Action) -> Tuple[float, Dict[str, Any]]:
        if not action.route_and_respond:
            return -0.5, {"error": "No routing action provided"}

        ground_truth = self.routing_ground_truth.get(
            email.email_id, {
                "team": RoutingTeam.GENERAL_SUPPORT,
                "should_escalate": False,
                "response_min_length": 50,
                "response_max_length": 300,
                "should_followup": False,
            }
        )

        reward = 0.0
        details = {}

        # 1. Routing team correctness (0.5 points)
        if action.route_and_respond.routing_team == ground_truth["team"]:
            reward += 0.5
            details["routing_correct"] = True
        else:
            reward -= 0.3
            details["routing_correct"] = False

        # 2. Response quality (0.3 points)
        response = action.route_and_respond.suggested_response
        response_len = len(response)
        min_len = ground_truth["response_min_length"]
        max_len = ground_truth["response_max_length"]

        if min_len <= response_len <= max_len:
            reward += 0.3
            details["response_length_ok"] = True
        elif min_len <= response_len <= max_len * 1.2 or min_len * 0.8 <= response_len <= max_len:
            reward += 0.15
            details["response_length_ok"] = "partial"
        else:
            reward -= 0.1
            details["response_length_ok"] = False

        # 3. Escalation decision (0.1 points)
        if action.route_and_respond.escalate == ground_truth["should_escalate"]:
            reward += 0.1
            details["escalation_correct"] = True
        else:
            reward -= 0.15
            details["escalation_correct"] = False

        # 4. Follow-up detection (0.05 points)
        if action.route_and_respond.follow_up_required == ground_truth["should_followup"]:
            reward += 0.05
            details["followup_correct"] = True
        else:
            reward -= 0.05
            details["followup_correct"] = False

        # 5. Confidence scoring
        confidence = action.route_and_respond.confidence
        if confidence < 0.5:
            reward -= 0.1

        details["response_length"] = response_len
        details["ground_truth"] = ground_truth
        details["final_score"] = max(-0.5, min(1.0, reward))

        return max(-0.5, min(1.0, reward)), details
