@echo off
REM Comprehensive API verification script for OpenEnv Email Triage

setlocal enabledelayedexpansion

set HF_SPACE=https://shusmitSarkar-openenv-email-triage.hf.space
set TESTS_PASSED=0
set TESTS_FAILED=0

echo.
echo =========================================
echo OpenEnv Email Triage - API Verification
echo =========================================
echo Space: %HF_SPACE%
echo.

REM Test 1: Health Check
echo [TEST 1/7] GET /health
curl -s -w "\n" "%HF_SPACE%/health"
if !errorlevel! equ 0 (set /a TESTS_PASSED+=1) else (set /a TESTS_FAILED+=1)
echo.

REM Test 2: Root Endpoint
echo [TEST 2/7] GET / ^(root endpoint^)
curl -s -w "\n" "%HF_SPACE%/"
if !errorlevel! equ 0 (set /a TESTS_PASSED+=1) else (set /a TESTS_FAILED+=1)
echo.

REM Test 3: Get Tasks
echo [TEST 3/7] GET /tasks ^(list all tasks^)
curl -s -w "\n" "%HF_SPACE%/tasks"
if !errorlevel! equ 0 (set /a TESTS_PASSED+=1) else (set /a TESTS_FAILED+=1)
echo.

REM Test 4: POST /reset with empty body
echo [TEST 4/7] POST /reset with empty JSON body
curl -s -X POST -H "Content-Type: application/json" -d "{}" -w "\n" "%HF_SPACE%/reset"
if !errorlevel! equ 0 (set /a TESTS_PASSED+=1) else (set /a TESTS_FAILED+=1)
echo.

REM Test 5: POST /reset with specific task
echo [TEST 5/7] POST /reset with task_id=urgency_detection
curl -s -X POST -H "Content-Type: application/json" -d "{}" -w "\n" "%HF_SPACE%/reset?task_id=urgency_detection"
if !errorlevel! equ 0 (set /a TESTS_PASSED+=1) else (set /a TESTS_FAILED+=1)
echo.

REM Test 6: POST /reset with seed
echo [TEST 6/7] POST /reset with seed=42
curl -s -X POST -H "Content-Type: application/json" -d "{}" -w "\n" "%HF_SPACE%/reset?task_id=email_priority_classification&seed=42"
if !errorlevel! equ 0 (set /a TESTS_PASSED+=1) else (set /a TESTS_FAILED+=1)
echo.

REM Test 7: POST /reset with intelligent_routing task
echo [TEST 7/7] POST /reset with task_id=intelligent_routing
curl -s -X POST -H "Content-Type: application/json" -d "{}" -w "\n" "%HF_SPACE%/reset?task_id=intelligent_routing"
if !errorlevel! equ 0 (set /a TESTS_PASSED+=1) else (set /a TESTS_FAILED+=1)
echo.

echo =========================================
echo Test Summary
echo =========================================
echo Tests Attempted: 7
echo Success Count: %TESTS_PASSED%
echo.
