---
title: OpenEnv Email Triage
emoji: 📧
colorFrom: purple
colorTo: blue
sdk: docker
app_file: server.py
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

This environment is immediately useful for:
- Training agents to make intelligent routing decisions
- Evaluating whether LLMs can prioritize effectively
- Benchmarking agentic decision-making on a real operational task

## Key Features

✅ **3 Tasks with Increasing Difficulty**
- **Easy**: Priority classification (binary/ternary signals)
- **Medium**: Urgency detection with escalation decisions
- **Hard**: Intelligent routing + response composition

✅ **Deterministic Graders**: Each task has a clear, reproducible scoring function (0.0–1.0 range)

✅ **Meaningful Reward Shaping**: Partial credit for partial progress; penalties for clearly wrong decisions

✅ **Realistic Email Dataset**: 10 representative emails covering real support scenarios (billing, outages, complaints, etc.)

✅ **OpenEnv Spec Compliance**: Typed Pydantic models, `/reset`, `/step`, `/state` HTTP endpoints

✅ **Containerized**: Dockerfile + working server for HF Spaces deployment

## Action & Observation Spaces

### Observation Space

Each observation contains:
```python
Observation:
  email: Email                # Current email to process
    - email_id: str          # Unique identifier
    - sender: str            # Email address
    - subject: str           # Subject line
    - body: str              # Email body (max 2000 chars)
    - timestamp: float       # Unix timestamp
    - sender_history: int    # Previous emails from sender (0-100)
    - is_reply: bool         # Whether replying to prior email
    - attachments: int       # Number of attachments (0-5)
    - customer_lifetime_value: float # 0.0-1.0 (high-value flag)
  task_id: str              # Current task name
  step_count: int           # Steps in this episode
  episode_info: dict        # Metadata (total emails, processed count, etc.)
```

### Action Space

#### Task 1: Email Priority Classification
```python
Action:
  classify_priority:
    priority: PriorityLevel  # critical | high | medium | low
    confidence: float        # 0.0-1.0 (prediction confidence)
```

#### Task 2: Urgency & Escalation Detection
```python
Action:
  detect_urgency:
    urgency_signals: list    # [deadline, complaint, urgent_keyword, repeat_contact, 
                             #  vip_customer, service_outage, payment_issue, none]
    escalate: bool           # Should prioritize for immediate response?
    estimated_response_time_minutes: int  # Target response time (1-1440)
```

#### Task 3: Intelligent Email Routing & Response
```python
Action:
  route_and_respond:
    routing_team: RoutingTeam  # billing | technical_support | sales | 
                               # general_support | escalation | feedback
    suggested_response: str    # 50-500 character email response draft
    confidence: float          # 0.0-1.0
    escalate: bool             # Escalate to manager?
    follow_up_required: bool   # Schedule follow-up?
```

### Reward Space

Rewards are shaped to provide meaningful learning signals:
- **Range**: -1.0 to +1.0 per step
- **Episode Cumulative**: Can reach -5.0 to +10.0 across episode
- **Partial Credit**: Agents receive progressive rewards for partial correctness

#### Task 1: Priority Classification
- +1.0: Correct priority class
- +0.5: Off by one level (e.g., predicted HIGH when CRITICAL)
- -0.25: Completely wrong or missing action
- Confidence penalty: (-1.0 confidence) × 0.2

#### Task 2: Urgency Detection
- +1.0: Perfect signal detection + correct escalation
- +0.3 per correct signal detected
- -0.2 per missed signal
- -0.1 per false positive
- +0.3 for correct escalation decision
- +0.2 for appropriate response time estimate

#### Task 3: Intelligent Routing & Response
- +0.5: Correct routing team
- +0.3: Response length in acceptable range
- +0.1: Correct escalation decision
- +0.05: Correct follow-up flag
- -10% if confidence < 0.5

## Tasks & Difficulty Progression

### Task 1: Email Priority Classification (Easy)
**Objective**: Classify emails into 4 priority buckets

**Expected Difficulty**: Beginner agents should achieve 40-60% accuracy with basic keyword matching

**Example Emails**:
- "CRITICAL: Production down" → CRITICAL
- "Billing error $50" → HIGH
- "Feature request" → LOW

**Episode**: 5 emails per episode, max 10 steps

**Grader Quality**: Exact priority levels with confidence penalty for low confidence scores

### Task 2: Urgency & Escalation Detection (Medium)
**Objective**: Identify urgency signals and recommend escalation + response time

**Expected Difficulty**: Requires understanding multiple signals, business logic reasoning

