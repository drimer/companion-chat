"""
End-to-end tests for the complete conversation flow.
These tests run against the full application stack with real OpenAI API calls.
"""

import asyncio
import os
import time
import uuid

import pytest
from fastapi import Request
from httpx import AsyncClient

from companionchat.dependencies import get_authenticated_sub
from companionchat.main import app


@pytest.fixture
async def async_client():
    """Create an async HTTP client for testing."""

    async def override_auth_sub(request: Request) -> str:
        return request.headers.get("x-test-sub", "sub-a")

    app.dependency_overrides[get_authenticated_sub] = override_auth_sub

    async with AsyncClient(
        app=app, base_url="http://test", headers={"x-test-sub": "sub-a"}
    ) as client:
        yield client

    app.dependency_overrides.pop(get_authenticated_sub, None)


@pytest.mark.e2e
@pytest.mark.skipif(
    os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "dummy",
    reason="E2E tests require real OpenAI API key - set OPENAI_API_KEY environment variable",
)
class TestFullConversationFlow:
    """End-to-end tests for the complete conversation experience."""

    async def test_complete_user_journey(self, async_client):
        """Test the complete user journey from conversation creation to chat."""

        # Step 1: Create a new conversation
        create_response = await async_client.post("/conversations")
        assert create_response.status_code == 201

        conversation_data = create_response.json()
        conversation_id = conversation_data["id"]
        assert conversation_data["system_prompt"]
        assert conversation_data["user_id"]
        assert conversation_data["created_at"]

        # Step 2: Retrieve the conversation to verify it exists
        get_response = await async_client.get(f"/conversations/{conversation_id}")
        assert get_response.status_code == 200

        retrieved_data = get_response.json()
        assert retrieved_data["id"] == conversation_id

        # Verify that a different user cannot access the conversation
        other_user_headers = {"x-test-sub": "sub-b"}
        forbidden_get = await async_client.get(
            f"/conversations/{conversation_id}", headers=other_user_headers
        )
        assert forbidden_get.status_code == 403

        # Step 3: Start a conversation with initial message
        initial_chat_request = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! I'm excited to practice Japanese with you. Can you introduce yourself in both Japanese and English?",
                }
            ]
        }

        chat_response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=initial_chat_request
        )
        assert chat_response.status_code == 200

        chat_data = chat_response.json()
        assert "message" in chat_data
        assert "usage" in chat_data
        assert len(chat_data["message"]) > 0

        ai_response = chat_data["message"]
        print(f"AI Response 1: {ai_response}")

        forbidden_chat = await async_client.post(
            f"/conversations/{conversation_id}/chat",
            json=initial_chat_request,
            headers=other_user_headers,
        )
        assert forbidden_chat.status_code == 403

        # Step 4: Continue the conversation with follow-up
        follow_up_request = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! I'm excited to practice Japanese with you. Can you introduce yourself in both Japanese and English?",
                },
                {"role": "assistant", "content": ai_response},
                {
                    "role": "user",
                    "content": "That's great! Can you teach me how to say 'Nice to meet you' in Japanese?",
                },
            ]
        }

        follow_up_response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=follow_up_request
        )
        assert follow_up_response.status_code == 200

        follow_up_data = follow_up_response.json()
        assert "message" in follow_up_data
        assert len(follow_up_data["message"]) > 0

        print(f"AI Response 2: {follow_up_data['message']}")

        # Step 5: Test conversation context is maintained
        context_request = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! I'm excited to practice Japanese with you. Can you introduce yourself in both Japanese and English?",
                },
                {"role": "assistant", "content": ai_response},
                {
                    "role": "user",
                    "content": "That's great! Can you teach me how to say 'Nice to meet you' in Japanese?",
                },
                {"role": "assistant", "content": follow_up_data["message"]},
                {
                    "role": "user",
                    "content": "Now can you help me with the pronunciation?",
                },
            ]
        }

        context_response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=context_request
        )
        assert context_response.status_code == 200

        context_data = context_response.json()
        assert "message" in context_data
        print(f"AI Response 3: {context_data['message']}")

        # Verify the AI maintains context and remembers previous exchanges
        assert len(context_data["message"]) > 0

    async def test_conversation_with_multiple_languages(self, async_client):
        """Test conversation mixing Japanese and English as intended."""

        # Create conversation
        create_response = await async_client.post("/conversations")
        assert create_response.status_code == 201
        conversation_id = create_response.json()["id"]

        # Test bilingual conversation
        bilingual_request = {
            "messages": [
                {
                    "role": "user",
                    "content": "こんにちは！英語を練習したいです。Hello! I want to practice English.",
                }
            ]
        }

        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=bilingual_request
        )
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        print(f"Bilingual Response: {data['message']}")

        # The response should acknowledge both languages
        response_text = data["message"].lower()
        # This is a heuristic check - the AI should respond appropriately to the bilingual input
        assert len(data["message"]) > 10  # Should be a substantial response

    async def test_error_handling_with_real_api(self, async_client):
        """Test error handling scenarios with real API."""

        # Test chat with non-existent conversation
        fake_id = str(uuid.uuid4())
        chat_request = {"messages": [{"role": "user", "content": "Hello"}]}

        response = await async_client.post(
            f"/conversations/{fake_id}/chat", json=chat_request
        )
        assert response.status_code == 404

    async def test_conversation_with_long_history(self, async_client):
        """Test conversation with longer message history."""

        # Create conversation
        create_response = await async_client.post("/conversations")
        assert create_response.status_code == 201
        conversation_id = create_response.json()["id"]

        # Build a longer conversation history
        conversation_history = [
            {
                "role": "user",
                "content": "Hello! Let's practice Japanese and English together.",
            },
            {
                "role": "assistant",
                "content": "Hello! こんにちは！I'm excited to practice with you. 一緒に頑張りましょう！",
            },
            {
                "role": "user",
                "content": "Great! Can you teach me some basic greetings in Japanese?",
            },
            {
                "role": "assistant",
                "content": "Of course! Here are some basic greetings: おはよう (ohayou) - good morning, こんにちは (konnichiwa) - hello/good afternoon, こんばんは (konbanwa) - good evening.",
            },
            {"role": "user", "content": "How do I say 'thank you' in Japanese?"},
            {
                "role": "assistant",
                "content": "You can say ありがとう (arigatou) for casual situations, or ありがとうございます (arigatou gozaimasu) for more formal situations.",
            },
            {
                "role": "user",
                "content": "Perfect! Now can you help me practice using these in a sentence?",
            },
        ]

        chat_request = {"messages": conversation_history}

        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=chat_request
        )
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "usage" in data
        print(f"Long conversation response: {data['message']}")

        # Should handle longer context appropriately
        assert len(data["message"]) > 0
        assert data["usage"]["total_tokens"] > 0


