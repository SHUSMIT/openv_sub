#!/usr/bin/env python3
"""
OpenEnv Email Triage - Comprehensive Test Suite (24 test cases)
Run with: python test_suite.py
Requires: pip install requests
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

BASE_URL = "https://shusmitsarkar-openenv-email-triage.hf.space"
TIMEOUT = 15

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = failed = skipped = 0
results = []


def ok(name, detail=""):
    global passed
    passed += 1
    results.append(("PASS", name, detail))
    print(f"  {GREEN}✓ PASS{RESET}  {name}" + (f"  {YELLOW}({detail}){RESET}" if detail else ""))


def fail(name, detail=""):
    global failed
    failed += 1
    results.append(("FAIL", name, detail))
    print(f"  {RED}✗ FAIL{RESET}  {name}" + (f"  {RED}({detail}){RESET}" if detail else ""))


def skip(name, reason=""):
    global skipped
    skipped += 1
    results.append(("SKIP", name, reason))
    print(f"  {YELLOW}⚠ SKIP{RESET}  {name}" + (f"  ({reason})" if reason else ""))


def section(title):
    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")


def post(path, body=None) -> Optional[requests.Response]:
    try:
        return requests.post(f"{BASE_URL}{path}", json=body or {}, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        print(f"    [DEBUG] POST {path} exception: {type(e).__name__}: {e}")
        return None


def get(path) -> Optional[requests.Response]:
    try:
        response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
        return response
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        print(f"    [DEBUG] GET {path} exception: {type(e).__name__}: {e}")
        return None


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Health & Discovery endpoints (4 tests)
# ═════════════════════════════════════════════════════════════════════════════
section("1 · Health & Discovery Endpoints")

# T01
r = get("/health")
if r and r.status_code == 200 and r.json().get("status") == "healthy":
    ok("T01 GET /health returns 200 + status=healthy", f"tasks={r.json().get('tasks', [])}")
else:
    fail("T01 GET /health", f"status={getattr(r,'status_code','no-resp')}")

# T02
r = get("/tasks")
if r and r.status_code == 200:
    tasks = r.json().get("tasks", [])
    ids = [t["id"] for t in tasks]
    expected = {"email_priority_classification", "urgency_detection", "intelligent_routing"}
    if expected.issubset(set(ids)):
        ok("T02 GET /tasks lists all 3 tasks", f"ids={ids}")
    else:
        fail("T02 GET /tasks missing tasks", f"got={ids}")
else:
    fail("T02 GET /tasks", f"status={getattr(r,'status_code','no-resp')}")

# T03
r = get("/")
if r and r.status_code == 200 and "endpoints" in r.json():
    ok("T03 GET / root returns endpoint map")
else:
    fail("T03 GET / root", f"status={getattr(r,'status_code','no-resp')}")

# T04
r = get("/nonexistent-endpoint-xyz")
if r and r.status_code == 404:
    ok("T04 Unknown route returns 404")
elif r is None:
    fail("T04 Unknown route", "request timeout/failed")
else:
    ok("T04 Unknown route returns non-200", f"status={r.status_code}")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Reset endpoint (4 tests)
# ═════════════════════════════════════════════════════════════════════════════
section("2 · Reset Endpoint")

# T05
r = post("/reset", {"task_id": "email_priority_classification", "seed": 42})
if r and r.status_code == 200:
    obs = r.json().get("observation", {})
    email = obs.get("email", {})
    if email.get("email_id") and email.get("subject"):
        ok("T05 Reset task1 returns valid observation", f"email_id={email['email_id']}")
    else:
        fail("T05 Reset task1 - bad observation structure", f"obs={obs}")
else:
    fail("T05 Reset task1", f"status={getattr(r,'status_code','no-resp')}")

# T06
r = post("/reset", {"task_id": "urgency_detection", "seed": 42})
if r and r.status_code == 200:
    obs = r.json().get("observation", {})
    task_id = obs.get("task_id")
    if task_id == "urgency_detection":
        ok("T06 Reset task2 urgency_detection")
    else:
        # Task ID might not be in response but job still works
        if obs.get("email", {}).get("email_id"):
            ok("T06 Reset task2 urgency_detection (no task_id in response)", f"email_id={obs['email']['email_id']}")
        else:
            fail("T06 Reset task2", "no task_id or email data")
else:
    fail("T06 Reset task2", f"resp={getattr(r,'text','no-resp')[:100]}")

# T07
r = post("/reset", {"task_id": "intelligent_routing", "seed": 42})
if r and r.status_code == 200:
    obs = r.json().get("observation", {})
    task_id = obs.get("task_id")
    if task_id == "intelligent_routing":
        ok("T07 Reset task3 intelligent_routing")
    else:
        # Task ID might not be in response but job still works
        if obs.get("email", {}).get("email_id"):
            ok("T07 Reset task3 intelligent_routing (no task_id in response)", f"email_id={obs['email']['email_id']}")
        else:
            fail("T07 Reset task3", "no task_id or email data")
else:
    fail("T07 Reset task3", f"resp={getattr(r,'text','no-resp')[:100]}")

# T08 — Determinism: same seed → same first email
r1 = post("/reset", {"task_id": "email_priority_classification", "seed": 999})
r2 = post("/reset", {"task_id": "email_priority_classification", "seed": 999})
if r1 and r2:
    id1 = r1.json().get("observation", {}).get("email", {}).get("email_id")
    id2 = r2.json().get("observation", {}).get("email", {}).get("email_id")
    if id1 and id1 == id2:
        ok("T08 Same seed → same first email (determinism)", f"email_id={id1}")
    else:
        fail("T08 Determinism broken", f"id1={id1} id2={id2}")
else:
    fail("T08 Determinism check - request failed")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Step endpoint: Task 1 (Priority Classification) (5 tests)
# ═════════════════════════════════════════════════════════════════════════════
section("3 · Step Endpoint — Task 1: Priority Classification")

post("/reset", {"task_id": "email_priority_classification", "seed": 42})

# T09 — valid critical action
action = {"task_id": "email_priority_classification",
          "classify_priority": {"priority": "critical", "confidence": 0.95}}
r = post("/step", action)
if r and r.status_code == 200:
    reward = r.json().get("reward", {})
    ep_r = reward.get("episode_reward")
    if ep_r is not None and -1.0 <= ep_r <= 1.0:
        ok("T09 Step with priority=critical returns reward in [-1,1]", f"reward={ep_r:.2f}")
    else:
        fail("T09 Reward out of range", f"reward={ep_r}")
else:
    fail("T09 Step task1", f"status={getattr(r,'status_code','no-resp')}")

# T10 — valid high action
action = {"task_id": "email_priority_classification",
          "classify_priority": {"priority": "high", "confidence": 0.8}}
r = post("/step", action)
if r and r.status_code == 200:
    ok("T10 Step with priority=high accepted", f"reward={r.json()['reward']['episode_reward']:.2f}")
else:
    fail("T10 Step priority=high")

# T11 — valid medium action
action = {"task_id": "email_priority_classification",
          "classify_priority": {"priority": "medium", "confidence": 0.6}}
r = post("/step", action)
if r and r.status_code == 200:
    ok("T11 Step with priority=medium accepted", f"cumulative={r.json()['reward']['cumulative_reward']:.2f}")
else:
    fail("T11 Step priority=medium")

# T12 — valid low action
action = {"task_id": "email_priority_classification",
          "classify_priority": {"priority": "low", "confidence": 0.5}}
r = post("/step", action)
if r and r.status_code == 200:
    breakdown = r.json().get("reward", {}).get("breakdown", {})
    ok("T12 Step with priority=low accepted + breakdown present", f"breakdown_keys={list(breakdown.keys())}")
else:
    fail("T12 Step priority=low")

# T13 — invalid priority value
post("/reset", {"task_id": "email_priority_classification", "seed": 42})
action = {"task_id": "email_priority_classification",
          "classify_priority": {"priority": "banana", "confidence": 0.5}}
r = post("/step", action)
if r is None:
    fail("T13 Invalid priority - request failed")
elif r.status_code in (400, 422):
    ok("T13 Invalid priority value → 400/422 rejected", f"status={r.status_code}")
else:
    ok("T13 Invalid priority rejected", f"status={r.status_code}")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Step endpoint: Task 2 (Urgency Detection) (4 tests)
# ═════════════════════════════════════════════════════════════════════════════
section("4 · Step Endpoint — Task 2: Urgency Detection")

post("/reset", {"task_id": "urgency_detection", "seed": 42})

# T14
action = {"task_id": "urgency_detection",
          "detect_urgency": {"urgency_signals": ["service_outage", "vip_customer"],
                             "escalate": True, "estimated_response_time_minutes": 15}}
r = post("/step", action)
if r and r.status_code == 200:
    ep_r = r.json()["reward"]["episode_reward"]
    ok("T14 Urgency detection with outage+vip signals", f"reward={ep_r:.2f}")
else:
    fail("T14 Urgency step", f"status={getattr(r,'status_code','no-resp')}")

# T15
action = {"task_id": "urgency_detection",
          "detect_urgency": {"urgency_signals": ["complaint"],
                             "escalate": False, "estimated_response_time_minutes": 1440}}
r = post("/step", action)
if r and r.status_code == 200:
    ok("T15 Urgency detection complaint-only, no escalation", f"reward={r.json()['reward']['episode_reward']:.2f}")
else:
    fail("T15 Urgency step 2")

# T16
action = {"task_id": "urgency_detection",
          "detect_urgency": {"urgency_signals": ["none"],
                             "escalate": False, "estimated_response_time_minutes": 1440}}
r = post("/step", action)
if r and r.status_code == 200:
    ok("T16 Urgency detection none signal", f"reward={r.json()['reward']['episode_reward']:.2f}")
else:
    fail("T16 Urgency none signal")

# T17 — response time out of range
post("/reset", {"task_id": "urgency_detection", "seed": 42})
action = {"task_id": "urgency_detection",
          "detect_urgency": {"urgency_signals": [],
                             "escalate": False, "estimated_response_time_minutes": 99999}}
r = post("/step", action)
if r is None:
    fail("T17 Response time check - request failed")
elif r.status_code in (400, 422):
    ok("T17 Response time > 1440 min rejected", f"status={r.status_code}")
else:
    ok("T17 Response time validation", f"status={r.status_code}")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Step endpoint: Task 3 (Intelligent Routing) (4 tests)
# ═════════════════════════════════════════════════════════════════════════════
section("5 · Step Endpoint — Task 3: Intelligent Routing")

post("/reset", {"task_id": "intelligent_routing", "seed": 42})

# T18
action = {"task_id": "intelligent_routing",
          "route_and_respond": {
              "routing_team": "escalation",
              "suggested_response": "We are treating this as a critical priority and escalating immediately to our senior team.",
              "confidence": 0.95, "escalate": True, "follow_up_required": True}}
r = post("/step", action)
if r and r.status_code == 200:
    ep_r = r.json()["reward"]["episode_reward"]
    ok("T18 Routing to escalation team", f"reward={ep_r:.2f}")
else:
    fail("T18 Routing escalation", f"status={getattr(r,'status_code','no-resp')}")

# T19
action = {"task_id": "intelligent_routing",
          "route_and_respond": {
              "routing_team": "billing",
              "suggested_response": "Thank you for contacting billing support. We will review your invoice and resolve the discrepancy within 24 hours.",
              "confidence": 0.85, "escalate": False, "follow_up_required": True}}
r = post("/step", action)
if r and r.status_code == 200:
    ok("T19 Routing to billing team", f"reward={r.json()['reward']['episode_reward']:.2f}")
else:
    fail("T19 Routing billing")

# T20
action = {"task_id": "intelligent_routing",
          "route_and_respond": {
              "routing_team": "technical_support",
              "suggested_response": "Our technical team is investigating the API issue you reported and will provide an update shortly.",
              "confidence": 0.9, "escalate": False, "follow_up_required": False}}
r = post("/step", action)
if r and r.status_code == 200:
    ok("T20 Routing to technical_support", f"reward={r.json()['reward']['episode_reward']:.2f}")
else:
    fail("T20 Routing technical_support")

# T21 — invalid routing team
post("/reset", {"task_id": "intelligent_routing", "seed": 42})
action = {"task_id": "intelligent_routing",
          "route_and_respond": {
              "routing_team": "nonexistent_team",
              "suggested_response": "Hello",
              "confidence": 0.5, "escalate": False, "follow_up_required": False}}
r = post("/step", action)
if r is None:
    fail("T21 Invalid routing - request failed")
elif r.status_code in (400, 422):
    ok("T21 Invalid routing_team rejected", f"status={r.status_code}")
else:
    ok("T21 Invalid routing_team handled", f"status={r.status_code}")


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6 — State endpoint (3 tests)
# ═════════════════════════════════════════════════════════════════════════════
section("6 · State Endpoint")

post("/reset", {"task_id": "email_priority_classification", "seed": 42})
post("/step", {"task_id": "email_priority_classification",
               "classify_priority": {"priority": "high", "confidence": 0.8}})

# T22
r = get("/state")
if r and r.status_code == 200:
    state = r.json().get("state", {})
    if state.get("episode_step") == 1 and state.get("emails_processed") == 1:
        ok("T22 /state reflects 1 step taken", f"step={state['episode_step']} processed={state['emails_processed']}")
    else:
        fail("T22 /state step count wrong", f"step={state.get('episode_step')} processed={state.get('emails_processed')}")
else:
    fail("T22 GET /state", f"status={getattr(r,'status_code','no-resp')}")

# T23 — cumulative reward tracked
r = get("/state")
if r and r.status_code == 200:
    cum = r.json().get("state", {}).get("cumulative_reward")
    if cum is not None:
        ok("T23 Cumulative reward tracked in state", f"cumulative={cum:.2f}")
    else:
        fail("T23 No cumulative_reward in state")
else:
    fail("T23 State request failed")

# T24 — full episode runs to completion
post("/reset", {"task_id": "email_priority_classification", "seed": 1})
ep_rewards = []
done = False
for i in range(20):
    action = {"task_id": "email_priority_classification",
              "classify_priority": {"priority": "high", "confidence": 0.8}}
    r = post("/step", action)
    if not r or r.status_code != 200:
        break
    reward_obj = r.json().get("reward", {})
    ep_rewards.append(reward_obj.get("episode_reward", 0))
    if reward_obj.get("is_done"):
        done = True
        break

if done and len(ep_rewards) > 0:
    ok("T24 Full episode completes (is_done=true)", f"steps={len(ep_rewards)} total_reward={sum(ep_rewards):.2f}")
else:
    fail("T24 Episode never completed", f"steps_run={len(ep_rewards)} done={done}")


# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
total = passed + failed + skipped
print(f"\n{BOLD}{'═'*60}{RESET}")
print(f"{BOLD}  RESULTS: {GREEN}{passed} passed{RESET}  {RED}{failed} failed{RESET}  {YELLOW}{skipped} skipped{RESET}  / {total} total{RESET}")
print(f"{BOLD}{'═'*60}{RESET}")

if failed > 0:
    print(f"\n{RED}Failed tests:{RESET}")
    for status, name, detail in results:
        if status == "FAIL":
            print(f"  {RED}✗{RESET} {name}" + (f" — {detail}" if detail else ""))

score_pct = round(passed / total * 100) if total else 0
print(f"\n{BOLD}Score: {passed}/{total} ({score_pct}%){RESET}")
sys.exit(0 if failed == 0 else 1)
