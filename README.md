# Python Hackathon Backend – Optimized for rapid development and Feedback-Driven shipping (Mistral 2024, OpenAI 2025, DeepMind Medgemma 2025)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Maintainer](https://img.shields.io/badge/maintainer-@louisbrulenaudet-blue)](https://github.com/louisbrulenaudet)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Package Manager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

This repository is a FastAPI-based backend service optimized for rapid development and feedback-driven shipping during hackathons.

In order to run the backend the fastest way possible, you can use the makefile setup and uv for Python dependency management.

If the frontend team needs to run their application separately, the recommended and most secure approach is to clone this repository twice: once for production (e.g., with a `-prod` suffix) and once for development (e.g., with a `-dev` suffix). Keep the production backend on the `main` branch and the development backend on the appropriate development branches. Start the production backend using `make prod`, then share your IP address with the frontend team so they can connect to the backend.

You can get your IP address by running the following command:

```sh
ipconfig getifaddr en0
```

> **Warning:** Do not forget to disable your firewall or allow the port 8001 in your firewall settings to allow the frontend team to connect to your backend. Make commands are only available in unix-like systems (Linux, macOS). For Windows users, you can use the WSL (Windows Subsystem for Linux) to run these commands.

To ensure smooth development and minimize conflicts, it is recommended to implement each component in its own dedicated router and corresponding business logic files within the `core` directory. This modular approach enables you to test and develop components independently, reducing the risk of interfering with other parts of the application. Organizing your code in this way enhances maintainability, scalability, and clarity, making it easier to merge core features across branches and integrate them into different routers as the project evolves.

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

## Best Practices

- Always validate request/response data using Pydantic models before processing
- Always use DTO objects for data propagation during runtime
- Implement comprehensive error handling with meaningful error messages
- Use environment variables for configuration and secrets (never hardcode sensitive data)
- Always run `make check` and `make format` before committing
- Use Makefile for common tasks to ensure consistency across the team
- Follow RESTful API design principles
- Use utility decorators (`retry`, `async_retry`) for operations that may fail transiently
- Implement proper async/await patterns throughout the application
- Use dependency injection for testability and maintainability
- Document all public functions and classes with docstrings

- **Hackathon-specific:** Keep components modular and independent to enable parallel development and easy merging

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose for containerization and deployment.
- [uv](https://github.com/astral-sh/uv) (Python dependency manager)
- [ruff](https://docs.astral.sh/ruff/) (linter/formatter)

In order to run the backend the fastest way possible, you can use the makefile setup and uv for Python dependency management as this:

```sh
make init
make upgrade
make dev
```

Then you can ping the API at [http://127.0.0.1:8000/api/v1/ping](http://127.0.0.1:8000/api/v1/ping).

If you need to install packages such as transformers, you can do so with the following command:

```sh
uv add transformers
```

## Quick Start

### 1. Initialize the environment

```sh
make init
```

### 2. Start FastAPI server

The backend can be run in two modes: development and production. The development mode is intended for local development with hot-reloading, while the production mode is optimized for performance and stability. Here's how to start the development server:

```sh
make dev
```

- The API will be available at [http://localhost:8000](http://localhost:8000) by default with a ping endpoint at [http://localhost:8000/api/v1/ping](http://localhost:8000/api/v1/ping).

### 2.1 Start production server

Here's how to start the production server:

```sh
make prod
```

- The production server will run on port 8001 by default at [http://0.0.0.0:8001](http://0.0.0.0:8001) with a ping endpoint at [http://0.0.0.0:8001/api/v1/ping](http://0.0.0.0:8001/api/v1/ping).

## Code Quality

- Lint and check code:
  ```sh
  make check
  ```

- Format code:
  ```sh
  make format
  ```

## Citing this project

If you use this code in your research, please use the following BibTeX entry.

```BibTeX
@misc{louisbrulenaudet2025,
author = {Louis Brulé Naudet},
title = {Python Hackathon Backend – Optimized for rapid development and Feedback-Driven shipping (Mistral 2024, OpenAI 2025, DeepMind Medgemma 2025)},
howpublished = {\url{https://github.com/louisbrulenaudet/hackathon-backend}},
year = {2025}
}
```

---

## Feedback

If you have any feedback, please reach out at [louisbrulenaudet@icloud.com](mailto:louisbrulenaudet@icloud.com).
