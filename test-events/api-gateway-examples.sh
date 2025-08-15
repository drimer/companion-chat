# Example curl commands for testing the API through API Gateway

# 1. Create a new conversation
curl -X POST https://your-api-gateway-url/conversations \
  -H "Content-Type: application/json" \
  -d '{}'

# 2. Send a chat message (replace {conversation-id} with actual ID)
curl -X POST https://your-api-gateway-url/conversations/{conversation-id}/chat \
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
  }'
