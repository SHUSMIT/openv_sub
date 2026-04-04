@echo off
REM Advanced API tests - /step endpoint and full episode workflow

setlocal enabledelayedexpansion

set HF_SPACE=https://shusmitSarkar-openenv-email-triage.hf.space

echo.
echo =========================================
echo Advanced API Tests - Episode Workflow
echo =========================================
echo.

REM Test 8: Full episode workflow with /step
echo [TEST 8/7] Full episode workflow (reset + step + step + state)
echo Step 1: Reset environment
curl -s -X POST -H "Content-Type: application/json" -d "{}" "%HF_SPACE%/reset?task_id=email_priority_classification&seed=42" > reset_response.json

REM Extract state for next step
echo Step 2: Execute first action
curl -s -X POST -H "Content-Type: application/json" -d "{\"classify_priority\":{\"priority\":\"high\",\"confidence\":0.9,\"reasoning\":\"Urgent issue\"}}" "%HF_SPACE%/step?task_id=email_priority_classification" > step1_response.json

REM Show results
echo Step 3: Get current state
curl -s "%HF_SPACE%/state?task_id=email_priority_classification" > state_response.json

echo Reset response:
type reset_response.json | find "status"
echo.
echo Step 1 response:
type step1_response.json | find "reward"
echo.
echo State response:
type state_response.json | find "step_count"
echo.

REM Test 9: /state endpoint
echo [TEST 9/? ] GET /state endpoint with different tasks
echo State for email_priority_classification:
curl -s "%HF_SPACE%/state?task_id=email_priority_classification" | find "task_id"
echo.

echo State for urgency_detection:
curl -s "%HF_SPACE%/state?task_id=urgency_detection" | find "task_id"
echo.

echo State for intelligent_routing:
curl -s "%HF_SPACE%/state?task_id=intelligent_routing" | find "task_id"
echo.

REM Test 10: Episode summary
echo [TEST 10/? ] GET /episode-summary
echo Episode summary:
curl -s "%HF_SPACE%/episode-summary?task_id=email_priority_classification"
echo.

echo =========================================
echo Cleanup
echo =========================================
del reset_response.json step1_response.json state_response.json 2>nul
echo Test files cleaned up
echo.