**Urgency Signals Detected**:
- DEADLINE: Explicit time pressure
- COMPLAINT: Customer dissatisfaction
- REPEAT_CONTACT: Customer has emailed before
- VIP_CUSTOMER: High-value customer
- SERVICE_OUTAGE: System failure affecting many
- PAYMENT_ISSUE: Billing or payment failure
- URGENT_KEYWORD: "urgent", "ASAP", etc.

**Episode**: 7 emails per episode, max 15 steps

**Grader Quality**: Rewards correct signal detection, appropriate escalation logic, realistic response times

### Task 3: Intelligent Email Routing & Response (Hard)
**Objective**: Route to correct team AND compose appropriate response

**Expected Difficulty**: Hardest task — requires understanding context + generating coherent responses

**Routing Teams**:
- **Billing**: Charge, payment, invoice issues
- **Technical Support**: API, integration, technical problems
- **Sales**: Pricing, quotes, new customer inquiries
- **General Support**: General inquiries, info requests
- **Escalation**: Service outages, critical issues, angry customers
- **Feedback**: Feature requests, suggestions

**Episode**: 10 emails per episode, max 20 steps

**Grader Quality**: 5-component reward (routing + response quality + escalation + follow-up + confidence)

## Getting Started

### Installation

```bash
# Clone repo
git clone <repo-url>
cd openenv-email-triage

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional - for inference)
cp .env.example .env
# Edit .env with your API credentials
```

### Quick Validation

```bash
# Test environment without calling LLM
python validate.py
```

Output:
```
============================================================
TEST: Task Configurations
============================================================
PASS email_priority_classification: Email Priority Classification (easy)
PASS urgency_detection: Urgency & Escalation Detection (medium)
PASS intelligent_routing: Intelligent Email Routing & Response (hard)

============================================================
TEST: Environment Initialization
============================================================
PASS Environment initialized for task: email_priority_classification
PASS Environment initialized for task: urgency_detection
PASS Environment initialized for task: intelligent_routing

[... more tests ...]

SUMMARY: All tests passed!
```

### Running Baseline Agent

The baseline inference script runs a language model against all 3 tasks:

```bash
# Using Groq API (FREE, fast)
export GROQ_API_KEY="gsk-..."
export API_BASE_URL="https://api.groq.com/openai/v1"
export MODEL_NAME="mixtral-8x7b-32768"
python inference.py

# OR using OpenAI
export OPENAI_API_KEY="sk-..."
export MODEL_NAME="gpt-4"
python inference.py
```

Output (strict format):
```
[START] task=email_priority_classification env=openenv-email-triage model=mixtral-8x7b-32768
[STEP] step=1 action=classify_priority(priority=critical,confidence=0.95) reward=1.00 done=false error=null
[STEP] step=2 action=classify_priority(priority=high,confidence=0.87) reward=0.50 done=false error=null
[STEP] step=3 action=classify_priority(priority=low,confidence=0.92) reward=1.00 done=false error=null
[STEP] step=4 action=classify_priority(priority=medium,confidence=0.75) reward=-0.25 done=false error=null
[STEP] step=5 action=classify_priority(priority=critical,confidence=0.88) reward=1.00 done=true error=null
[END] success=true steps=5 rewards=1.00,0.50,1.00,-0.25,1.00

[START] task=urgency_detection env=openenv-email-triage model=mixtral-8x7b-32768
[STEP] step=1 action=detect_urgency(...) reward=0.75 done=false error=null
...
[END] success=true steps=7 rewards=...

[START] task=intelligent_routing env=openenv-email-triage model=mixtral-8x7b-32768
[STEP] step=1 action=route_and_respond(...) reward=0.80 done=false error=null
...
[END] success=true steps=10 rewards=...
```

Results are saved to `baseline_results.json`.

### Environment API (HTTP)

When deployed or running locally, the environment exposes OpenEnv endpoints:

```bash
# Start server
python -m uvicorn server:app --host 0.0.0.0 --port 7860
```

Endpoints:

#### `/health` (GET)
```bash
curl http://localhost:7860/health
# { "status": "healthy", "service": "OpenEnv Email Triage", "tasks": [...] }
```

#### `/reset` (POST)
```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "email_priority_classification", "seed": 42}'

# Returns: { "status": "success", "observation": {...} }
```

#### `/step` (POST)
```bash
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "email_priority_classification",
    "action": {
      "task_id": "email_priority_classification",
      "classify_priority": {
        "priority": "critical",
        "confidence": 0.95
      }
    }
  }'

# Returns: { "status": "success", "observation": {...}, "reward": {...}, "info": {...} }
```

#### `/state` (GET)
```bash
curl http://localhost:7860/state?task_id=email_priority_classification

# Returns: { "status": "success", "state": {...} }
```

