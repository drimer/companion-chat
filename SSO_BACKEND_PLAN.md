# Implementation notes to have in consideration

Ideally, there should be an authorization service that checks all incoming requests against the resources attached to them.
For example, an attempt from user A to retrieve information about a conversation C that was created by user B should ideally
go through authz service that checks whether that is allowed, and if not, the request shouldn't even reach the API endpoint
to get the conversation.

However, as this is all a proof of concept, I want to abstain from creating another lambda.

Having said this, please write code that is easily moveable to a new authz lambda. The less coupled to existing code, the better, obviously,
but also create new Python modules and please all logic related to authz (authorization) physically separate (files, folders, etc).

# Backend Ownership Enforcement Checklist

- [x] Ensure API Gateway proxy methods remain (ANY /, ANY /{proxy+}) and attach a Cognito user-pool authorizer named `CompanionChatAuthorizer` that forwards claims in the Lambda event context.
- [x] Provide a dependency `get_authenticated_sub` in `companionchat.dependencies` that reads the `sub` claim from the API Gateway event context, raising `HTTPException(status_code=401)` when it is absent; support local runs via FastAPI dependency overrides.
- [x] Expand DynamoDB: add table `users` (partition key `sub`) and a GSI `user_id-index` on the existing `conversations` table with partition key `user_id` to query conversations by owner.
- [x] Implement `UserRepository` in `companionchat.db.repositories` with methods `get_by_sub(sub: str)` and `upsert_from_claims(claims: dict)` to store Cognito details (email, phone).
- [x] Update `ConversationRepository.create` signature to `create(owner_sub: str) -> Conversation` and persist the supplied owner string; add method `list_for_user(owner_sub: str) -> list[Conversation]` leveraging the new GSI.
- [x] Add method `enforce_ownership(conversation: Conversation, owner_sub: str)` in `ConversationRepository` (or a service wrapper) that raises `PermissionError` when the conversation owner differs.
- [x] Update FastAPI router functions (`create_conversation`, `get_conversation`, `chat_with_conversation`) to depend on `get_authenticated_sub`, pass the value to repository methods, and translate `PermissionError` into `HTTPException(status_code=403)`.
- [x] Write unit tests in [tests/unit/test_repositories.py](tests/unit/test_repositories.py) for `ConversationRepository.create`, `list_for_user`, and `enforce_ownership`, using fake Dynamo responses for matching/mismatching `sub`.
- [x] Add integration tests in [tests/integration/test_api_endpoints.py](tests/integration/test_api_endpoints.py) that mock API Gateway context to simulate different `sub` values, ensuring 403 for cross-user access.
- [x] Extend e2e flow in [tests/e2e/test_full_conversation_flow.py](tests/e2e/test_full_conversation_flow.py) to create two users (e.g., `sub_a`, `sub_b`), confirming API Gateway rejects unauthorized access when the authorizer forwards claims.
- [ ] Update [docs/api-usage.md](docs/api-usage.md) and [docs/development.md](docs/development.md) with the requirement to pass access tokens, describe the `CompanionChatAuthorizer`, and document the DynamoDB schema updates.
- [ ] Modify infrastructure scripts (e.g., [infra/aws/modules/conversations-lambda](infra/aws/modules/conversations-lambda)) to provision the `users` table, and the `user_id-index` before deploying code changes.

# Infrastructure

The Cognito instance has been created manually, and needs to be written in Terraform.
As the backend make end up having hardcoded references to it, think about how the Github action for deployment will put both together.

