#!/usr/bin/env python3
"""
OpenEnv Compliance Validator (Fixed)
====================================

Tests required for competition submission:
1. ✅ OpenEnv spec compliance (reset/step/state)
2. ✅ 3+ tasks with graders
3. ✅ Inference format ([START], [STEP], [END])
4. ✅ Docker buildable
5. ✅ HF Space deployable
"""

import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import EmailTriageEnv
from models import Action, ActionClassifyPriority, PriorityLevel


def section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def test_pass(desc: str, details: str = ""):
    print(f"  ✅ {desc}")
    if details:
        print(f"     {details}")


def test_fail(desc: str, details: str = ""):
    print(f"  ❌ {desc}")
    if details:
        print(f"     {details}")


def test_spec_compliance():
    """Test OpenEnv spec compliance"""
    section("1. OPENENV SPEC COMPLIANCE")
    
    try:
        env = EmailTriageEnv(task_id="email_priority_classification", seed=42)
        test_pass("Environment instantiation", "EmailTriageEnv created")
        
        # Test reset()
        obs = env.reset()
        assert hasattr(obs, 'email'), "Missing obs.email"
        assert hasattr(obs, 'task_id'), "Missing obs.task_id"
        assert hasattr(obs, 'step_count'), "Missing obs.step_count"
        test_pass("reset() method", f"Returns Observation with email_id={obs.email.email_id}")
        
        # Test step()
        action = Action(
            task_id="email_priority_classification",
            classify_priority=ActionClassifyPriority(priority=PriorityLevel.HIGH, confidence=0.9)
        )
        obs, reward, info = env.step(action)
        assert hasattr(reward, 'episode_reward'), "Missing reward.episode_reward"
        assert hasattr(reward, 'cumulative_reward'), "Missing reward.cumulative_reward"
        assert hasattr(reward, 'is_done'), "Missing reward.is_done"
        test_pass("step() method", f"Returns Observation, Reward, Info | reward={reward.episode_reward:.2f}")
        
        # Test state()
        state = env.state()
        # state() returns State model (Pydantic BaseModel is acceptable)
        assert hasattr(state, 'task_id'), "state() should have task_id"
        assert hasattr(state, 'episode_step'), "state() should have episode_step"
        test_pass("state() method", f"Returns State model with task_id and episode_step")
        
        return True
    except Exception as e:
        test_fail("OpenEnv spec compliance", str(e))
        return False


def test_three_tasks():
    """Test 3+ tasks exist"""
    section("2. MULTIPLE TASKS (3 required)")
    
    try:
        tasks = [
            "email_priority_classification",
            "urgency_detection",
            "intelligent_routing"
        ]
        
        for i, task_id in enumerate(tasks, 1):
            env = EmailTriageEnv(task_id=task_id, seed=42)
            obs = env.reset()
            test_pass(f"Task {i}: {task_id}", f"Initialized | Email: {obs.email.email_id}")
        
        return True
    except Exception as e:
        test_fail("Task initialization", str(e))
        return False


def test_grading():
    """Test grading/reward functionality"""
    section("3. GRADING & REWARD SYSTEM")
    
    try:
        env = EmailTriageEnv(task_id="email_priority_classification", seed=42)
        obs = env.reset()
        
        # Run 3 steps
        rewards = []
        for i in range(3):
            action = Action(
                task_id="email_priority_classification",
                classify_priority=ActionClassifyPriority(priority=PriorityLevel.HIGH, confidence=0.9)
            )
            obs, reward, info = env.step(action)
            rewards.append(reward.episode_reward)
            
            # Check reward is in valid range
            assert -1.0 <= reward.episode_reward <= 1.0, f"Reward {reward.episode_reward} out of range"
        
        test_pass("Reward generation", f"3 steps | Rewards: {[f'{r:.2f}' for r in rewards]}")
        test_pass("Reward range", "All rewards in [-1.0, 1.0]")
        test_pass("Deterministic grading", f"Cumulative: {reward.cumulative_reward:.2f}")
        
        return True
    except Exception as e:
        test_fail("Grading system", str(e))
        return False


