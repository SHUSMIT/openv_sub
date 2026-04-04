"""
OpenEnv Email Triage Environment - Pydantic Models
Defines typed models for Observation, Action, and Reward
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority levels for email classification"""
    CRITICAL = "critical"        # 0 - Immediate attention required
    HIGH = "high"                # 1 - Urgent
    MEDIUM = "medium"            # 2 - Normal workflow
    LOW = "low"                  # 3 - Can wait


class RoutingTeam(str, Enum):
    """Routing team categories"""
    BILLING = "billing"
    TECHNICAL_SUPPORT = "technical_support"
    SALES = "sales"
    GENERAL_SUPPORT = "general_support"
    ESCALATION = "escalation"
    FEEDBACK = "feedback"


class UrgencySignal(str, Enum):
    """Urgency indicators in email content"""
    DEADLINE = "deadline"
    COMPLAINT = "complaint"
    URGENT_KEYWORD = "urgent_keyword"
    REPEAT_CONTACT = "repeat_contact"
    VIP_CUSTOMER = "vip_customer"
    SERVICE_OUTAGE = "service_outage"
    PAYMENT_ISSUE = "payment_issue"
    NONE = "none"


class Email(BaseModel):
    """Represents a single email"""
    email_id: str = Field(..., description="Unique email identifier")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    timestamp: float = Field(..., description="Unix timestamp of email arrival")

    # Contextual features
    sender_history: int = Field(default=0, description="Number of previous emails from sender (0-10)")
    is_reply: bool = Field(default=False, description="Whether this is a reply to previous email")
    attachments: int = Field(default=0, description="Number of attachments (0-5)")
    customer_lifetime_value: float = Field(default=0.0, ge=0.0, le=1.0,
                                          description="Customer value score (0.0-1.0)")
    
    # Multi-turn and context tracking
    parent_email_id: Optional[str] = Field(default=None, description="ID of email this replies to (multi-turn)")
    escalation_chain: Optional[List[str]] = Field(default=None, description="Chain of related email IDs")
    industry: str = Field(default="general", description="Industry sector (healthcare, finance, ecommerce, saas, education)")
    previous_agent_action: Optional[str] = Field(default=None, description="What agent did on previous email (for context)")
    scenario_context: Optional[str] = Field(default=None, description="Special context (e.g., 'system_outage', 'vip_escalation')")


class Observation(BaseModel):
    """Environment observation returned to agent"""
    email: Email = Field(..., description="Current email to process")
    task_id: str = Field(..., description="Current task identifier")
    step_count: int = Field(default=0, description="Number of steps in episode")
    episode_info: Dict[str, Any] = Field(default_factory=dict, description="Episode metadata")
    action_history: List[Dict[str, Any]] = Field(default_factory=list, 
                                                description="Previous actions taken on related emails in this episode")


class ActionClassifyPriority(BaseModel):
    """Action: Classify email priority"""
    priority: PriorityLevel = Field(..., description="Assigned priority level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in classification")


class ActionDetectUrgency(BaseModel):
    """Action: Detect urgency signals"""
    urgency_signals: List[UrgencySignal] = Field(default_factory=list, description="Detected urgency signals")
    escalate: bool = Field(default=False, description="Should escalate?")
    estimated_response_time_minutes: int = Field(default=24*60, ge=1, le=24*60,
                                                 description="Estimated response time target")


class ActionRouteAndRespond(BaseModel):
    """Action: Route email and compose response"""
    routing_team: RoutingTeam = Field(..., description="Team to route email to")
    suggested_response: str = Field(..., description="Suggested email response (1-500 chars)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in routing decision")
    escalate: bool = Field(default=False, description="Should escalate?")
    follow_up_required: bool = Field(default=False, description="Should schedule follow-up?")


class Action(BaseModel):
    """
    Agent action - one of three action types depending on task
    """
    task_id: str = Field(..., description="Task identifier")

    # Exactly one of these should be populated per action
    classify_priority: Optional[ActionClassifyPriority] = None
    detect_urgency: Optional[ActionDetectUrgency] = None
    route_and_respond: Optional[ActionRouteAndRespond] = None


class Reward(BaseModel):
    """Reward signal for agent"""
    episode_reward: float = Field(..., ge=-1.0, le=1.0,
                                 description="Reward for this step (-1.0 to 1.0)")
    cumulative_reward: float = Field(..., ge=-10.0, le=10.0,
                                    description="Cumulative episode reward (can exceed +-1.0)")
    breakdown: Dict[str, float] = Field(default_factory=dict,
                                       description="Reward component breakdown")
    is_done: bool = Field(default=False, description="Episode complete?")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional info")


class State(BaseModel):
    """Current environment state"""
    task_id: str
    episode_step: int
    emails_processed: int
    cumulative_reward: float
    episode_complete: bool
    current_email: Optional[Email]
    metadata: Dict[str, Any]
