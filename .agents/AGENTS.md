# FastAPI Project Architecture Rules

This repository follows Clean Architecture, SOLID principles, and enterprise software engineering best practices for any FastAPI development.

## General Rules

* Use Python 3.12+
* Use FastAPI
* Use Pydantic v2
* Use SQLAlchemy 2.x ORM
* Use Alembic for database migrations
* Use asynchronous programming (`async`/`await`) whenever appropriate.
* Use dependency injection provided by FastAPI.
* Follow RESTful API design.
* Return consistent API responses.
* Use proper HTTP status codes.
* Write readable, maintainable code.
* Never place business logic inside API routes.

---

## Project Structure

Always organise the project as follows:

```text
app/
│
├── main.py
│
├── api/
│   ├── deps.py
│   └── v1/
│       ├── api.py
│       └── endpoints/
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   └── exceptions.py
│
├── db/
│   ├── database.py
│   ├── session.py
│   └── base.py
│
├── models/
│
├── schemas/
│
├── repositories/
│
├── services/
│
├── middleware/
│
├── utils/
│
├── constants/
│
├── common/
│
├── tests/
│
└── migrations/
```

---

## Layer Responsibilities

### API Layer
Responsible only for:
* receiving HTTP requests
* validating request body
* calling Service layer
* returning HTTP response

Never perform:
* SQL
* database operations
* business calculations
* authentication logic
* external API calls

### Service Layer
Contains all business logic.
Responsibilities include:
* validation
* business rules
* workflows
* transactions
* calling repositories
* calling external services
* Services should not know anything about HTTP requests.

### Repository Layer
Responsible only for database access.
Responsibilities:
* CRUD
* queries
* joins
* pagination
* filtering
* Repositories must never contain business rules.

### Model Layer
Contains SQLAlchemy ORM models only. Do not place validation logic here.

### Schema Layer
Contains Pydantic models. Separate schemas into:
* Create
* Update
* Response
* List Response
* Search Request

### Core Layer
Contains:
* configuration
* JWT
* password hashing
* logging
* exception handlers
* security
* application settings

### Middleware
Contains:
* authentication middleware
* logging middleware
* request ID
* audit middleware

### Utils
Contains reusable helper functions only. No business logic.

---

## Coding Standards
* Use type hints.
* Use async functions.
* Use dependency injection.
* Separate interfaces from implementation where appropriate.
* Avoid duplicated code.
* Write small focused methods.
* Use meaningful variable names.

---

## API Standards
Every endpoint must:
* have summary
* have description
* specify response model
* return proper status codes
* raise HTTPException only in API layer when appropriate

---

## Error Handling
Use:
* custom exception classes
* global exception handlers
* consistent error response format:
```json
{
    "success": false,
    "code": "USER_NOT_FOUND",
    "message": "User does not exist",
    "timestamp": "...",
    "path": "/api/v1/users/5"
}
```

---

## Authentication
* Use JWT Access Token, Refresh Token, OAuth2PasswordBearer.
* Use password hashing with bcrypt or Argon2.
* Authentication logic belongs in `core/security.py`.

---

## Database
* Use SQLAlchemy ORM, AsyncSession, Alembic, and Repository pattern.
* Never execute SQL inside API routes.

---

## Logging
* Structured logging with request ID, execution time, errors, warnings, and auth events.
* Never log passwords or sensitive information.

---

## Validation
* Validate using Pydantic.
* Do not manually validate request objects inside routes.

---

## Response Format
Unless otherwise specified, every API should return:
```json
{
    "success": true,
    "message": "...",
    "data": {},
    "timestamp": "...",
    "requestId": "..."
}
```

---

## Documentation
* Include summary, description, request/response examples using FastAPI's OpenAPI features.

---

## Testing
* Generate tests for services, repositories, and API endpoints using pytest.

---

## Forbidden Practices
* Put SQL or business logic inside routers.
* Access the database directly from routes.
* Duplicate validation logic.
* Use global mutable state.
* Hardcode configuration values or secrets.
* Return raw SQLAlchemy models to clients.
* Mix ORM models with API response schemas.

---

## Code Generation Rule
Whenever generating new features:
1. Create ORM model.
2. Create Pydantic schemas.
3. Create repository.
4. Create service.
5. Create API router.
6. Register router in `api.py`.
7. Add dependency injection.
8. Add validation.
9. Add logging.
10. Add tests.
