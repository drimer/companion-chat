# API Usage Guide

## Create a Conversation

```bash
curl -X POST "http://localhost:4000/conversations" \
  -H "Content-Type: application/json"
```

**Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "system_prompt": "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak.",
  "user_id": "test-user-001",
  "created_at": "2025-08-15T10:30:00Z"
}
```

## Chat with OpenAI

```bash
curl -X POST "http://localhost:4000/conversations/{conversation_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello! I want to practice Japanese with you."
      }
    ]
  }'
```

**Response**:
```json
{
  "message": "Hello! こんにちは！I'm excited to practice English with you while helping you learn Japanese. 一緒に頑張りましょう！How should we start?",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 32,
    "total_tokens": 77
  }
}
```

## Get Conversation Metadata

```bash
curl "http://localhost:4000/conversations/{conversation_id}"
```

## Production API Testing

For testing the deployed AWS API Gateway:

### Windows (PowerShell)
```powershell
# Run the PowerShell testing script
powershell.exe -File "test-events/api-gateway-examples.ps1"
```

### Linux/macOS/WSL (Bash)
```bash
# Run the bash testing script
bash test-events/api-gateway-examples.sh
```

Both scripts will:
1. Create a new conversation
2. Send a chat message requesting Japanese response
3. Display the properly decoded Japanese text
4. Show token usage statistics
