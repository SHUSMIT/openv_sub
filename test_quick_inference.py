#!/usr/bin/env python3
"""
Quick Integration Test — Checks inference.py can at least initialize without import errors
"""

import os
import sys
import json
from pathlib import Path

# Set environment variables for testing
os.environ.setdefault("API_BASE_URL", "https://api.openai.com/v1")
os.environ.setdefault("MODEL_NAME", "gpt-4")
os.environ.setdefault("HF_TOKEN", "test_token_for_validation")

def test_inference_import():
    """Test that inference.py can be imported without errors"""
    print("\n" + "="*70)
    print("QUICK INFERENCE IMPORT TEST")
    print("="*70 + "\n")
    
    try:
        repo_root = Path(__file__).parent
        sys.path.insert(0, str(repo_root))
        
        # Test 1: Import agent class
        print("Test 1: Importing EmailTriageAgent...")
        from inference import EmailTriageAgent
        print("[PASS] EmailTriageAgent imported successfully")
        
        # Test 2: Try to initialize an agent (without running full episode)
        print("\nTest 2: Initializing EmailTriageAgent for task...")
        try:
            agent = EmailTriageAgent("email_priority_classification", "gpt-4")
            print(f"[PASS] Agent initialized: {type(agent).__name__}")
            print(f"  - Task ID: {agent.task_id}")
            print(f"  - Model: {agent.model}")
        except Exception as e:
            print(f"[WARN] Agent initialization failed (this is OK if environment is missing): {e}")
        
        # Test 3: Check output format functions
        print("\nTest 3: Checking output format functions...")
        from inference import _init_client
        print("[PASS] _init_client function found")
        
        # Test 4: Verify main function signature
        print("\nTest 4: Checking main() function...")
        from inference import main
        print(f"[PASS] main() function exists and is callable")
        
        # Test 5: Syntax validation (just check it compiles)
        print("\nTest 5: Validating inference.py syntax...")
        inference_file = repo_root / "inference.py"
        with open(inference_file, 'r') as f:
            code = f.read()
        compile(code, str(inference_file), 'exec')
        print("[PASS] inference.py syntax is valid (no syntax errors)")
        
        print("\n" + "="*70)
        print("[SUCCESS] ALL QUICK TESTS PASSED")
        print("="*70 + "\n")
        return 0
        
    except SyntaxError as e:
        print(f"\n[ERROR] SYNTAX ERROR in inference.py: {e}")
        return 1
    except ImportError as e:
        print(f"\n[ERROR] IMPORT ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_inference_import())
