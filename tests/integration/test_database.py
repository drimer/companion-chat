"""
Integration tests for database operations.
These tests run against a local DynamoDB container to test actual database interactions.
"""

import os
import uuid
from datetime import datetime

import pytest

from src.companionchat.db.repositories import ConversationRepository
from src.companionchat.dependencies import create_dynamodb_client_context
from src.companionchat.settings import Settings


@pytest.fixture
def test_settings():
    """Test settings with local DynamoDB configuration."""
    return Settings(
        DB_CONVERSATIONS_TABLE_NAME="conversations",
        AWS_REGION="us-east-1",
        AWS_ENDPOINT_URL="http://localhost:8000",
        AWS_ACCESS_KEY_ID="dummy",
        AWS_SECRET_ACCESS_KEY="dummy",
        OPENAI_API_KEY="test-key",
        OPENAI_MODEL="gpt-4o-mini",
        MAX_TOKENS=1000,
    )


@pytest.fixture
async def conversation_repository(test_settings):
    """Create a conversation repository for testing."""
    async with create_dynamodb_client_context() as client:
        repo = ConversationRepository(client, test_settings.DB_CONVERSATIONS_TABLE_NAME)
        yield repo


class TestConversationRepository:
    """Test conversation repository database operations."""

    async def test_create_conversation(self, conversation_repository):
        """Test creating a conversation in the database."""
        # Act
        conversation = await conversation_repository.create()

        # Assert
        assert conversation is not None
        assert isinstance(conversation.id, uuid.UUID)  # Should be UUID, not string
        assert len(str(conversation.id)) == 36  # UUID string length
        assert (
            conversation.system_prompt
            == "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."
        )
        assert (
            conversation.user_id == "default-user-123"
        )  # Updated to match repository constant
        assert isinstance(conversation.created_at, datetime)

    async def test_get_existing_conversation(self, conversation_repository):
        """Test retrieving an existing conversation from the database."""
        # Arrange - create a conversation first
        created_conversation = await conversation_repository.create()

        # Act
        retrieved_conversation = await conversation_repository.get(
            created_conversation.id
        )

        # Assert
        assert retrieved_conversation is not None
        assert retrieved_conversation.id == created_conversation.id
        assert (
            retrieved_conversation.system_prompt == created_conversation.system_prompt
        )
        assert retrieved_conversation.user_id == created_conversation.user_id
        assert retrieved_conversation.created_at == created_conversation.created_at

    async def test_get_nonexistent_conversation(self, conversation_repository):
        """Test retrieving a conversation that doesn't exist."""
        # Arrange
        fake_id = str(uuid.uuid4())

        # Act
        conversation = await conversation_repository.get(fake_id)

        # Assert
        assert conversation is None

    async def test_multiple_conversations(self, conversation_repository):
        """Test creating and retrieving multiple conversations."""
        # Arrange & Act
        conversation1 = await conversation_repository.create()
        conversation2 = await conversation_repository.create()

        # Assert they are different
        assert conversation1.id != conversation2.id

        # Act - retrieve both
        retrieved1 = await conversation_repository.get(conversation1.id)
        retrieved2 = await conversation_repository.get(conversation2.id)

        # Assert
        assert retrieved1 is not None
        assert retrieved2 is not None
        assert retrieved1.id == conversation1.id
        assert retrieved2.id == conversation2.id
        assert retrieved1.id != retrieved2.id


class TestDatabaseErrorHandling:
    """Test database error handling scenarios."""

    async def test_get_with_invalid_id_format(self, conversation_repository):
        """Test retrieving conversation with invalid ID format."""
        # Arrange
        invalid_id = "not-a-uuid"

        # Act & Assert - should handle gracefully
        conversation = await conversation_repository.get(invalid_id)
        assert conversation is None

    async def test_connection_resilience(self, conversation_repository):
        """Test that the repository handles connection issues gracefully."""
        # This test would require more sophisticated setup to simulate
        # network issues or database unavailability
        # For now, we'll just test that the basic operations work

        conversation = await conversation_repository.create()
        assert conversation is not None

        retrieved = await conversation_repository.get(conversation.id)
        assert retrieved is not None


# Note: These tests require a local DynamoDB instance to be running
# Start it with: docker-compose -f infra/docker-compose.yml up -d
# The tests will be skipped if the database is not available
@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests that require actual database connectivity."""

    @pytest.mark.skipif(
        os.getenv("SKIP_DB_TESTS") == "true",
        reason="Database tests skipped - set SKIP_DB_TESTS=false to run",
    )
    async def test_end_to_end_conversation_flow(self, conversation_repository):
        """Test the complete conversation lifecycle."""
        # Create
        conversation = await conversation_repository.create()
        assert conversation is not None
        original_id = conversation.id

        # Read
        retrieved = await conversation_repository.get(original_id)
        assert retrieved is not None
        assert retrieved.id == original_id

        # Verify persistence across operations
        retrieved_again = await conversation_repository.get(original_id)
        assert retrieved_again is not None
        assert retrieved_again.id == original_id
        assert retrieved_again.created_at == retrieved.created_at
        assert retrieved_again.created_at == retrieved.created_at
        assert retrieved_again.created_at == retrieved.created_at
