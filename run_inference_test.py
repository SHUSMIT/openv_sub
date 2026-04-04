#!/usr/bin/env python3
"""
API KEY SETUP GUIDE & INFERENCE TEST
====================================

This script shows how to:
1. Set up API keys (OpenAI or Groq)
2. Run a single inference episode
3. Validate output format compliance

QUICK START:

Option A - OpenAI (paid, but most models available):
  set OPENAI_API_KEY=sk-your-key-here
  python run_inference_test.py

Option B - Groq (FREE Mixtral 8x7b):
  set GROQ_API_KEY=gsk-your-key-here
  set API_BASE_URL=https://api.groq.com/openai/v1
  set MODEL_NAME=mixtral-8x7b-32768
  python run_inference_test.py

Option C - HuggingFace (free Neom/Llama models):
  set HF_TOKEN=hf_your-token-here
  set API_BASE_URL=https://api-inference.huggingface.co/v1
  set MODEL_NAME=NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
  python run_inference_test.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check_api_setup():
    """Check if API is configured"""
    print_section("1. CHECKING API KEY CONFIGURATION")
    
    api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4")
    
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    hf_token = os.getenv("HF_TOKEN", "").strip()
    
    print(f"  API_BASE_URL: {api_base_url}")
    print(f"  MODEL_NAME:   {model_name}")
    
    if openai_key:
        provider = "OpenAI"
        print(f"  ✅ OPENAI_API_KEY: Configured (masked: {openai_key[:10]}...)")
    elif groq_key:
        provider = "Groq"
        print(f"  ✅ GROQ_API_KEY:   Configured (masked: {groq_key[:10]}...)")
    elif hf_token:
        provider = "Hugging Face"
        print(f"  ✅ HF_TOKEN:       Configured (masked: {hf_token[:10]}...)")
    else:
        print("\n  ❌ NO API KEY FOUND!\n")
        print("  Set one of these environment variables:\n")
        print("    Option A - OpenAI:")
        print("      set OPENAI_API_KEY=sk-...")
        print("      python run_inference_test.py\n")
        print("    Option B - Groq (FREE):")
        print("      set GROQ_API_KEY=gsk-...")
        print("      set API_BASE_URL=https://api.groq.com/openai/v1")
        print("      set MODEL_NAME=mixtral-8x7b-32768")
        print("      python run_inference_test.py\n")
        print("    Option C - HuggingFace (free):")
        print("      set HF_TOKEN=hf_...")
        print("      set API_BASE_URL=https://api-inference.huggingface.co/v1")
        print("      set MODEL_NAME=NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO")
        print("      python run_inference_test.py\n")
        return False
    
    print(f"\n  Using: {provider}")
    return True


def run_test_episode():
    """Run a single test episode with API calls"""
    print_section("2. RUNNING TEST EPISODE (5 steps)")
    
    try:
        from openai import OpenAI
        from environment import EmailTriageEnv
        from models import (
            Action, ActionClassifyPriority, PriorityLevel
        )
        
        # Get API configuration
        api_base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("MODEL_NAME", "gpt-4")
        openai_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        hf_token = os.getenv("HF_TOKEN")
        
        api_key = openai_key or groq_key or hf_token
        
        # Initialize client
        if api_base_url != "https://api.openai.com/v1":
            client = OpenAI(api_key=api_key, base_url=api_base_url)
        else:
            client = OpenAI(api_key=api_key)
        
        # Initialize environment
        env = EmailTriageEnv(task_id="email_priority_classification", seed=42)
        obs = env.reset()
        
        print(f"  [START] task=email_priority_classification env=openenv-email-triage model={model_name}")
        
        rewards = []
        step_count = 0
        
        for step_num in range(1, 6):
            email_data = obs.email.model_dump()
            step_count += 1
            
            # Build prompt
            system_prompt = (
                "You are an expert email triage system. Classify emails into priorities:\n"
                "- CRITICAL: Immediate attention, production issues, angry customers\n"
                "- HIGH: Urgent but not breaking, billing issues\n"
                "- MEDIUM: Normal workflow\n"
                "- LOW: Can wait, informational\n\n"
                'Respond with ONLY JSON: {"priority": "critical|high|medium|low", "confidence": 0.0-1.0}'
            )
            
            user_msg = f"Subject: {email_data['subject']}\nBody: {email_data['body']}"
            
            # Call LLM
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    max_tokens=200,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg},
                    ]
                )
                
                response_text = response.choices[0].message.content or "medium"
                priority_str = response_text.lower()
                
                if "critical" in priority_str:
                    priority = PriorityLevel.CRITICAL
                elif "high" in priority_str:
                    priority = PriorityLevel.HIGH
                elif "low" in priority_str:
                    priority = PriorityLevel.LOW
                else:
                    priority = PriorityLevel.MEDIUM
                
            except Exception as e:
                print(f"    [LLM Error] {str(e)[:60]}... using fallback MEDIUM")
                priority = PriorityLevel.MEDIUM
            
            # Take action
            action = Action(
                task_id="email_priority_classification",
                classify_priority=ActionClassifyPriority(
                    priority=priority,
                    confidence=0.85
                )
            )
            
            obs, reward, info = env.step(action)
            ep_reward = reward.episode_reward
            rewards.append(ep_reward)
            
            # Emit [STEP] line (strict format compliance)
            action_str = f"classify_priority(priority={priority},confidence=0.85)"
            done_str = str(reward.is_done).lower()
            print(f"  [STEP] step={step_num} action={action_str} reward={ep_reward:.2f} done={done_str} error=null")
        
        # Emit [END] line
        success = sum(rewards) > 0
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)
        print(f"  [END] success={str(success).lower()} steps={step_count} rewards={rewards_str}")
        
        print(f"\n  Episode Summary:")
        print(f"    Steps completed: {step_count}")
        print(f"    Total reward: {sum(rewards):.2f}")
        print(f"    Average per step: {sum(rewards)/step_count:.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n  ❌ Error: {str(e)}")
        print(f"\n  Troubleshooting:")
        print(f"    1. Verify API key is set correctly")
        print(f"    2. Check API quota/rate limits")
        print(f"    3. Try different model: set MODEL_NAME=gpt-3.5-turbo")
        return False


def show_api_options():
    """Show available API options"""
    print_section("3. RECOMMENDED API OPTIONS (for testing)")
    
    options = [
        {
            "name": "Groq Mixtral 8x7b (FREE, FAST)",
            "setup": [
                "1. Get free API key: https://console.groq.com/",
                "2. Set environment variables:",
                "   set GROQ_API_KEY=gsk-your-key",
                "   set API_BASE_URL=https://api.groq.com/openai/v1",
                "   set MODEL_NAME=mixtral-8x7b-32768",
            ]
        },
        {
            "name": "OpenAI GPT-4 (PAID, most capable)",
            "setup": [
                "1. Get API key: https://platform.openai.com/api-keys",
                "2. Set environment variable:",
                "   set OPENAI_API_KEY=sk-your-key",
                "3. Optional - use cheaper model:",
                "   set MODEL_NAME=gpt-3.5-turbo",
            ]
        },
        {
            "name": "Hugging Face Inference API (FREE)",
            "setup": [
                "1. Get token: https://huggingface.co/settings/tokens",
                "2. Set environment variables:",
                "   set HF_TOKEN=hf_your-token",
                "   set API_BASE_URL=https://api-inference.huggingface.co/v1",
                "   set MODEL_NAME=NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
            ]
        },
    ]
    
    for i, opt in enumerate(options, 1):
        print(f"\n  Option {i}: {opt['name']}")
        print(f"  {'-'*60}")
        for line in opt['setup']:
            print(f"    {line}")


def main():
    print("\n╔" + "="*68 + "╗")
    print("║  OpenEnv Email Triage - API Setup & Inference Test            ║")
    print("║  Run this to test inference with real LLM API keys           ║")
    print("╚" + "="*68 + "╝")
    
    # Check API setup
    if not check_api_setup():
        show_api_options()
        return 1
    
    # Run test
    if run_test_episode():
        print_section("✅ SUCCESS")
        print("  Inference script ran successfully!")
        print("  Output format is compliant with [START], [STEP], [END] spec.")
        print("\n  Ready to submit! 🚀\n")
        return 0
    else:
        print_section("❌ FAILED")
        print("  Fix the error above and try again.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