@pytest.mark.e2e
@pytest.mark.skipif(
    os.getenv("SKIP_PERFORMANCE_TESTS") == "true",
    reason="Performance tests skipped - set SKIP_PERFORMANCE_TESTS=false to run",
)
class TestPerformanceAndReliability:
    """Test performance and reliability aspects."""

    async def test_response_time(self, async_client):
        """Test that responses come within reasonable time."""

        # Create conversation
        create_response = await async_client.post("/conversations")
        assert create_response.status_code == 201
        conversation_id = create_response.json()["id"]

        # Measure response time for chat
        start_time = time.time()

        chat_request = {
            "messages": [{"role": "user", "content": "Hi! How are you today?"}]
        }

        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=chat_request
        )

        end_time = time.time()
        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 30.0  # Should respond within 30 seconds
        print(f"Response time: {response_time:.2f} seconds")

    async def test_concurrent_conversations(self, async_client):
        """Test handling multiple concurrent conversations."""

        # Create multiple conversations
        conversations = []
        for i in range(3):
            create_response = await async_client.post("/conversations")
            assert create_response.status_code == 201
            conversations.append(create_response.json()["id"])

        # Send concurrent chat requests
        chat_tasks = []
        for i, conversation_id in enumerate(conversations):
            chat_request = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Hello from conversation {i+1}! Can you respond with the number {i+1}?",
                    }
                ]
            }

            task = async_client.post(
                f"/conversations/{conversation_id}/chat", json=chat_request
            )
            chat_tasks.append(task)

        # Wait for all responses
        responses = await asyncio.gather(*chat_tasks)

        # Verify all succeeded
        for i, response in enumerate(responses):
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            print(f"Concurrent response {i+1}: {data['message'][:100]}...")


@pytest.mark.e2e
class TestHealthAndMonitoring:
    """Test health check and monitoring endpoints."""

    async def test_health_endpoint(self, async_client):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
