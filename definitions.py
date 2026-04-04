"""
Task definitions with expanded realistic email datasets (150+ emails)
Covers: Healthcare, Finance, E-commerce, SaaS, Education, and edge cases
"""

import random
from typing import List, Dict, Any
from models import Email

try:
    from expanded_emails import get_all_emails, get_critical_emails, get_emails_by_industry
except ModuleNotFoundError:
    try:
        from expanded_emails import get_all_emails, get_critical_emails, get_emails_by_industry
    except ModuleNotFoundError:
        # Fallback keeps the environment runnable if deployment packaging misses expanded_emails.py.
        _FALLBACK_INDUSTRIES = ["healthcare", "finance", "ecommerce", "saas", "education"]
        _FALLBACK_CONTEXTS = [
            "mixed_priority",
            "sarcastic_complaint",
            "vague_complaint",
            "cascade_incident",
            "escalation_required",
            "vip_opportunity",
            "system_outage",
            "deadline_risk",
            "enterprise_partnership",
            None,
        ]
        _FALLBACK_EMAIL_CACHE: List[Email] = []

        def _build_fallback_emails() -> List[Email]:
            emails: List[Email] = []
            previous_by_industry: Dict[str, str] = {}
            base_timestamp = 1712200000.0

            for idx in range(30):
                industry = _FALLBACK_INDUSTRIES[idx % len(_FALLBACK_INDUSTRIES)]
                scenario_context = _FALLBACK_CONTEXTS[idx % len(_FALLBACK_CONTEXTS)]
                is_critical = (idx % 6 == 0)
                is_urgent = (idx % 5 == 0 and not is_critical)

                subject_prefix = "CRITICAL: " if is_critical else "URGENT: " if is_urgent else ""
                email_stub = (
                    "ambig"
                    if scenario_context in {"mixed_priority", "sarcastic_complaint", "vague_complaint"} and idx % 2 == 0
                    else "fallback"
                )
                email_id = f"{email_stub}_{industry}_{idx:03d}"

                parent_email_id = previous_by_industry.get(industry) if idx % 4 == 0 else None
                escalation_chain = [parent_email_id] if parent_email_id else None

                emails.append(
                    Email(
                        email_id=email_id,
                        sender=f"customer{idx}@{industry}.example.com",
                        subject=f"{subject_prefix}{industry.title()} support issue #{idx}",
                        body=(
                            f"I need help with a {industry} workflow issue. "
                            f"Scenario: {scenario_context or 'general_request'}."
                        ),
                        timestamp=base_timestamp + float(idx * 60),
                        sender_history=idx % 5,
                        is_reply=parent_email_id is not None,
                        attachments=idx % 3,
                        customer_lifetime_value=min(1.0, 0.25 + (idx % 8) * 0.1),
                        parent_email_id=parent_email_id,
                        escalation_chain=escalation_chain,
                        industry=industry,
                        previous_agent_action="follow_up_requested" if parent_email_id else None,
                        scenario_context=scenario_context,
                    )
                )
                previous_by_industry[industry] = email_id

            return emails

        def _get_cached_fallback_emails() -> List[Email]:
            if not _FALLBACK_EMAIL_CACHE:
                _FALLBACK_EMAIL_CACHE.extend(_build_fallback_emails())
            return _FALLBACK_EMAIL_CACHE

        def get_all_emails() -> List[Email]:
            return list(_get_cached_fallback_emails())

        def get_critical_emails() -> List[Email]:
            return [
                email
                for email in _get_cached_fallback_emails()
                if "CRITICAL" in email.subject or email.scenario_context in {"system_outage", "cascade_incident"}
            ]

        def get_emails_by_industry(industry: str) -> List[Email]:
            return [email for email in _get_cached_fallback_emails() if email.industry == industry]


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