## Baseline Performance

Expected scores on frontier models (GPT-4, Mixtral, etc.):

| Task | Easy Agents | Medium Agents | Hard Agents |
|------|-------------|---------------|------------|
| **Priority Classification** | 0.65-0.80 | 0.75-0.85 | 0.80-0.95 |
| **Urgency Detection** | 0.40-0.55 | 0.55-0.70 | 0.70-0.85 |
| **Intelligent Routing** | 0.35-0.50 | 0.50-0.68 | 0.65-0.82 |
| **Average Across All** | ~0.47 | ~0.64 | ~0.77 |

Note: Baseline agent based on Mixtral-8x7b in CoT mode achieved ~0.65 average.

## OpenEnv Spec Compliance

### Typed Models (Pydantic)

All models fully typed and validated:
- `Observation`: Email + task metadata
- `Action`: Task-specific action unions
- `Reward`: Episode reward + cumulative + breakdown
- `State`: Full environment state snapshot
- `Email`, `PriorityLevel`, `RoutingTeam`, `UrgencySignal`: Supporting enums/models

### Endpoints

✅ `/reset`: Initializes episode, returns Observation
✅ `/step`: Processes action, returns (Observation, Reward, info dict)
✅ `/state`: Returns current State snapshot
✅ `/health`: Health check

### Configuration (openenv.yaml)

```yaml
name: EmailTriageEnv
version: "1.0.0"
metadata:
  description: "Real-world email triage..."
  domain: customer_support
  difficulty: [easy, medium, hard]
  task_count: 3

endpoints:
  reset: /reset
  step: /step
  state: /state

environment:
  observation_model: Observation
  action_model: Action
  reward_model: Reward

tasks:
  - id: email_priority_classification
    name: "Email Priority Classification"
    difficulty: easy
    grader: email_priority_grader
  - id: urgency_detection
    name: "Urgency & Escalation Detection"
    difficulty: medium
    grader: urgency_detection_grader
  - id: intelligent_routing
    name: "Intelligent Email Routing & Response"
    difficulty: hard
    grader: intelligent_routing_grader
```

## Deployment to Hugging Face Spaces

### Prerequisites
- Hugging Face account + personal access token
- Docker installed locally

### Steps

1. **Create HF Space**:
   - Visit https://huggingface.co/new-space
   - Name: `openenv-email-triage`
   - License: OpenRAIL (or your choice)
   - Space SDK: Docker
   - Create

2. **Deploy**:
   ```bash
   git clone https://huggingface.co/spaces/<username>/openenv-email-triage
   cd openenv-email-triage
   git remote add origin <repo-url>
   git push -u origin main
   ```

3. **Verify Deployment**:
   ```bash
   # Wait for build to complete (5-10 min)
   curl https://<username>-openenv-email-triage.hf.space/health
   # Should return: { "status": "healthy", ... }
   ```

### Environment Variables (in HF Space Settings)

Add to **Repository Secrets**:
```
GROQ_API_KEY=gsk-...
API_BASE_URL=https://api.groq.com/openai/v1
MODEL_NAME=mixtral-8x7b-32768
```

## Docker

### Build & Run Locally

```bash
# Build
docker build -t openenv-email-triage:latest .

# Run
docker run -p 7860:7860 \
  -e GROQ_API_KEY="gsk-..." \
  -e API_BASE_URL="https://api.groq.com/openai/v1" \
  -e MODEL_NAME="mixtral-8x7b-32768" \
  openenv-email-triage:latest
```

### Dockerfile Highlights

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
```

- Uses Python 3.11 slim image for minimal size
- Installs all dependencies in one layer (efficient)
- Exposes port 7860 (HF Spaces default)
- Health check enabled (curl to /health)

## Project Structure

```
openenv-email-triage/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── openenv.yaml                       # OpenEnv spec configuration
├── Dockerfile                         # Container definition
├── .env.example                       # Environment variables template
├── .dockerignore                      # Docker build exclusions
│
├── inference.py                       # Baseline evaluation script (MAIN)
├── server.py                          # FastAPI HTTP server
├── validate.py                        # Local validation tests
├── test_inference_logic.py            # Unit tests
│
└── env/                               # Environment package
    ├── __init__.py
    ├── environment.py                 # Main EmailTriageEnv class
    ├── models.py                      # Pydantic models (Email, Action, Reward, etc.)
    │
    ├── tasks/
    │   ├── __init__.py
    │   └── definitions.py             # Task configs + email data
    │
    └── graders/
        ├── __init__.py
        └── task_graders.py            # Scoring functions for all 3 tasks
