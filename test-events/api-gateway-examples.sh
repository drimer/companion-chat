#!/bin/bash
# Bash script for testing the API through API Gateway
# Usage: bash test-events/api-gateway-examples.sh

set -e  # Exit on any error

echo "🚀 Testing Companion Chat API via API Gateway"
echo "================================================"

# Base URL
BASE_URL="https://uycxfk6mv4.execute-api.eu-west-2.amazonaws.com/dev"

# 1. Create a new conversation
echo ""
echo "📝 Creating a new conversation..."
response=$(curl -s -X POST "$BASE_URL/conversations" \
  -H "Content-Type: application/json" \
  -d '{}')

if [ $? -eq 0 ]; then
    echo "✅ Conversation created successfully!"
    conversation_id=$(echo $response | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    echo "   ID: $conversation_id"
    echo "   Response: $response"
else
    echo "❌ Failed to create conversation"
    exit 1
fi

# 2. Send a chat message
echo ""
echo "💬 Sending a chat message..."
chat_response=$(curl -s -X POST "$BASE_URL/conversations/$conversation_id/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hi, how are you? daijoubu desu ka?"
      },
      {
        "role": "assistant", 
        "content": "Hi! I'\''m doing well, thank you! And yes, daijoubu desu. How about you? 何か話したいことがありますか？"
      },
      {
        "role": "user",
        "content": "それは何でしたか。わたしは分かりません"
      },
      {
        "role": "assistant",
        "content": "ごめんなさい！もっと簡単に言いますね。私は「どうですか？」と聞きたかったのです。あなたは元気ですか？"
      },
      {
        "role": "user",
        "content": "はい、元気です。好きな色は何ですか？"
      }
    ]
  }')

if [ $? -eq 0 ]; then
    echo "✅ Chat message sent successfully!"
    echo "   AI Response: $chat_response"
else
    echo "❌ Failed to send chat message"
    echo "   💡 Tip: Check if OpenAI API key is configured in Lambda environment variables"
fi

echo ""
echo "🎉 API testing completed!"
