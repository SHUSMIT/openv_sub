"""
OpenEnv Email Triage Environment
A real-world email triage and response prioritization environment for AI agents.
"""

# Version
__version__ = "1.0.0"
__author__ = "OpenEnv Community"

# Import core classes for convenience
try:
    from models import (
        Email,
        Action,
        Observation,
        Reward,
        State,
        PriorityLevel,
        RoutingTeam,
        UrgencySignal,
        ActionClassifyPriority,
        ActionDetectUrgency,
        ActionRouteAndRespond,
    )
    from environment import EmailTriageEnv
    
    __all__ = [
        "Email",
        "Action",
        "Observation",
        "Reward",
        "State",
        "PriorityLevel",
        "RoutingTeam",
        "UrgencySignal",
        "ActionClassifyPriority",
        "ActionDetectUrgency",
        "ActionRouteAndRespond",
        "EmailTriageEnv",
    ]
except ImportError:
    # If imports fail, that's ok during pip install discovery
    pass


__all__ = [
    "EmailTriageEnv",
    "Email",
    "Action",
    "Observation",
    "Reward",
    "State",
    "PriorityLevel",
    "RoutingTeam",
    "UrgencySignal",
    "ActionClassifyPriority",
    "ActionDetectUrgency",
    "ActionRouteAndRespond",
]

__version__ = "1.0.0"
