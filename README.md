---
title: OpenEnv Email Triage
emoji: 📧
colorFrom: purple
colorTo: blue
sdk: docker
app_file: app.py
app_port: 7860
pinned: false
---

# OpenEnv Email Triage Environment

A real-world email triage and intelligent routing environment for training and evaluating AI agents using the OpenEnv framework. This environment simulates realistic customer support workflows where agents must classify emails by priority, detect urgency signals, and route to appropriate teams.

## Overview

**EmailTriageEnv** provides a complete reinforcement learning environment based on the OpenEnv specification where AI agents learn to:
- Classify incoming support emails into priority levels (CRITICAL → HIGH → MEDIUM → LOW)
- Detect urgency signals and make escalation decisions
- Route emails intelligently to specialized teams and compose appropriate responses

This is a **real-world task simulation** — not a game or toy problem. Email triage is a fundamental workflow in customer support, and this environment captures the core decision-making challenges agents face.

## Real-World Utility

Email triage is a critical operational challenge across all customer-facing organizations:
- **Customer Support Teams**: Need to respond to urgent issues first (e.g., service outages affecting 500+ users)
- **SaaS/Enterprise Platforms**: Route billing, technical, sales inquiries to correct specialists
- **Compliance**: Prioritize compliance requests with firm deadlines
- **Operational Efficiency**: Avoid wasting time on low-priority requests while high-value customers wait

## Key Features

✅ **3 Tasks with Increasing Difficulty**
- **Easy**: Priority classification (binary/ternary signals)
- **Medium**: Urgency detection with escalation decisions
- **Hard**: Intelligent routing + response composition

✅ **Deterministic Graders**: Each task has a clear, reproducible scoring function (0.0–1.0 range)

✅ **Meaningful Reward Shaping**: Partial credit for partial progress; penalties for clearly wrong decisions

✅ **Realistic Email Dataset**: 150+ emails covering diverse real support scenarios

✅ **OpenEnv Spec Compliance**: Typed Pydantic models, `/reset`, `/step`, `/state` HTTP endpoints

✅ **Containerized**: Dockerfile + working server for HF Spaces deployment

## Action & Observation Spaces

### Observation Space

```python
Observation:
  email: Email                # Current email to process
    - email_id: str
    - sender: str
    - subject: str
    - body: str
    - timestamp: float
    - sender_history: int     # Previous emails from sender
    - is_reply: bool
    - attachments: int
    - customer_lifetime_value: float  # 0.0-1.0
  task_id: str
  step_count: int
  episode_info: dict
  action_history: list        # Actions on related emails (multi-turn)
```

### Action Space

#### Task 1: Email Priority Classification
```python
Action:
  classify_priority:
    priority: PriorityLevel  # critical | high | medium | low
    confidence: float        # 0.0-1.0
```

#### Task 2: Urgency & Escalation Detection
```python
Action:
  detect_urgency:
    urgency_signals: list    # [deadline, complaint, urgent_keyword, repeat_contact,
                             #  vip_customer, service_outage, payment_issue, none]
    escalate: bool
    estimated_response_time_minutes: int  # 1-1440
```

#### Task 3: Intelligent Email Routing & Response
```python
Action:
  route_and_respond:
    routing_team: RoutingTeam  # billing | technical_support | sales |
                               # general_support | escalation | feedback
    suggested_response: str    # 50-500 character response draft
    confidence: float          # 0.0-1.0
    escalate: bool
    follow_up_required: bool
```

### Reward Space

- **Range**: -1.0 to +1.0 per step
- **Episode Cumulative**: -10.0 to +10.0
- **Partial Credit**: Progressive rewards for partial correctness

## Tasks

### Task 1: Email Priority Classification (Easy)
- Classify emails into 4 priority buckets
- Episodes: 15 emails, max 20 steps

### Task 2: Urgency & Escalation Detection (Medium)
- Identify urgency signals and recommend escalation + response time
- Episodes: 20 emails, max 30 steps

### Task 3: Intelligent Email Routing & Response (Hard)
- Route to correct team AND compose appropriate response
- Episodes: 25 emails, max 40 steps

## Getting Started

### Installation

```bash
git clone <repo-url>
cd openenv-email-triage
pip install -r requirements.txt
```

### Running Baseline Agent

```bash
export HF_TOKEN="hf_..."
export API_BASE_URL="https://api.groq.com/openai/v1"
export MODEL_NAME="mixtral-8x7b-32768"
python inference.py
```

### Environment API (HTTP)

```bash
# Start server
python -m uvicorn server.app:app --host 0.0.0.0 --port 7860
```

**Endpoints:**
- `GET /health` — Health check
- `POST /reset` — Initialize episode, returns Observation
- `POST /step` — Process action, returns (Observation, Reward, info)
- `GET /state` — Current State snapshot
- `GET /tasks` — List all tasks

## Docker

```bash
docker build -t openenv-email-triage:latest .
docker run -p 7860:7860 \
  -e HF_TOKEN="hf_..." \
  -e API_BASE_URL="https://api.groq.com/openai/v1" \
  -e MODEL_NAME="mixtral-8x7b-32768" \
  openenv-email-triage:latest
```

## Baseline Performance

| Task | Expected Score Range |
|------|---------------------|
| **Priority Classification** | 0.65–0.85 |
| **Urgency Detection** | 0.50–0.70 |
| **Intelligent Routing** | 0.50–0.70 |

## Project Structure

```
openenv-email-triage/
├── inference.py          # Baseline evaluation script (MAIN)
├── environment.py        # EmailTriageEnv implementation
├── models.py             # Pydantic models
├── definitions.py        # Task configs + email data
├── expanded_emails.py    # Diverse email dataset (150+ emails)
├── task_graders.py       # Scoring functions
├── dynamic_grader.py     # LLM-based dynamic grading (fallback)
├── server.py             # FastAPI server (standalone)
├── app.py                # HF Spaces entrypoint
├── server/
│   ├── __init__.py
│   └── app.py            # FastAPI server (package)
├── openenv.yaml          # OpenEnv configuration
├── Dockerfile            # Container definition
└── requirements.txt      # Dependencies
```

## License

OpenRAIL — provided as part of the OpenEnv competition.
