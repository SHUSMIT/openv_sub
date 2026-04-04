"""
Task definitions with expanded realistic email datasets (150+ emails)
Covers: Healthcare, Finance, E-commerce, SaaS, Education, and edge cases
"""

import random
from typing import List, Dict, Any
from env.models import Email
from env.tasks.expanded_emails import get_all_emails, get_critical_emails, get_emails_by_industry


def get_training_emails() -> List[Email]:
    """Return all 150+ emails from expanded dataset"""
    return get_all_emails()


# Updated task configurations with larger episode sizes to showcase diversity
TASK_CONFIGS: Dict[str, Dict[str, Any]] = {
    "email_priority_classification": {
        "name": "Email Priority Classification",
        "description": "Classify emails into 4 priority levels",
        "difficulty": "easy",
        "emails_per_episode": 15,
        "max_steps": 20,
    },
    "urgency_detection": {
        "name": "Urgency & Escalation Detection",
        "description": "Detect urgency signals and recommend escalation timing",
        "difficulty": "medium",
        "emails_per_episode": 20,
        "max_steps": 30,
    },
    "intelligent_routing": {
        "name": "Intelligent Email Routing & Response",
        "description": "Route to correct team and compose appropriate response",
        "difficulty": "hard",
        "emails_per_episode": 25,
        "max_steps": 40,
    },
}


def get_task_config(task_id: str) -> Dict[str, Any]:
    """Get configuration for a task"""
    return TASK_CONFIGS.get(task_id, {})


def get_emails_for_task(task_id: str, seed: int = None) -> List[Email]:
    """Get appropriate email set for task with industry and complexity diversity"""
    if seed is not None:
        random.seed(seed)

    all_emails = get_training_emails()
    config = get_task_config(task_id)
    num_emails = config.get("emails_per_episode", 5)

    if task_id == "email_priority_classification":
        # Mix clear priorities, edge cases, and ambiguous scenarios
        critical = get_critical_emails()[:5]
        routine = [e for e in all_emails if "CRITICAL" not in e.subject and 
                   "URGENT" not in e.subject and e.customer_lifetime_value < 0.5][:5]
        ambiguous = [e for e in all_emails if e.scenario_context in
                     ["mixed_priority", "sarcastic_complaint", "vague_complaint"]][:3]
        mix = critical + routine + ambiguous
        seen = set(e.email_id for e in mix)
        unique = [e for e in mix if e.email_id not in seen or not seen.remove(e.email_id)]
        return unique[:num_emails] if unique else random.sample(all_emails, min(num_emails, len(all_emails)))

    elif task_id == "urgency_detection":
        # Include multi-turn, escalations, and cascading
        critical = get_critical_emails()[:8]
        multiturn = [e for e in all_emails if e.parent_email_id is not None][:8]
        cascade = [e for e in all_emails if e.scenario_context and
                   ("cascade" in e.scenario_context.lower() or 
                    "escalation" in e.scenario_context.lower())][:4]
        mix = critical + multiturn + cascade
        seen = set()
        unique = [e for e in mix if not (e.email_id in seen or seen.add(e.email_id))]
        return unique[:num_emails] if unique else random.sample(all_emails, min(num_emails, len(all_emails)))

    elif task_id == "intelligent_routing":
        # Full diversity: industries, critical, multi-turn, edges
        routing_mix = []
        for industry in ["healthcare", "finance", "ecommerce", "saas", "education"]:
            routing_mix.extend(get_emails_by_industry(industry)[:4])
        routing_mix.extend(get_critical_emails()[:3])
        routing_mix.extend([e for e in all_emails if e.parent_email_id is not None][:3])
        routing_mix.extend([e for e in all_emails if "ambig" in e.email_id][:3])
        seen = set()
        unique = [e for e in routing_mix if not (e.email_id in seen or seen.add(e.email_id))]
        return unique[:num_emails] if unique else random.sample(all_emails, min(num_emails, len(all_emails)))

    return random.sample(all_emails, min(num_emails, len(all_emails)))
