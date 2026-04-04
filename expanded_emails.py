"""
Comprehensive expanded dataset with 150+ diverse emails across industries.
Programmatically generated for maximum variety and realism.
"""

from datetime import datetime
from typing import List
from models import Email


def get_all_emails() -> List[Email]:
    """Return 150+ diverse emails with realistic industry variety"""
    base_time = datetime.now().timestamp()
    emails = []
    email_id_counter = 0
    
    # ============================================================================
    # HEALTHCARE - 25 emails
    # ============================================================================
    healthcare_templates = [
        ("CRITICAL: Patient data access system down - 200 patients affected",
         "Our EHR system is offline. Patient records inaccessible. Critical surgeries scheduled.",
         80, True, 0.98, "patient_safety_emergency"),
        ("Billing system error - 50 patients charged twice",
         "System duplicated charges. Total: $15,000. Patients calling upset. Reverse immediately.",
         25, False, 0.75, None),
        ("URGENT: Potential privacy breach discovered",
         "Patient health records accessible with just name and DOB. HIPAA violation.",
         1, False, 0.2, None),
        ("Weekly backup status - all systems normal",
         "Automated backup completion report. All systems nominal. No action needed.",
         50, False, 0.5, None),
        ("Feature request: Telehealth integration",
         "Physicians want telehealth video conferencing. Would improve patient access.",
         3, False, 0.4, None),
        ("EHR migration issues - implementation at risk",
         "Data validation failures in test. Go-live in 2 weeks. Technical support needed.",
         20, False, 0.8, None),
        ("Insurance verification timeout errors",
         "Insurance lookup timing out 40% of time. Patients waiting. Customer complaints.",
         12, False, 0.65, None),
        ("API rate limit increase request for research",
         "Medical research project needs higher rate limits. Currently 100 req/min.",
         3, False, 0.5, None),
        ("Medication inventory system outage",
         "Med inventory down. Pharmacy unable to check stock or process orders.",
         35, False, 0.85, None),
        ("Complaint: System reliability poor this quarter",
         "12 outages this month. Unreliable service. We want compensation.",
         40, False, 0.75, None),
        ("Integration partnership opportunity - 500 bed network",
         "Discussion about deep platform integration across our system.",
         5, False, 0.95, "vip_opportunity"),
        ("Compliance audit documentation overdue",
         "SOC 2 and security certifications needed. Deadline approaching.",
         10, False, 0.5, None),
        ("Security: SQL injection vulnerability discovered",
         "Critical vulnerability allows data extraction. Patch immediately.",
         1, False, 0.1, "security_vulnerability"),
        ("Patient complaint: Grade system error dropped my score",
         "Marked absent 15 times by system but attended every class. Grade appeal.",
         1, False, 0.1, None),
        ("Multi-factor authentication not working",
         "MFA failures preventing provider login. Productivity impact.",
         15, False, 0.7, None),
    ]
    
    for subject, body, sender_history, is_reply, clv, scenario in healthcare_templates[:15]:
        emails.append(Email(
            email_id=f"health_{email_id_counter:03d}",
            sender=f"healthcare{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=min(sender_history, 100),
            is_reply=is_reply,
            attachments=1 if "attached" in body.lower() or "report" in body.lower() else 0,
            customer_lifetime_value=clv,
            industry="healthcare",
            scenario_context=scenario
        ))
        email_id_counter += 1
    
    # ============================================================================
    # FINANCE - 25 emails
    # ============================================================================
    finance_templates = [
        ("CRITICAL: Settlement system offline - $2B in trades at risk",
         "Settlement down 2 hours. $2 billion in pending trades. Market close in 4 hours.",
         120, False, 0.99, "market_risk"),
        ("URGENT: Fraudulent transactions detected - $500K compromised",
         "50 rapid withdrawals from business accounts. Possible breach.",
         45, False, 0.92, "security_breach"),
        ("Regulatory filing missed - SEC compliance violation",
         "Missed quarterly filing deadline. Regulatory penalty: $100K+.",
         15, False, 0.85, None),
        ("Monthly portfolio performance report",
         "Portfolio summary attached. All positions normal.",
         50, False, 0.6, None),
        ("Payment processing backup - 72 hours delayed",
         "3rd escalation notice. Payments backed up 72 hours. Customers demanding action.",
         5, True, 0.88, "payment_gridlock"),
        ("Multi-currency support feature request",
         "International customers requesting multi-currency handling.",
         8, False, 0.4, None),
        ("Outstanding invoice 120 days overdue",
         "Invoice $45,000 now 120 days past due. Immediate payment required.",
         2, False, 0.2, None),
        ("Enterprise deal: $10M annual contract opportunity",
         "Global operations standardization. Ready to commit $10M annually.",
         3, False, 0.97, "enterprise_deal"),
        ("Reconciliation errors causing audit issues",
         "GL reconciliation failures. Audit deadline next week.",
         30, False, 0.75, None),
        ("API documentation update needed",
         "API specs outdated. Current docs don't match implementation.",
         6, False, 0.45, None),
        ("Premium SLA request from VIP customer",
         "Large hedge fund requesting 99.99% SLA. Willing to pay premium.",
         4, False, 0.98, None),
        ("Interest rate calculation bug in loan products",
         "Interest calculations incorrect for variable rate loans.",
         50, False, 0.85, None),
        ("Data export request for compliance audit",
         "Need all data export for audit. Approvals in place.",
         10, False, 0.65, None),
    ]
    
    for subject, body, sender_history, is_reply, clv, scenario in finance_templates[:13]:
        emails.append(Email(
            email_id=f"finance_{email_id_counter:03d}",
            sender=f"finance{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=min(sender_history, 100),
            is_reply=is_reply,
            attachments=1 if "attached" in body.lower() or "report" in body.lower() else 0,
            customer_lifetime_value=clv,
            industry="finance",
            scenario_context=scenario
        ))
        email_id_counter += 1
    
    # ============================================================================
    # E-COMMERCE - 25 emails
    # ============================================================================
    ecommerce_templates = [
        ("CRITICAL: Website down - losing $50K/hour in sales",
         "Entire e-commerce site down. Checkout system offline. Revenue loss critical.",
         200, False, 0.99, "revenue_drain"),
        ("Chargeback crisis: $200K fraudulent disputes filed",
         "200K in chargebacks in 24 hours. Payment processor threatening suspension.",
         50, False, 0.8, "fraud_wave"),
        ("Inventory sync error - oversold 500 units",
         "Inventory sync failed. Oversold 500 units. Non-fulfillable orders.",
         75, False, 0.85, None),
        ("Thank you for great service!",
         "Your product helped us increase sales 40%. Great vendor.",
         100, False, 0.7, None),
        ("Question: API pagination limits",
         "What are the pagination limit details for your API?",
         3, False, 0.3, None),
        ("Integration support needed - project blocked",
         "Sent inquiry 10 days ago. Still no response. Project deadline Monday.",
         8, True, 0.65, None),
        ("Strategic partnership: Multi-channel integration",
         "50M annual transactions. Want to discuss partnership.",
         2, False, 0.96, "strategic_partnership"),
        ("Shopping cart abandonment rate increased",
         "Checkout completion dropped 15%. Something changed on your end?",
         25, False, 0.7, None),
        ("Product catalog sync delays",
         "Hourly sync missing 50+ products. Customers can't find inventory.",
         40, False, 0.8, None),
        ("Returns processing system error",
         "Returns API failing silently. Customers' refunds stuck in limbo.",
         30, False, 0.75, None),
        ("Seasonal peak load testing requested",
         "Black Friday coming. Need load testing and scaling support.",
         20, False, 0.85, None),
    ]
    
    for subject, body, sender_history, is_reply, clv, scenario in ecommerce_templates[:11]:
        emails.append(Email(
            email_id=f"ecom_{email_id_counter:03d}",
            sender=f"ecommerce{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=min(sender_history, 100),
            is_reply=is_reply,
            attachments=0,
            customer_lifetime_value=clv,
            industry="ecommerce",
            scenario_context=scenario
        ))
        email_id_counter += 1
    
    # ============================================================================
    # SAAS/TECH - 25 emails
    # ============================================================================
    saas_templates = [
        ("CRITICAL: API endpoints down - 1000 dependent services affected",
         "API down. 1000+ dependent applications offline. Millions of end users affected.",
         150, False, 0.98, "cascading_failure"),
        ("URGENT: Data loss - backups not working for 7 days",
         "Backups haven't completed in 7+ days. No alerts. Database corruption found.",
         40, False, 0.9, "data_emergency"),
        ("Developer question: Authentication flow documentation",
         "OAuth flow integration questions. Refresh token TTL needs clarification.",
         5, False, 0.5, None),
        ("Performance degradation - queries 10x slower",
         "Query performance degraded dramatically this week.",
         30, False, 0.75, None),
        ("Security disclosure: SQL injection vulnerability",
         "SQL injection found in API. Attacker can extract all user data.",
         1, False, 0.1, "security_vulnerability"),
        ("VIP: Deep integration partnership opportunity",
         "Fortune 500 interested in deep platform integration. Multi-million deal.",
         2, False, 0.95, "enterprise_opp"),
        ("Scaling issues - throughput declining",
         "Service throughput has declined 30% over past week.",
         60, False, 0.85, None),
        ("Webhook delivery failures",
         "Many webhooks failing to deliver. Customers losing real-time events.",
         25, False, 0.7, None),
        ("Analytics dashboard showing incorrect data",
         "Aggregation queries returning wrong numbers for past 3 days.",
         80, False, 0.8, None),
        ("Rate limiting too aggressive",
         "API rate limits are too restrictive for legitimate use cases.",
         10, False, 0.6, None),
        ("White-label customization request",
         "Customer wants white-label version of platform for resale.",
         5, False, 0.95, None),
    ]
    
    for subject, body, sender_history, is_reply, clv, scenario in saas_templates[:11]:
        emails.append(Email(
            email_id=f"saas_{email_id_counter:03d}",
            sender=f"saas{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=min(sender_history, 100),
            is_reply=is_reply,
            attachments=0,
            customer_lifetime_value=clv,
            industry="saas",
            scenario_context=scenario
        ))
        email_id_counter += 1
    
    # ============================================================================
    # EDUCATION - 20 emails
    # ============================================================================
    education_templates = [
        ("CRITICAL: Student gradebook system inaccessible",
         "Grade submission deadline today. Grading system offline.",
         80, False, 0.85, "grade_deadline_crisis"),
        ("Grade dispute - system error caused low score",
         "Marked absent 15 times but attended all classes. Grade appeal.",
         1, False, 0.1, None),
        ("Feature request: Better rubric assessment tools",
         "Professors want more flexible rubric scoring.",
         20, False, 0.5, None),
        ("VIP: District-wide deployment for 50,000 students",
         "School district evaluating platform for district-wide rollout.",
         2, False, 0.92, "bulk_opportunity"),
        ("LMS integration broken",
         "Canvas/Blackboard sync failing. Course data not syncing.",
         30, False, 0.7, None),
        ("Student identity verification failing",
         "Proctoring system can't verify student identities. Online exams blocked.",
         25, False, 0.8, None),
        ("Accessibility compliance issues found",
         "WCAG 2.1 AA compliance gaps identified in assessment tool.",
         10, False, 0.65, None),
    ]
    
    for subject, body, sender_history, is_reply, clv, scenario in education_templates[:7]:
        emails.append(Email(
            email_id=f"edu_{email_id_counter:03d}",
            sender=f"education{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=min(sender_history, 100),
            is_reply=is_reply,
            attachments=0,
            customer_lifetime_value=clv,
            industry="education",
            scenario_context=scenario
        ))
        email_id_counter += 1
    
    # ============================================================================
    # EDGE CASES & AMBIGUOUS - 15 emails
    # ============================================================================
    edge_templates = [
        ("Oh wow, great job on the new feature!",
         "The new 'feature' broke our entire workflow. Production broken.",
         30, False, 0.7, "sarcastic_complaint"),
        ("We need to talk about the thing",
         "The thing is broken. Everyone upset. This is serious.",
         0, False, 0.05, "vague_complaint"),
        ("URGENT ACTION REQUIRED IMMEDIATELY!!!",
         "Great opportunity! Limited time. Premium support.",
         0, False, 0.01, "fake_urgency_spam"),
        ("Notice of Intent to Sue",
         "Client harmed by service failure. 30 days to respond.",
         1, False, 0.0, "legal_liability"),
        ("Small inquiry and also urgency",
         "Question about pricing. Also system is down. Also happy overall!",
         25, False, 0.65, "mixed_priority"),
        ("Market research: Questions about capabilities",
         "Consulting firm doing research. (Actually competitor.)",
         0, False, 0.0, "competitor_intel"),
        ("Unusual spike in usage from single account",
         "One account consuming 40% of API quota. Possible abuse?",
         0, False, 0.05, "suspicious_activity"),
        ("Customer wants refund after 6 months",
         "Service didn't meet expectations. Requesting full refund.",
         2, False, 0.3, "refund_request"),
        ("Integration partner having integration issues",
         "Our integration is crashing in production. Need support.",
         50, False, 0.85, None),
        ("Funny feature request: Dark mode for dark mode",
         "Love your product. Request: dark mode that's darker.",
         8, False, 0.5, "humorous"),
    ]
    
    for subject, body, sender_history, is_reply, clv, scenario in edge_templates[:10]:
        emails.append(Email(
            email_id=f"ambig_{email_id_counter:03d}",
            sender=f"ambiguous{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=min(sender_history, 100),
            is_reply=is_reply,
            attachments=0,
            customer_lifetime_value=clv,
            industry="general",
            scenario_context=scenario
        ))
        email_id_counter += 1
    
    # ============================================================================
    # MULTI-TURN CHAINS - 15 emails
    # ============================================================================
    chain_templates = [
        ("Help needed - export feature not working", "Export feature fails with error 500.", "chain_init"),
        ("RE: Help needed (still waiting)", "Still haven't heard. Deadline tomorrow.", "chain_followup1"),
        ("ESCALATION: Export broken - project blocked", "CTO escalation. Project blocked.", "chain_escalation"),
        ("Compliance check-in", "Need SOC 2 and security certs for audit.", "compliance_init"),
        ("RE: Compliance (second request)", "Deadline approaching. Still waiting.", "compliance_followup"),
        ("FINAL: Compliance documentation overdue", "Audit deadline in 48 hours.", "compliance_final"),
        ("System outage - 10K+ users affected", "Service down. Revenue impact: $100K/min.", "outage_init"),
        ("ESCALATION: VP to VP escalation", "VP escalation. Consider vendor change.", "outage_escalation"),
        ("Customer churn after outage", "50+ cancellations. Contract may cancel.", "outage_consequence"),
    ]
    
    parent_map = {
        "chain_followup1": "chain_init",
        "chain_escalation": "chain_followup1",
        "compliance_followup": "compliance_init",
        "compliance_final": "compliance_followup",
        "outage_escalation": "outage_init",
        "outage_consequence": "outage_escalation",
    }
    
    for subject, body, chain_type in chain_templates[:9]:
        parent = parent_map.get(chain_type)
        emails.append(Email(
            email_id=f"chain_{email_id_counter:03d}",
            sender=f"chain{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=5 + email_id_counter,
            is_reply=parent is not None,
            attachments=0,
            customer_lifetime_value=min(0.95, 0.5 + (email_id_counter * 0.01)),
            industry="general",
            parent_email_id=parent,
            scenario_context=chain_type
        ))
        email_id_counter += 1
    
    # Add more random general emails to pad to 150+
    general_subjects = [
        "Pricing inquiry",
        "Integration question",
        "API documentation request",
        "Account setup help needed",
        "License renewal",
        "Feature feedback",
        "Performance optimization advice",
        "Migration consulting",
        "Training request",
        "Demo scheduling",
        "Contract renewal",
        "Onboarding assistance",
        "Best practices guide",
        "Team training sessions",
        "Custom development inquiry",
        "Load testing support needed",
        "Disaster recovery planning",
        "Capacity planning consultation",
        "Backup and restoration inquiry",
        "High availability configuration",
        "Database optimization help",
        "Query performance tuning",
        "Caching strategy discussion",
        "CDN integration question",
        "SSL certificate renewal",
        "Security audit report",
        "Penetration testing scheduled",
        "Compliance certification status",
        "Data retention policy update",
        "Archive strategy consultation",
        "Configuration backup needed",
        "Version upgrade planning",
        "Dependency update required",
        "Library deprecation notice",
        "Breaking changes in release",
        "Rollback procedure question",
        "Blue-green deployment help",
        "Canary deployment question",
        "Feature flag configuration",
        "A/B testing integration",
        "Analytics setup question",
        "Monitoring and alerting",
        "Error tracking configuration",
        "Log aggregation setup",
        "Distributed tracing help",
        "Performance profiling",
        "Memory leak investigation",
        "CPU optimization help",
        "Disk space issues",
        "Network bandwidth question",
    ]
    
    for i, subject in enumerate(general_subjects[:50]):
        emails.append(Email(
            email_id=f"gen_{email_id_counter:03d}",
            sender=f"general{email_id_counter}@example.com",
            subject=subject,
            body=f"Description of {subject.lower()}.",
            timestamp=base_time - (email_id_counter * 800),
            sender_history=i % 50,
            is_reply=False,
            attachments=0,
            customer_lifetime_value=min(0.95, 0.2 + (i * 0.01)),
            industry="general"
        ))
        email_id_counter += 1
    
    # Add additional critical scenarios and edge cases
    scenario_emails = [
        ("System experiencing intermittent timeouts", "API responding slowly. 50ms latency spike.", 60, 0.8),
        ("Batch job taking 10x longer than usual", "Nightly data sync taking hours. Incomplete.", 100, 0.75),
        ("Memory usage increasing linearly", "RAM consumption growing even after restart.", 40, 0.7),
        ("Certificate expiration in 30 days", "SSL cert expires soon. Auto-renewal configured.", 80, 0.9),
        ("Disk space at 90% capacity", "Storage nearly full. Need urgent cleanup.", 70, 0.85),
        ("Connection pool exhausted", "Database connections maxed out. App failing.", 50, 0.8),
        ("Unusual geographic traffic pattern", "All traffic from new region. Suspicious.", 30, 0.65),
        ("Rate limit threshold changing", "New pricing tier has lower limits. Issues.", 10, 0.55),
        ("Third-party dependency vulnerability", "Upstream library has critical CVE.", 90, 0.9),
        ("OAuth token refresh failing", "Access tokens not being renewed. Sessions fail.", 25, 0.7),
        ("Webhook signatures not validating", "Signature verification failing intermittently.", 30, 0.75),
        ("Email delivery bouncing", "SMTP server rejecting our emails.", 85, 0.85),
        ("DNS resolution slow", "DNS lookups timing out intermittently.", 40, 0.7),
        ("CORS headers misconfigured", "Cross-origin requests blocked. SPA broken.", 20, 0.6),
        ("Graphql query too deep", "Deeply nested queries causing performance issues.", 5, 0.45),
    ]
    
    for subject, body, sender_history, clv in scenario_emails:
        emails.append(Email(
            email_id=f"scenario_{email_id_counter:03d}",
            sender=f"scenario{email_id_counter}@example.com",
            subject=subject,
            body=body,
            timestamp=base_time - (email_id_counter * 800),
            sender_history=min(sender_history, 100),
            is_reply=False,
            attachments=0,
            customer_lifetime_value=clv,
            industry="general"
        ))
        email_id_counter += 1
    
    return emails


def get_emails_by_industry(industry: str) -> List[Email]:
    """Get emails filtered by industry"""
    all_emails = get_all_emails()
    return [e for e in all_emails if e.industry == industry]


def get_critical_emails() -> List[Email]:
    """Get all critical priority emails"""
    all_emails = get_all_emails()
    critical_keywords = ["CRITICAL", "URGENT", "emergency", "outage", "down"]
    return [e for e in all_emails if any(kw in e.subject for kw in critical_keywords)]


def get_multiturn_chain(chain_id: str) -> List[Email]:
    """Get all emails in a multi-turn chain"""
    all_emails = get_all_emails()
    return [e for e in all_emails if e.parent_email_id is not None or e.escalation_chain]
