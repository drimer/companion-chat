# API Testing Guide

This directory contains test events and examples for testing the companion chat API across different environments.

## Quick Start

### Option 1: API Gateway (Production-like testing)
Test the deployed API through API Gateway - **recommended for end-to-end testing**.

#### Linux/macOS/WSL (Bash)
```bash
# Run the bash script directly
bash test-events/api-gateway-examples.sh
```

#### Windows (PowerShell)
```powershell
# Run the PowerShell script
powershell.exe -File "test-events/api-gateway-examples.ps1"

# Or run manually:
# 1. Create a conversation
$conversation = Invoke-RestMethod -Uri "https://uycxfk6mv4.execute-api.eu-west-2.amazonaws.com/dev/conversations" -Method POST -ContentType "application/json" -Body "{}"
Write-Host "Created conversation: $($conversation.id)"

# 2. Send a chat message
$body = '{"messages":[{"role":"user","content":"Hi, how are you?"}]}'
Invoke-RestMethod -Uri "https://uycxfk6mv4.execute-api.eu-west-2.amazonaws.com/dev/conversations/$($conversation.id)/chat" -Method POST -ContentType "application/json" -Body $body
```

### Option 2: Lambda Console (AWS Console testing)
Test the Lambda function directly in the AWS Console using pre-built test events.

1. Open AWS Lambda Console
2. Navigate to the `companion-chat-dev-chat-conversations-lambda` function
3. Go to the "Test" tab
4. Use the test events from the JSON files below

## Available Test Resources

### 1. `api-gateway-examples.sh`
Bash script for testing via API Gateway
- **Platform**: Linux/macOS/WSL
- **Usage**: `bash test-events/api-gateway-examples.sh`
- **Purpose**: End-to-end API testing through API Gateway

### 2. `api-gateway-examples.ps1`
PowerShell script for testing via API Gateway
- **Platform**: Windows/PowerShell
- **Usage**: `powershell.exe -File "test-events/api-gateway-examples.ps1"`
- **Purpose**: End-to-end API testing through API Gateway with UTF-8 support
- **Features**: Handles Lambda cold starts, displays Japanese responses correctly

### 3. PowerShell Commands (manual testing)
PowerShell commands for testing via API Gateway
- **Platform**: Windows
- **Usage**: Copy/paste commands into PowerShell
- **Purpose**: End-to-end API testing through API Gateway

### 3. `create-conversation.json`
Lambda test event for creating conversations
- **Platform**: AWS Console
- **Usage**: Copy into Lambda test interface
- **Endpoint**: `POST /conversations`

### 4. `send-message.json`
Lambda test event for sending chat messages
- **Platform**: AWS Console  
- **Usage**: Copy into Lambda test interface
- **Endpoint**: `POST /conversations/{id}/chat`

## Testing Workflow

### Full End-to-End Test
1. **Create a conversation** using your platform's method
2. **Copy the conversation ID** from the response
3. **Send a chat message** using the conversation ID
4. **Verify the AI response**

### Platform-Specific Instructions

#### For Linux/macOS/WSL Users
- Use `api-gateway-examples.sh` for automated testing
- Modify the script to update conversation IDs as needed

#### For Windows Users  
- Use PowerShell commands from Quick Start section
- The `$conversation.id` variable automatically carries the ID between commands

#### For AWS Console Users
- Use the JSON test events for direct Lambda testing
- Update conversation IDs manually in the test events

## Notes

- **API Gateway URL**: Update the URL in scripts when deploying to different environments
- **OpenAI API Key**: Ensure the Lambda has a valid OpenAI API key configured
- **CORS**: API Gateway is configured to allow cross-origin requests
- **Error Handling**: Check Lambda logs in CloudWatch for detailed error information

## Troubleshooting

### Common Issues
- **401 Unauthorized**: Check OpenAI API key in Lambda environment variables
- **404 Not Found**: Verify the API Gateway URL and conversation ID
- **Timeout**: Check Lambda function timeout settings (default: 30s)
- **Line Ending Issues (WSL)**: Run `dos2unix test-events/api-gateway-examples.sh` if needed
