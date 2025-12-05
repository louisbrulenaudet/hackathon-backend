# Hackathon Backend Agent Instructions

## Project Overview

This repository is a FastAPI-based backend service optimized for rapid development and feedback-driven shipping during hackathons.

## Tech Stack

- **Language:** Python 3.12+ (strict type hints)
- **Framework:** FastAPI (async web framework)
- **Validation:** Pydantic v2 (data validation and settings management)
- **HTTP Client:** httpx (async HTTP client)
- **Caching:** aiocache (async caching)
- **Formatting/Linting:** Ruff (fast Python linter and formatter)
- **Package Manager:** uv (fast Python package installer and resolver)
- **Build Tools:** Docker, Docker Compose
- **Automation:** Makefile
- **Environment:** python-dotenv (.env)
- **Testing:** pytest, pytest-asyncio, pytest-cov

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── base.py          # Health check endpoints (ping, health)
│   │       └── router.py            # API router configuration
│   ├── core/
│   │   └── config.py                # Application settings and configuration
│   ├── dtos/
│   │   └── models.py                # Pydantic DTOs for request/response validation
│   ├── enums/
│   │   └── error_codes.py           # Centralized error code definitions
│   ├── exceptions/
│   │   ├── core_exception.py        # Base exception class with structured error handling
│   │   └── client_initialization_error.py  # Client initialization error
│   ├── utils/
│   │   └── decorators.py            # Utility decorators (retry, async_retry)
│   └── main.py                      # FastAPI application entry point with middleware
├── make/
│   ├── dev.mk                       # Development commands
│   ├── docker.mk                    # Docker-related commands
│   ├── help.mk                      # Help command implementation
│   └── variables.mk                 # Makefile variables
├── tests/                           # Test suite
├── pyproject.toml                    # Project configuration, dependencies, and tool settings
├── compose.yaml                     # Docker Compose configuration
├── Dockerfile                       # Docker image definition
├── Makefile                         # Main Makefile with command shortcuts
└── requirements.txt                 # Python dependencies (generated from pyproject.toml)
```

## Environment Configuration

### Required Environment Variables

The application uses Pydantic Settings for configuration management. Required environment variables (defined in `app/core/config.py`):

- `APP_NAME` (default: "Backend") - Application name
- `API_KEY` - API key for authentication
- `API_CLIENT` - API client identifier

### Setup Instructions

1. **Install dependencies:**

   ```sh
   make init
   ```

2. **Configure environment:**

   Copy `.env.template` to `.env` and fill in required variables:

   ```
   APP_NAME=Hackathon Backend
   API_KEY=your_api_key_here
   API_CLIENT=your_client_id_here
   ```

3. **Development:**

   ```sh
   make dev
   ```

   - The API will be available at [http://localhost:8000](http://localhost:8000)
   - Ping endpoint: [http://localhost:8000/api/v1/ping](http://localhost:8000/api/v1/ping)

4. **Production:**

   ```sh
   make prod
   ```

   - Production server runs on port 8001 by default at [http://0.0.0.0:8001](http://0.0.0.0:8001)
   - Ping endpoint: [http://0.0.0.0:8001/api/v1/ping](http://0.0.0.0:8001/api/v1/ping)

## Common Commands

The following Makefile commands are available for development, formatting, testing, and deployment:

### Development Commands

| Command                | Description                                 |
|------------------------|---------------------------------------------|
| `make dev`             | Run development server with hot reloading   |
| `make prod`            | Run production server on port 8001          |
| `make test`            | Run the test suite with coverage            |
| `make init`            | Initialize development environment          |
| `make install-dev`     | Install development dependencies            |
| `make upgrade`         | Update project dependencies                 |
| `make check`           | Run code quality checks (Ruff linting)      |
| `make format`          | Format the codebase using Ruff              |
| `make pre-commit`      | Run pre-commit checks on all files          |

### Docker Commands

| Command                | Description                                  |
|------------------------|----------------------------------------------|
| `make build`           | Create application containers                |
| `make rebuild`         | Rebuild containers with fresh configuration  |
| `make start`           | Launch application services                  |
| `make stop`            | Stop all running services                    |
| `make restart`         | Restart all application services             |
| `make logs`            | Display container logs                       |
| `make clean`           | Remove all containers and volumes            |
| `make run-dev`         | Start development server with live reload    |
| `make check-docker`    | Verify Docker installation and configuration |

## Middleware Stack

The application uses a comprehensive middleware stack for security, performance, and functionality:

### Security Middleware

- **CORS:** Configurable cross-origin resource sharing (allows all origins in hackathon mode - **do not use in production**)
- **Error Handling:** Global exception handler for structured error responses

### Performance Middleware

- **GZip Compression:** Response compression for better performance (minimum size: 1000 bytes)
- **Async Support:** Full async/await support throughout the application

### Error Handling

- **Global Exception Handler:** Centralized error handling with logging
- **Structured Error Responses:** JSON-safe error representation for API responses
- **HTTP Status Code Mapping:** Automatic mapping of exceptions to appropriate status codes

## Error Handling

This application implements a comprehensive error handling strategy using a custom `CoreError` base class for centralized error management. All errors follow a structured approach with proper logging, serialization, and HTTP status code mapping.

### CoreError Foundation

All errors must be instances of `CoreError` or its subclasses. The `CoreError` class provides:

- **Structured Error Codes:** Unique symbolic codes for error identification (defined in `app/enums/error_codes.py`)
- **Contextual Details:** Optional metadata for debugging and monitoring
- **Automatic Logging:** Built-in structured logging with error context
- **Serialization:** JSON-safe error representation for API responses via `to_dict()` method
- **Type Safety:** Full type hints for error attributes

### Error Classification

#### Application-Specific Errors

Errors unique to this application are defined in `app/exceptions/` directory:

```python
# In app/exceptions/client_initialization_error.py
from app.enums import ErrorCodes
from app.exceptions.core_exception import CoreError

