# Backend Ownership Enforcement Checklist

- [ ] Ensure API Gateway proxy methods remain (ANY /, ANY /{proxy+}) and attach a Cognito user-pool authorizer named `CompanionChatAuthorizer` that forwards claims in the Lambda event context.
- [ ] Add lightweight token verification behind FastAPI using a helper module `companionchat.auth.jwt_verifier` with function `verify_access_token(token: str) -> dict` that caches JWKS and returns decoded claims.
- [ ] Create a dependency `get_authenticated_sub` in `companionchat.dependencies` that reads the `sub` claim from the API Gateway event context or from `verify_access_token`, raising `HTTPException(status_code=401)` if missing.
- [ ] Expand DynamoDB: add table `users` (partition key `sub`) and a GSI `user_id-index` on the existing `conversations` table with partition key `user_id` to query conversations by owner.
- [ ] Implement `UserRepository` in `companionchat.db.repositories` with methods `get_by_sub(sub: str)` and `upsert_from_claims(claims: dict)` to store Cognito details (email, phone).
- [ ] Update `ConversationRepository.create` signature to `create(owner_sub: str) -> Conversation` and persist the supplied owner string; add method `list_for_user(owner_sub: str) -> list[Conversation]` leveraging the new GSI.
- [ ] Add method `enforce_ownership(conversation: Conversation, owner_sub: str)` in `ConversationRepository` (or a service wrapper) that raises `PermissionError` when the conversation owner differs.
- [ ] Update FastAPI router functions (`create_conversation`, `get_conversation`, `chat_with_conversation`) to depend on `get_authenticated_sub`, pass the value to repository methods, and translate `PermissionError` into `HTTPException(status_code=403)`.
- [ ] Write unit tests in [tests/unit/test_repositories.py](tests/unit/test_repositories.py) for `ConversationRepository.create`, `list_for_user`, and `enforce_ownership`, using fake Dynamo responses for matching/mismatching `sub`.
- [ ] Add integration tests in [tests/integration/test_api_endpoints.py](tests/integration/test_api_endpoints.py) that mock API Gateway context to simulate different `sub` values, ensuring 403 for cross-user access.
- [ ] Extend e2e flow in [tests/e2e/test_full_conversation_flow.py](tests/e2e/test_full_conversation_flow.py) to create two users (e.g., `sub_a`, `sub_b`), confirming API Gateway rejects unauthorized access when the authorizer forwards claims.
- [ ] Update [docs/api-usage.md](docs/api-usage.md) and [docs/development.md](docs/development.md) with the requirement to pass access tokens, describe the `CompanionChatAuthorizer`, and document the DynamoDB schema updates.
- [ ] Modify infrastructure scripts (e.g., [infra/aws/modules/conversations-lambda](infra/aws/modules/conversations-lambda)) to provision `CompanionChatAuthorizer`, the `users` table, and the `user_id-index` before deploying code changes.

# Infrastructure

The Cognito instance has been created manually, and needs to be written in Terraform.
As the backend make end up having hardcoded references to it, think about how the Github action for deployment will put both together.