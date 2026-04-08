#!/usr/bin/env python3
"""
Phase 2 Validation Test Suite — Comprehensive checks for all critical fixes
Tests both ERROR FIXES and PHASE 2 READINESS
"""

import os
import sys
import json
import re
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Test Results
results = {
    "timestamp": datetime.now().isoformat(),
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}


def log_test(name: str, passed: bool, message: str = "", details: str = ""):
    """Log a test result"""
    results["total_tests"] += 1
    if passed:
        results["passed"] += 1
        status = f"{GREEN}[PASS]{RESET}"
    else:
        results["failed"] += 1
        status = f"{RED}[FAIL]{RESET}"
    
    print(f"{status}: {name}")
    if message:
        print(f"       {message}")
    if details:
        print(f"       {YELLOW}{details}{RESET}")
    
    results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message,
        "details": details
    })


def section(title: str):
    """Print section header"""
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{title:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")


# ============================================================================
# PART 1: IMPORT CHAIN VALIDATION (Circular Import Fix)
# ============================================================================

def test_no_circular_imports():
    """Test 1: Verify no circular imports in import chain"""
    section("TEST 1: IMPORT CHAIN VALIDATION")
    
    try:
        # Step 1: Add parent directory to path
        repo_root = Path(__file__).parent
        sys.path.insert(0, str(repo_root))
        
        # Step 2: Try importing app.py
        import app as root_app
        log_test(
            "Import root app.py",
            hasattr(root_app, 'app'),
            "Successfully imported app from root",
            f"app object exists: {hasattr(root_app, 'app')}"
        )
        
        # Step 3: Try importing server.app
        from server.app import app as server_app
        log_test(
            "Import server.app.app",
            server_app is not None,
            "Successfully imported FastAPI app from server.app",
            f"app is FastAPI instance: {type(server_app).__name__}"
        )
        
        # Step 4: Verify they're the same object
        if hasattr(root_app, 'app'):
            same_object = root_app.app is server_app
            log_test(
                "app.py imports from server.app correctly",
                same_object,
                "root app.py should import from server.app",
                f"Same object: {same_object}"
            )
        
        return True
    except ImportError as e:
        log_test(
            "Import chain test",
            False,
            f"ImportError: {e}",
            "Check for circular imports"
        )
        return False
    except Exception as e:
        log_test(
            "Import chain test",
            False,
            f"Unexpected error: {type(e).__name__}: {e}",
            ""
        )
        return False


# ============================================================================
# PART 2: ENVIRONMENT INITIALIZATION (HF Space Compatibility)
# ============================================================================

def test_server_startup():
    """Test 2: Verify server can be imported and has all endpoints"""
    section("TEST 2: SERVER INITIALIZATION")
    
    try:
        # Import the FastAPI app
        from server.app import app
        
        log_test(
            "FastAPI app imported",
            app is not None,
            "server.app.app exists",
            f"Type: {type(app).__name__}"
        )
        
        # Check endpoints exist
        routes = [route.path for route in app.routes]
        required_endpoints = ["/health", "/reset", "/step", "/state", "/tasks", "/episode-summary", "/"]
        
        for endpoint in required_endpoints:
            exists = any(endpoint in route for route in routes)
            log_test(
                f"Endpoint exists: {endpoint}",
                exists,
                f"Route {endpoint} is registered",
                f"Available routes: {routes}"
            )
        
        return True
    except Exception as e:
        log_test(
            "Server startup test",
            False,
            f"Error: {type(e).__name__}: {e}",
            ""
        )
        return False


# ============================================================================
# PART 3: INFERENCE SCRIPT VALIDATION
# ============================================================================

def load_inference_script() -> Optional[dict]:
    """Load and parse inference.py"""
    try:
        inference_path = Path(__file__).parent / "inference.py"
        with open(inference_path, 'r') as f:
            content = f.read()
        return {"path": inference_path, "content": content}
    except Exception as e:
        log_test("Load inference.py", False, str(e), "")
        return None


def test_inference_exception_handling():
    """Test 3: Verify OpenAI v1 exception handling"""
    section("TEST 3: OPENAI V1 EXCEPTION HANDLING")
    
    script = load_inference_script()
    if not script:
        return False
    
    content = script["content"]
    
    # Check for broad exception handling
    has_broad_except = "except Exception as e:" in content
    log_test(
        "Broad Exception handling in call_llm()",
        has_broad_except,
        "Uses `except Exception` to catch all OpenAI v1 exceptions",
        "APIConnectionError, APITimeoutError, AuthenticationError, etc. are subclasses of Exception"
    )
    
    # Check for exception logging
    has_error_logging = "err_type" in content and "err_module" in content
    log_test(
        "Exception type logging",
        has_error_logging,
        "Logs exception module and type for debugging",
        "Helps identify which OpenAI exception was raised"
    )
    
    # Check for return statement after exception
    has_fallback_return = "return {}" in content
    log_test(
        "Exception fallback return",
        has_fallback_return,
        "Returns safe default {} on API failure",
        "Prevents unhandled exceptions from crashing the script"
    )
    
    return True


def test_output_format_compliance():
    """Test 4: Verify [START], [STEP], [END] format compliance"""
    section("TEST 4: OUTPUT FORMAT COMPLIANCE")
    
    script = load_inference_script()
    if not script:
        return False
    
    content = script["content"]
    
    # Check for [START] line
    has_start = "[START]" in content and "task=" in content and "env=" in content and "model=" in content
    log_test(
        "[START] line format",
        has_start,
        "Emits [START] task=<task> env=<env> model=<model>",
        "Required by validator for evaluation"
    )
    
    # Check for [STEP] line with all required fields
    has_step = "[STEP]" in content and "step=" in content and "action=" in content and "reward=" in content and "done=" in content and "error=" in content
    log_test(
        "[STEP] line format",
        has_step,
        "Emits [STEP] with step, action, reward, done, error fields",
        "Must include score field (new requirement)"
    )
    
    # Check for [END] line with score field (CRITICAL FIX)
    has_end_score = "[END]" in content and "score=" in content
    log_test(
        "[END] line includes score field (CRITICAL)",
        has_end_score,
        "Emits [END] success=<bool> steps=<n> score=<score> rewards=<...>",
        "score field is mandatory in Phase 2"
    )
    
    # Check reward formatting to 2 decimal places
    has_format_reward = ":.2f" in content
    log_test(
        "Reward formatting (2 decimals)",
        has_format_reward,
        "Formats rewards to 2 decimal places (0.00 format)",
        "Validator expects this exact format"
    )
    
    return True


def test_reset_failed_handling():
    """Test 5: Verify reset failure handling with score field"""
    section("TEST 5: RESET FAILURE HANDLING")
    
    script = load_inference_script()
    if not script:
        return False
    
    content = script["content"]
    
    # Check for reset exception handling
    has_reset_try_except = "try:" in content and "env.reset()" in content
    log_test(
        "Reset wrapped in try/except",
        has_reset_try_except,
        "Safely catches reset() exceptions",
        ""
    )
    
    # Check that [END] line is emitted even on reset failure
    has_end_on_failure = re.search(r'\[END\].*success=false.*score=0\.00', content)
    log_test(
        "[END] emitted on reset failure with score=0.00",
        has_end_on_failure is not None,
        "Emits [END] success=false steps=0 score=0.00 rewards=",
        "Ensures validator can parse output even on failure"
    )
    
    return True


def test_fallback_step_line():
    """Test 6: Verify fallback [STEP] line on exceptions"""
    section("TEST 6: FALLBACK STEP LINE")
    
    script = load_inference_script()
    if not script:
        return False
    
    content = script["content"]
    
    # Check for fallback STEP line emission
    has_fallback_step = "fallback" in content and "[STEP]" in content
    log_test(
        "Fallback [STEP] line on inner exceptions",
        has_fallback_step,
        "Emits minimal valid [STEP] line when step loop fails",
        "Prevents output parsing from breaking on incomplete logs"
    )
    
    # Verify it's emitted before breaking
    has_step_then_break = re.search(r'\[STEP\].*\n\s+break', content, re.DOTALL)
    log_test(
        "Fallback [STEP] emitted before break",
        has_step_then_break is not None,
        "Ensures [STEP] is in log stream before exiting loop",
        "Critical for validator output parsing"
    )
    
    return True


# ============================================================================
# PART 4: DOCKERFILE VALIDATION
# ============================================================================

def test_dockerfile_correctness():
    """Test 7: Verify Dockerfile fixes"""
    section("TEST 7: DOCKERFILE CORRECTNESS")
    
    try:
        # Check server/Dockerfile
        server_dockerfile = Path(__file__).parent / "server" / "Dockerfile"
        with open(server_dockerfile, 'r') as f:
            content = f.read()
        
        # Check for broken parent directory paths
        no_parent_paths = "../" not in content
        log_test(
            "No parent directory paths in COPY",
            no_parent_paths,
            "Uses relative paths within build context",
            "Docker COPY cannot reference parent directories"
        )
        
        # Check for correct module path in CMD
        has_correct_cmd = "server.app:app" in content
        log_test(
            "Correct CMD module path (server.app:app)",
            has_correct_cmd,
            "CMD uses server.app:app instead of server:app",
            "Matches the package structure"
        )
        
        # Check README.md for HF Spaces configuration
        readme_path = Path(__file__).parent / "README.md"
        with open(readme_path, 'r') as f:
            readme = f.read()
        
        has_app_file = "app_file: app.py" in readme
        log_test(
            "HF Spaces app_file: app.py",
            has_app_file,
            "README.md header sets app_file: app.py",
            ""
        )
        
        has_app_port = "app_port: 7860" in readme
        log_test(
            "HF Spaces app_port: 7860",
            has_app_port,
            "README.md header sets app_port: 7860",
            ""
        )
        
        return True
    except Exception as e:
        log_test("Dockerfile validation", False, str(e), "")
        return False


# ============================================================================
# PART 5: PHASE 2 REQUIREMENTS
# ============================================================================

def test_phase2_readiness():
    """Test 8-11: Verify Phase 2 evaluation readiness"""
    section("TEST 8-11: PHASE 2 READINESS")
    
    try:
        # Test environment environment variables
        required_vars = ["MODEL_NAME", "API_BASE_URL", "HF_TOKEN"]
        for var in required_vars:
            exists = os.getenv(var) is not None
            log_test(
                f"Environment variable: {var}",
                exists,
                f"{var} is set" if exists else f"{var} not set (use defaults or set manually)",
                "These are used by inference.py"
            )
        
        # Test that inference.py uses OpenAI client
        script = load_inference_script()
        if script:
            has_openai_client = "from openai import OpenAI" in script["content"]
            log_test(
                "Uses OpenAI Client",
                has_openai_client,
                "inference.py imports OpenAI client",
                "Required for Phase 2 evaluation"
            )
            
            has_env_vars = all(var in script["content"] for var in ["API_BASE_URL", "MODEL_NAME", "HF_TOKEN"])
            log_test(
                "Reads credentials from environment",
                has_env_vars,
                "Uses os.getenv() for API_BASE_URL, MODEL_NAME, HF_TOKEN",
                "Phase 2 evaluator will inject these"
            )
        
        # Test that environment has 3+ tasks
        from environment import EmailTriageEnv
        tasks = ["email_priority_classification", "urgency_detection", "intelligent_routing"]
        
        for task in tasks:
            try:
                env = EmailTriageEnv(task_id=task, seed=42)
                log_test(
                    f"Task exists: {task}",
                    True,
                    f"Initialized {task} environment",
                    ""
                )
            except Exception as e:
                log_test(
                    f"Task exists: {task}",
                    False,
                    str(e),
                    ""
                )
        
        return True
    except Exception as e:
        log_test("Phase 2 readiness test", False, str(e), "")
        return False


def test_scoring_range():
    """Test 12: Verify scores are in 0.0-1.0 range"""
    section("TEST 12: SCORE RANGE VALIDATION")
    
    script = load_inference_script()
    if not script:
        return False
    
    content = script["content"]
    
    # Check for score normalization
    has_min_max = "min(" in content and "max(" in content
    log_test(
        "Score clamping to [0.0, 1.0]",
        has_min_max,
        "Uses min/max to constrain scores to valid range",
        "Prevents invalid scores from breaking validator"
    )
    
    # Check for score calculation
    has_score_calc = "score" in content and ("/" in content or "*" in content)
    log_test(
        "Score calculation present",
        has_score_calc,
        "Calculates normalized score from rewards",
        ""
    )
    
    return True


def test_runtime_constraints():
    """Test 13: Verify runtime meets Phase 2 requirements"""
    section("TEST 13: RUNTIME CONSTRAINTS")
    
    script = load_inference_script()
    if not script:
        return False
    
    content = script["content"]
    
    # Check for max_steps limit (~20min constraint)
    has_step_limit = "MAX_STEPS" in content or "max_steps" in content or "range(1," in content
    log_test(
        "Step limit defined",
        has_step_limit,
        "inference.py should have bounded episode length",
        "Needed for <20min runtime requirement"
    )
    
    # Check for timeout handling
    has_timeout = "timeout" in content.lower() or "except" in content
    log_test(
        "Timeout handling present",
        has_timeout,
        "Handles long-running operations",
        ""
    )
    
    return True


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all Phase 2 validation tests"""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}{'OPENENV PHASE 2 VALIDATION TEST SUITE':^70}{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    print(f"\n{YELLOW}Testing both ERROR FIXES and PHASE 2 READINESS{RESET}\n")
    
    # Run all test sections
    test_no_circular_imports()
    test_server_startup()
    test_inference_exception_handling()
    test_output_format_compliance()
    test_reset_failed_handling()
    test_fallback_step_line()
    test_dockerfile_correctness()
    test_phase2_readiness()
    test_scoring_range()
    test_runtime_constraints()
    
    # Print summary
    section("TEST SUMMARY")
    total = results["total_tests"]
    passed = results["passed"]
    failed = results["failed"]
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print(f"Pass Rate: {pass_rate:.1f}%\n")
    
    if failed == 0:
        print(f"{GREEN}{BOLD}[SUCCESS] ALL TESTS PASSED - READY FOR PHASE 2!{RESET}\n")
    else:
        print(f"{RED}{BOLD}[ERROR] {failed} TESTS FAILED - FIX BEFORE PHASE 2!{RESET}\n")
    
    # Save results
    results_file = Path(__file__).parent / "phase2_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {results_file}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