class ClientInitializationError(CoreError):
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The client initialization failed.",
            ErrorCodes.CLIENT_INITIALIZATION_ERROR,
            details=str(details),
        )
```

#### Available Error Types

- `ClientInitializationError` - Raised when client initialization fails

### Error Code Management

Error codes are centrally managed in `app/enums/error_codes.py`:

```python
class ErrorCodes(enum.StrEnum):
    CLIENT_INITIALIZATION_ERROR = "CLIENT_INITIALIZATION_ERROR"
```

### Exception Handler

The global exception handler in `app/main.py` maps specific exceptions to HTTP status codes:

```python
@app.exception_handler(CoreError)
async def error_handler(_: Request, exc: CoreError) -> JSONResponse:
    status_codes = {
        "TaskNotFoundError": 404,
        "TaskInitalizationError": 500,
    }
    status_code = status_codes.get(exc.__class__.__name__, 400)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "code": exc.code,
            "details": exc.details or {},
        },
    )
```

## Request Validation with Pydantic

The API uses Pydantic v2 models for type-safe request and response validation. This approach provides automatic validation, type inference, and error handling.

### Implementation Pattern

```python
from pydantic import BaseModel, Field
from fastapi import APIRouter

# Define response model
class PingResponse(BaseModel):
    status: str = Field(default="ok", description="The status of the health check.")
    uptime: int = Field(default=0, description="The uptime of the service in seconds.")
    timestamp: int = Field(default=0, description="The current timestamp.")

# Use in route
@router.get("/ping", response_model=PingResponse)
async def ping() -> PingResponse:
    return PingResponse(
        status="ok",
        uptime=uptime,
        timestamp=now,
    )
```

### DTO Pattern

All data transfer objects are defined in `app/dtos/models.py`:

- `PingResponse` - Health check response

## Utility Decorators

The application provides utility decorators for common patterns in `app/utils/decorators.py`:

### Retry Decorator

```python
from app.utils.decorators import retry

@retry(max_retries=3, sleep_time=1, raises_on_exception=True)
def fetch_data():
    # Function that may fail
    pass
```

### Async Retry Decorator

```python
from app.utils.decorators import async_retry

@async_retry(max_retries=3, sleep_time=1, raises_on_exception=True)
async def async_fetch_data():
    # Async function that may fail
    pass
```

## Coding Conventions

- Use **strict Python 3.12+** with comprehensive type hints
- **Variables:** Use `snake_case` for all variables and functions (e.g., `account_id`, `get_account()`)
- **Classes:** Use `PascalCase` for class names (e.g., `CoreError`, `PingResponse`)
- **Constants:** Use `UPPER_SNAKE_CASE` for constants (e.g., `API_KEY`, `MAX_RETRIES`)
- **Enums:** Enum names in `PascalCase`, enum members in `UPPER_SNAKE_CASE` (e.g., `class ErrorCodes(enum.StrEnum): CLIENT_INITIALIZATION_ERROR = "CLIENT_INITIALIZATION_ERROR"`)
- All API endpoints must use **Pydantic models** for request/response validation
- Use **CoreError** subclasses for structured error handling with appropriate status codes
- **Formatting:** Enforced by Ruff (double quotes, spaces, line length 88)
- **Type hints:** Required for all function parameters and return types
- **Route organization:** Keep route handlers modular and focused on single responsibilities
- **Modular development:** Implement each component in its own dedicated router and corresponding business logic files within the `core` directory

## Best Practices

- Always validate request/response data using Pydantic models before processing
- Always use DTO objects for data propagation during runtime
- Use proper HTTP status codes for different error scenarios (400 for validation errors, 404 for not found, 500 for server errors)
- Implement comprehensive error handling with meaningful error messages
- Use environment variables for configuration and secrets (never hardcode sensitive data)
- Always run `make check` and `make format` before committing
- Use Makefile for common tasks to ensure consistency across the team
- Follow RESTful API design principles
- Use utility decorators (`retry`, `async_retry`) for operations that may fail transiently
- Implement proper async/await patterns throughout the application
- Use dependency injection for testability and maintainability
- Document all public functions and classes with docstrings
- Write tests for all business logic and API endpoints

- **Hackathon-specific:** Keep components modular and independent to enable parallel development and easy merging

## API Endpoints

### Health Check Endpoints

- **GET `/api/v1/ping`**
  - Health check endpoint with status, uptime, and timestamp
  - Response: `PingResponse` model

- **GET `/api/v1/health`**
  - Lightweight healthcheck for Docker/K8s
  - Returns: `{"status": "ok"}`

## Contribution

- Follow all coding conventions and rules
- Ensure all changes pass `make check`, `make format`, and `make test`
- Update this documentation when adding new endpoints or functionality
- Use proper error handling and status codes
- Validate all request/response data with Pydantic models
- Follow RESTful API design principles
- Implement proper type hints for all functions
- Write tests for new features
- Use utility decorators for retry logic when appropriate
- Keep components modular and independent for hackathon development
- **Security Note:** The CORS middleware currently allows all origins for hackathon convenience. This should be restricted in production environments.