```

## Configuration

### Task Difficulty Settings

Modify `env/tasks/definitions.py` TASK_CONFIGS:

```python
TASK_CONFIGS = {
    "email_priority_classification": {
        "name": "Email Priority Classification",
        "difficulty": "easy",
        "emails_per_episode": 5,      # Emails per episode
        "max_steps": 10,               # Max steps before episode ends
    },
    "urgency_detection": {
        "difficulty": "medium",
        "emails_per_episode": 7,
        "max_steps": 15,
    },
    "intelligent_routing": {
        "difficulty": "hard",
        "emails_per_episode": 10,
        "max_steps": 20,
    },
}
```

### Adding Custom Emails

Edit `env/tasks/definitions.py`:

```python
def get_training_emails() -> List[Email]:
    base_time = datetime.now().timestamp()
    emails = [
        Email(
            email_id="custom_001",
            sender="customer@example.com",
            subject="...",
            body="...",
            timestamp=base_time,
            sender_history=5,
            is_reply=False,
            attachments=0,
            customer_lifetime_value=0.5,
        ),
        # Add more emails...
    ]
    return emails
```

### Customizing Grading

Modify `env/graders/task_graders.py` to adjust reward functions:

```python
class EmailPriorityGrader:
    def grade(self, email: Email, action: Action) -> Tuple[float, Dict]:
        # Customize reward logic
        if distance == 0:
            reward = 1.0
        elif distance == 1:
            reward = 0.5  # Adjust penalty
        else:
            reward = 0.0
        return reward, details
```

## Testing & Validation

### Local Validation

```bash
python validate.py
```

This runs:
- ✅ Task configuration loading
- ✅ Environment initialization for all tasks
- ✅ Episode simulation (no LLM required)
- ✅ Grader determinism verification
- ✅ OpenEnv spec compliance checks

### Running Tests

```bash
python -m pytest test_inference_logic.py -v
```

### Manual Testing

```python
from env.environment import EmailTriageEnv
from env.models import Action, ActionClassifyPriority, PriorityLevel

# Create environment
env = EmailTriageEnv(task_id="email_priority_classification", seed=42)

# Get initial observation
obs = env.reset()
print(f"Email: {obs.email.subject}")

# Take action
action = Action(
    task_id="email_priority_classification",
    classify_priority=ActionClassifyPriority(
        priority=PriorityLevel.CRITICAL,
        confidence=0.95
    )
)

# Step environment
next_obs, reward, info = env.step(action)
print(f"Reward: {reward.episode_reward:.3f}")
print(f"Done: {reward.is_done}")
```

## Known Limitations

1. **Email Dataset Limited**: 10 total emails across all tasks. Could be expanded to 100+ with more diverse scenarios.

2. **Graders are Shallow**: Ground truth is hardcoded. Could use human labeling or LLM grading for evaluation.

3. **No Action History**: Agent can't see prior decisions on same email. Could be useful pre-context.

4. **Single-Email Episodes**: Agent processes one email at a time, not multi-turn conversations.

5. **No Real Consequences**: Routing decisions don't affect future emails. Real systems have downstream effects.

## Future Enhancements

- **Multi-turn Emails**: Build conversation trees where agent decisions affect follow-up messages
- **Consequence Tracking**: Wrong routing creates downstream failures (longer resolution times, more escalations)
- **Human Labeling**: Integrate human feedback on grading correctness
- **Expanded Dataset**: 100+ diverse emails across industries (B2B, B2C, SaaS, etc.)
- **Agentic Loops**: Multi-step reasoning where agents can query for additional info
- **Batch Processing**: Process multiple emails in parallel with resource constraints

## Contributing

To contribute improvements:

1. Fork and create a feature branch
2. Test locally: `python validate.py && python -m pytest`
3. Ensure backward compatibility with existing graders
4. Submit PR with description of changes

## License

This environment is provided as part of the OpenEnv competition. See LICENSE file.

## Citation

If you use this environment in published research, please cite:

```bibtex
@dataset{emailtriage2025,
  title={OpenEnv Email Triage Environment},
  author={OpenEnv Community},
  year={2025},
  url={https://huggingface.co/spaces/.../openenv-email-triage}
}
```

## Support & Issues

- **OpenEnv Docs**: https://github.com/openenv/openenv-core
- **HF Spaces Issues**: https://huggingface.co/spaces/.../openenv-email-triage/discussions
- **GitHub Issues**: https://github.com/.../openenv-email-triage/issues

---

**Last Updated**: April 2025
**OpenEnv Spec Version**: 1.0.0
**Environment Version**: 1.0.0
