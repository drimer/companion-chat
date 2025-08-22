#!/usr/bin/env pwsh

param(
    [string]$ApiUrl = "https://uycxfk6mv4.execute-api.eu-west-2.amazonaws.com/dev"
)

# Set UTF-8 encoding for better Japanese character support
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'UTF8'

# Try to set console code page to UTF-8 (may not work on all systems)
try {
    chcp 65001 | Out-Null
} catch {
    Write-Host "Note: Could not set console to UTF-8. Japanese characters may not display correctly." -ForegroundColor Yellow
}

Write-Host "API Gateway Testing Script" -ForegroundColor Cyan
Write-Host "API Base URL: $ApiUrl" -ForegroundColor Gray

# 1. Create a conversation
Write-Host "`nCreating a new conversation..." -ForegroundColor Yellow

$headers = @{
    "Content-Type" = "application/json"
}

try {
    Write-Host "Attempting to create conversation (may take a moment due to Lambda cold start)..." -ForegroundColor Gray
    $response = Invoke-RestMethod -Uri "$ApiUrl/conversations" -Method POST -Headers $headers -TimeoutSec 30
    Write-Host "Conversation created successfully!" -ForegroundColor Green
    Write-Host "   ID: $($response.id)" -ForegroundColor Cyan
    Write-Host "   Title: $($response.title)" -ForegroundColor Cyan
    
    $conversationId = $response.id
} catch {
    Write-Host "Failed to create conversation" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Message -like "*timeout*" -or $_.Exception.Message -like "*504*") {
        Write-Host "This is likely due to Lambda cold start. Try running the script again." -ForegroundColor Yellow
    }
    exit 1
}

# Wait 3 seconds before next API call
Write-Host "Waiting 3 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# 2. Send a chat message
Write-Host "`nSending a chat message..." -ForegroundColor Yellow

$messages = @(
    @{
        role = "user"
        content = "Hello! Can you respond in Japanese?"
    }
)

$body = @{
    messages = $messages
} | ConvertTo-Json -Depth 3

try {
    $chatResponse = Invoke-RestMethod -Uri "$ApiUrl/conversations/$conversationId/chat" -Method POST -Headers $headers -Body $body
    Write-Host "Chat message sent successfully!" -ForegroundColor Green
    
    # The API returns 'message' field, not 'content'
    if ($chatResponse.message) {
        # Fix encoding issue - Windows PowerShell interprets UTF-8 as Latin1
        try {
            $latin1Bytes = [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetBytes($chatResponse.message)
            $properText = [System.Text.Encoding]::UTF8.GetString($latin1Bytes)
            Write-Host "Response: $properText" -ForegroundColor Green
        } catch {
            # Fallback to raw text if decoding fails
            Write-Host "Response (raw): $($chatResponse.message)" -ForegroundColor Yellow
        }
        
        Write-Host "Usage - Prompt tokens: $($chatResponse.usage.prompt_tokens), Completion tokens: $($chatResponse.usage.completion_tokens)" -ForegroundColor Gray
    } else {
        Write-Host "Warning: No message in response" -ForegroundColor Yellow
        Write-Host "Full Response: $($chatResponse | ConvertTo-Json -Depth 3)" -ForegroundColor Gray
    }
} catch {
    Write-Host "Failed to send chat message" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Wait 3 seconds before next API call
Write-Host "Waiting 3 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# 3. Get conversation details
Write-Host "`nGetting conversation details..." -ForegroundColor Yellow

try {
    $details = Invoke-RestMethod -Uri "$ApiUrl/conversations/$conversationId" -Method GET -Headers $headers
    Write-Host "Conversation details retrieved!" -ForegroundColor Green
    Write-Host "   Title: $($details.title)" -ForegroundColor Cyan
    Write-Host "   Messages: $($details.messages.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "Failed to get conversation details" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nAll tests completed!" -ForegroundColor Green
