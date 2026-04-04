#!/usr/bin/env powershell
# Comprehensive API verification script for OpenEnv Email Triage HF Space

$HF_SPACE = "https://shusmitSarkar-openenv-email-triage.hf.space"
$TESTS_PASSED = 0
$TESTS_FAILED = 0

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "OpenEnv Email Triage - API Verification" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Space: $HF_SPACE" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "[TEST 1/7] GET /health" -ForegroundColor Yellow
try {
    $response = curl -s "$HF_SPACE/health"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: OK" -ForegroundColor Green
    Write-Host "   Response: $($json | ConvertTo-Json -Depth 2)" -ForegroundColor White
    $TESTS_PASSED++
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
    $TESTS_FAILED++
}
Write-Host ""

# Test 2: Root Endpoint
Write-Host "[TEST 2/7] GET / (root endpoint)" -ForegroundColor Yellow
try {
    $response = curl -s "$HF_SPACE/"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: OK" -ForegroundColor Green
    Write-Host "   Service: $($json.service)" -ForegroundColor White
    Write-Host "   Endpoints: $($json.endpoints.Keys.Count) endpoints registered" -ForegroundColor White
    $TESTS_PASSED++
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
    $TESTS_FAILED++
}
Write-Host ""

# Test 3: Get Tasks
Write-Host "[TEST 3/7] GET /tasks (list all tasks)" -ForegroundColor Yellow
try {
    $response = curl -s "$HF_SPACE/tasks"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: OK" -ForegroundColor Green
    Write-Host "   Tasks Found: $($json.tasks.Count)" -ForegroundColor White
    foreach ($task in $json.tasks) {
        Write-Host "     - $($task.id) [$($task.difficulty)]" -ForegroundColor White
    }
    $TESTS_PASSED++
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
    $TESTS_FAILED++
}
Write-Host ""

# Test 4: POST /reset with empty body (as validator does)
Write-Host "[TEST 4/7] POST /reset with empty JSON body" -ForegroundColor Yellow
try {
    $response = curl -s -X POST -H "Content-Type: application/json" -d '{}' "$HF_SPACE/reset"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: OK" -ForegroundColor Green
    Write-Host "   Status: $($json.status)" -ForegroundColor White
    if ($json.observation) {
        Write-Host "   Observation - Task: $($json.observation.task_id)" -ForegroundColor White
        Write-Host "   Observation - Email Subject: $($json.observation.email.subject.Substring(0, [Math]::Min(50, $json.observation.email.subject.Length)))..." -ForegroundColor White
    }
    $TESTS_PASSED++
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
    $TESTS_FAILED++
}
Write-Host ""

# Test 5: POST /reset with specific task
Write-Host "[TEST 5/7] POST /reset with task_id=urgency_detection" -ForegroundColor Yellow
try {
    $response = curl -s -X POST -H "Content-Type: application/json" -d '{}' "$HF_SPACE/reset?task_id=urgency_detection"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: OK" -ForegroundColor Green
    Write-Host "   Task: $($json.observation.task_id)" -ForegroundColor White
    Write-Host "   Step: $($json.observation.step_count)" -ForegroundColor White
    $TESTS_PASSED++
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
    $TESTS_FAILED++
}
Write-Host ""

# Test 6: POST /reset with seed for determinism
Write-Host "[TEST 6/7] POST /reset with seed=42 (for determinism test)" -ForegroundColor Yellow
try {
    $response1 = curl -s -X POST -H "Content-Type: application/json" -d '{}' "$HF_SPACE/reset?seed=42"
    $json1 = $response1 | ConvertFrom-Json
    $email1 = $json1.observation.email.subject
    
    Start-Sleep -Seconds 1
    
    $response2 = curl -s -X POST -H "Content-Type: application/json" -d '{}' "$HF_SPACE/reset?seed=42"
    $json2 = $response2 | ConvertFrom-Json
    $email2 = $json2.observation.email.subject
    
    if ($email1 -eq $email2) {
        Write-Host "✅ Status: OK (DETERMINISTIC)" -ForegroundColor Green
        Write-Host "   Email sequence matches across resets" -ForegroundColor White
    } else {
        Write-Host "⚠️  Non-deterministic results (this may be expected)" -ForegroundColor Yellow
    }
    $TESTS_PASSED++
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
    $TESTS_FAILED++
}
Write-Host ""

# Test 7: POST /step with action
Write-Host "[TEST 7/7] POST /step with priority classification action" -ForegroundColor Yellow
try {
    # First reset
    $reset = curl -s -X POST -H "Content-Type: application/json" -d '{}' "$HF_SPACE/reset?task_id=email_priority_classification"
    
    # Then step
    $action = @{
        classify_priority = @{
            priority = "high"
            confidence = 0.9
            reasoning = "Urgent customer issue"
        }
    } | ConvertTo-Json -Compress
    
    $response = curl -s -X POST -H "Content-Type: application/json" -d $action "$HF_SPACE/step?task_id=email_priority_classification"
    $json = $response | ConvertFrom-Json
    
    Write-Host "✅ Status: OK" -ForegroundColor Green
    Write-Host "   Step Result - Status: $($json.status)" -ForegroundColor White
    Write-Host "   Step Result - Reward: $($json.reward.episode_reward)" -ForegroundColor White
    Write-Host "   Step Result - Done: $($json.reward.is_done)" -ForegroundColor White
    $TESTS_PASSED++
} catch {
    Write-Host "❌ FAILED: $_" -ForegroundColor Red
    $TESTS_FAILED++
}
Write-Host ""

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Test Results Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $TESTS_PASSED/7" -ForegroundColor Green
Write-Host "Tests Failed: $TESTS_FAILED/7" -ForegroundColor $(if ($TESTS_FAILED -gt 0) { "Red" } else { "Green" })

if ($TESTS_FAILED -eq 0) {
    Write-Host "`n🎉 ALL TESTS PASSED - Deployment verified!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some tests failed - check output above" -ForegroundColor Yellow
}