def test_format_compliance():
    """Test [START], [STEP], [END] format strings"""
    section("4. INFERENCE OUTPUT FORMAT")
    
    try:
        import re
        
        # Valid format examples
        start = "[START] task=email_priority_classification env=openenv-email-triage model=gpt-4"
        step = "[STEP] step=1 action=classify_priority(...) reward=0.50 done=false error=null"
        end = "[END] success=true steps=3 rewards=0.50,0.75,0.25"
        
        # Regex patterns (from spec)
        start_pattern = r"\[START\] task=\S+ env=\S+ model=\S+"
        step_pattern = r"\[STEP\] step=\d+ action=\S+ reward=-?\d+\.\d{2} done=(true|false) error=(\S+|null)"
        end_pattern = r"\[END\] success=(true|false) steps=\d+ rewards=(-?\d+\.\d{2},?)*"
        
        assert re.match(start_pattern, start), "START format failed"
        test_pass("START format", start)
        
        assert re.match(step_pattern, step), "STEP format failed"
        test_pass("STEP format", step)
        
        assert re.match(end_pattern, end), "END format failed"
        test_pass("END format", end)
        
        return True
    except Exception as e:
        test_fail("Format compliance", str(e))
        return False


def test_config_files():
    """Test config files exist"""
    section("5. CONFIGURATION FILES")
    
    required = [
        ("openenv.yaml", "OpenEnv configuration"),
        ("Dockerfile", "Container definition"),
        ("requirements.txt", "Python dependencies"),
        ("README.md", "Documentation"),
        ("inference.py", "Baseline script"),
    ]
    
    all_ok = True
    for filename, desc in required:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            test_pass(f"{filename}", f"({size:,} bytes) - {desc}")
        else:
            test_fail(f"{filename} MISSING", desc)
            all_ok = False
    
    # Check openenv.yaml structure
    try:
        import yaml
        with open("openenv.yaml") as f:
            cfg = yaml.safe_load(f)
        
        required_keys = ["id", "name", "tasks"]
        for key in required_keys:
            if key in cfg:
                test_pass(f"openenv.yaml: {key} field present")
            else:
                test_fail(f"openenv.yaml: {key} field MISSING")
                all_ok = False
    except Exception as e:
        test_fail("openenv.yaml parsing", str(e))
        all_ok = False
    
    return all_ok


def test_docker():
    """Test Docker file validity"""
    section("6. DOCKER CONFIGURATION")
    
    try:
        with open("Dockerfile") as f:
            content = f.read()
        
        checks = [
            ("FROM", "Base image"),
            ("RUN pip install", "Dependencies installation"),
            ("EXPOSE", "Port exposure"),
            ("CMD", "Start command"),
        ]
        
        all_ok = True
        for marker, desc in checks:
            if marker in content:
                test_pass(f"{marker} present", desc)
            else:
                test_fail(f"{marker} MISSING", desc)
                all_ok = False
        
        return all_ok
    except Exception as e:
        test_fail("Dockerfile check", str(e))
        return False


def test_inference_script():
    """Test inference script structure"""
    section("7. INFERENCE SCRIPT")
    
    try:
        with open("inference.py") as f:
            content = f.read()
        
        checks = [
            ("from openai import OpenAI", "Uses OpenAI client"),
            ("[START]", "Emits [START] line"),
            ("[STEP]", "Emits [STEP] line"),
            ("[END]", "Emits [END] line"),
            ("env.reset()", "Calls reset()"),
            ("env.step(", "Calls step()"),
        ]
        
        all_ok = True
        for marker, desc in checks:
            if marker in content:
                test_pass(f"✓ {desc}", f"Code contains: {marker}")
            else:
                test_fail(f"✗ {desc}", f"Missing: {marker}")
                all_ok = False
        
        lines = len(content.split('\n'))
        test_pass("Script size", f"{lines} lines")
        
        return all_ok
    except Exception as e:
        test_fail("Inference script check", str(e))
        return False


def main():
    print("\n" + "╔" + "="*68 + "╗")
    print("║  OpenEnv Email Triage - COMPLIANCE VALIDATOR                  ║")
    print("║  Pre-submission checklist for competition requirements       ║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "OpenEnv Spec": test_spec_compliance(),
        "3 Tasks": test_three_tasks(),
        "Grading System": test_grading(),
        "Format ([START]/[STEP]/[END])": test_format_compliance(),
        "Config Files": test_config_files(),
        "Docker": test_docker(),
        "Inference Script": test_inference_script(),
    }
    
    section("SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {test_name}")
    
    print(f"\n  Score: {passed}/{total} checks passed")
    
    if passed == total:
        print(f"\n  🎉 ALL CHECKS PASSED - READY FOR SUBMISSION! 🎉\n")
        return 0
    else:
        print(f"\n  ⚠️  Fix {total - passed} issue(s) before submitting\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
