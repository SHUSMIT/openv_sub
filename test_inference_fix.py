#!/usr/bin/env python3
"""
Test script to validate that inference.py handles errors gracefully
"""

import os
import sys
import subprocess
from pathlib import Path

def test_inference_runs_without_crash():
    """Test that inference.py runs and exits with code 0"""
    repo_dir = Path(__file__).parent
    
    # Set environment variables for testing
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "sk-test-fake-key-for-testing-only-1234567890"
    env["MODEL_NAME"] = "gpt-3.5-turbo"  # Smaller model to reduce processing
    
    print("=" * 70)
    print("TEST: Running inference.py with error handling")
    print("=" * 70)
    
    try:
        # Run the inference script
        result = subprocess.run(
            [sys.executable, str(repo_dir / "inference.py")],
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print("\nExit Code: {}".format(result.returncode))
        print("\nSTDOUT (last 1000 chars):\n{}".format(result.stdout[-1000:] if result.stdout else "(empty)"))
        print("\nSTDERR (last 500 chars):\n{}".format(result.stderr[-500:] if result.stderr else "(empty)"))
        
        # Check that it exited with code 0 (success, even if some tasks failed)
        if result.returncode == 0:
            print("\n[OK] SUCCESS: Script exited with code 0 (gracefully handled all errors)")
            return True
        else:
            print("\n[FAIL] FAILURE: Script exited with code {}".format(result.returncode))
            return False
            
    except subprocess.TimeoutExpired:
        print("\n[FAIL] FAILURE: Script timed out")
        return False
    except Exception as e:
        print("\n[FAIL] FAILURE: Exception occurred: {}: {}".format(type(e).__name__, e))
        return False


def test_imports_work():
    """Test that the module can be imported"""
    print("\n" + "=" * 70)
    print("TEST: Verifying module imports")
    print("=" * 70)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import inference
        print("[OK] inference.py imports successfully")
        
        # Check for key components
        if hasattr(inference, 'EmailTriageAgent'):
            print("[OK] EmailTriageAgent class found")
        if hasattr(inference, 'main'):
            print("[OK] main() function found")
        
        return True
    except Exception as e:
        print("[FAIL] Import failed: {}: {}".format(type(e).__name__, e))
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n[INFO] INFERENCE.PY FIX VALIDATION TEST SUITE")
    print("=" * 70)
    
    test1_pass = test_imports_work()
    test2_pass = test_inference_runs_without_crash()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("Test 1 - Module imports: {} PASS".format("[OK]" if test1_pass else "[FAIL]"))
    print("Test 2 - Graceful error handling: {} PASS".format("[OK]" if test2_pass else "[FAIL]"))
    
    if test1_pass and test2_pass:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n[WARNING] SOME TESTS FAILED")
        sys.exit(1)
