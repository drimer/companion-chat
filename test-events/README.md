# Lambda Test Events

This directory contains test events for the Lambda function that can be used in the AWS Console.

## Usage

1. Open AWS Lambda Console
2. Navigate to the `companion-chat-dev-chat-conversations-lambda` function
3. Go to the "Test" tab
4. Click "Create new event"
5. Copy the content from one of the JSON files below
6. Paste it into the event payload
7. Give it a descriptive name
8. Save and test

## Available Test Events

### 1. `create-conversation.json`
Creates a new conversation.
- **Endpoint**: `POST /conversations`
- **Purpose**: Test conversation creation
- **Expected Response**: New conversation with generated UUID

### 2. `send-message.json`
Sends a chat message to an existing conversation.
- **Endpoint**: `POST /conversations/{id}/chat`
- **Purpose**: Test chat functionality with multi-turn conversation
- **Expected Response**: AI response to the last user message
- **Note**: Update the conversation ID in the path to match an existing conversation

## Updating Test Events

After any deployment, simply copy these events back into the Lambda console test interface. The files are version-controlled so they persist across deployments.

## Real API Gateway Testing

For more realistic testing, you can also use these events with API Gateway test functionality, or convert them to actual HTTP requests using tools like Postman or curl.
