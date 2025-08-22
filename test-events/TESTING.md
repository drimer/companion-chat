# Cross-Platform API Testing

This guide helps you test the Companion Chat API regardless of your operating system.

## Quick Test (Choose Your Platform)

### 🐧 Linux / 🍎 macOS / 🪟 WSL
```bash
bash test-events/api-gateway-examples.sh
```

### 🪟 Windows (PowerShell)
```powershell
.\test-events\api-gateway-examples.ps1
```

### 🌐 Any Platform (Manual cURL)
```bash
# 1. Create conversation
curl -X POST https://uycxfk6mv4.execute-api.eu-west-2.amazonaws.com/dev/conversations -H "Content-Type: application/json" -d '{}'

# 2. Send message (replace CONVERSATION_ID)
curl -X POST https://uycxfk6mv4.execute-api.eu-west-2.amazonaws.com/dev/conversations/CONVERSATION_ID/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```

## What These Tests Do

1. **Create a new conversation** - Tests the conversation creation endpoint
2. **Send a chat message** - Tests the chat functionality with a multi-turn conversation
3. **Display results** - Shows the API responses in a readable format

## Expected Results

✅ **Successful test should show:**
- A new conversation ID
- An AI response to the chat message
- No error messages

❌ **Common issues:**
- **401 Error**: OpenAI API key not configured in Lambda
- **404 Error**: Incorrect API Gateway URL or conversation ID
- **Timeout**: Lambda function timeout (check CloudWatch logs)

## Files in this directory

- `api-gateway-examples.sh` - Bash script for Unix-like systems
- `api-gateway-examples.ps1` - PowerShell script for Windows
- `create-conversation.json` - Lambda test event for AWS Console
- `send-message.json` - Lambda test event for AWS Console
- `README.md` - Detailed testing guide
