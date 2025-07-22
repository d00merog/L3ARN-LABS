# L3ARN-LABS
ᴛʜᴇ ꜰᴜᴛᴜʀᴇ ᴡᴀɪᴛꜱ ꜰᴏʀ ɴᴏ ᴏɴᴇ. ʟᴇᴠᴇʟ ᴜᴘ ʏᴏᴜʀ ꜱᴋɪʟʟꜱ ɴᴏᴡ. ᴊᴏɪɴ ᴏᴜʀ ʟᴇᴀʀɴɪɴɢ ʜᴜʙ 🍎
| ʙʀɪɴɢɪɴɢ ᴛʜᴇ ʟᴀʏᴇʀ 3 ᴏꜰ ᴇᴅᴜᴄᴀᴛɪᴏɴ

![351919820-309d5534-f15a-4872-a854-f3fbd5f28e1c](https://github.com/user-attachments/assets/8b673575-b861-42f7-8b9e-a6a145ec24b1)


## Overview

L3ARN-LABS is an open source initiative building an AI driven learning platform. The repository is split into a `backend` using **FastAPI** and a `frontend` powered by **Next.js** and Material UI.

### Features
- AI‑powered course recommendations and analytics
- Web3 authentication via wallet signatures
- Modular APIs for courses, lessons and notifications

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Copy `.env.example` to `.env` and update the variables

### Backend
```bash
python3 -m pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Architecture
```
┌──────────────┐       ┌────────────────────┐       ┌──────────────┐
│    Client    │ <---> │  Next.js Frontend   │ <---> │ FastAPI APIs │
└──────────────┘       └────────────────────┘       └──────────────┘
                                                │
                                                └─> Database
```
- Backend modules live in `backend/api` and `backend/core`.
- Frontend pages live under `frontend/src/pages`.
- Configuration is managed via `.env`.

## Contributing
1. Fork the repo and create a feature branch.
2. Commit your changes with descriptive messages.
3. Run `pytest` (currently there are no automated tests yet).
4. Open a Pull Request describing your contribution.

We welcome improvements to documentation, tests and features!

## License

Licensed under the [Apache 2.0](LICENSE) license.
=======
## Secrets management

Application secrets are no longer stored in a local `.env` file. Configure a self-hosted HashiCorp Vault and provide `VAULT_ADDR` and `VAULT_TOKEN` environment variables (or Docker secrets) when running the application. Secrets are looked up from Vault at `l3arn-labs/<SECRET_NAME>` and fallback to values in `/run/secrets/<SECRET_NAME>` or environment variables.

## Pre-commit hooks

This repository uses [pre-commit](https://pre-commit.com/) with `detect-secrets` to scan for secrets before every commit.

Install the hooks after cloning:

```bash
pip install pre-commit
pre-commit install
```

## Quick Start with Docker Compose

This project is fully containerized and can be run with Docker Compose.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/l3arn-labs.git
    cd l3arn-labs
    ```

2.  **Create a `.env` file from the example:**
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your secrets, or use the default values for local development.

3.  **Run the application:**
    ```bash
    docker-compose up --build
    ```
    The backend will be running at `http://localhost:8000` and the frontend at `http://localhost:3000`.

## Secrets Management

Application secrets are managed by HashiCorp Vault. The `docker-compose.yml` file includes a Vault service for local development.

When running the application with Docker Compose, the backend will automatically connect to the local Vault service.

For production deployments, you will need to provide the `VAULT_ADDR` and `VAULT_TOKEN` environment variables (or Docker secrets) to the backend service.

## API Map

The backend API is a FastAPI application with the following endpoints:

*   **Auth** (`/api/v1/auth`)
    *   `POST /token`: Authenticate a user and receive a JWT token.
        *   **Request Body:** `username`, `password`
        *   **Response:** `access_token`, `token_type`
*   **Users** (`/api/v1/users`)
    *   `GET /me`: Get the profile of the currently authenticated user.
    *   `PUT /me`: Update the profile of the currently authenticated user.
*   **Courses** (`/api/v1/courses`)
    *   `GET /`: Get a list of all available courses.
    *   `POST /`: Create a new course (instructors only).
    *   `GET /{course_id}`: Get the details of a specific course.
    *   `PUT /{course_id}`: Update a course (instructors only).
    *   `DELETE /{course_id}`: Delete a course (instructors only).
*   **Lessons** (`/api/v1/lessons`)
    *   `GET /courses/{course_id}/lessons`: Get a list of all lessons for a course.
    *   `POST /courses/{course_id}/lessons`: Create a new lesson for a course (instructors only).
    *   `GET /{lesson_id}`: Get the details of a specific lesson.
    *   `PUT /{lesson_id}`: Update a lesson (instructors only).
    *   `DELETE /{lesson_id}`: Delete a lesson (instructors only).

## How to Contribute

We welcome contributions to L3ARN-LABS! Please follow these guidelines to ensure a smooth development process.

### Setting up a Development Environment

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** to your local machine.
3.  **Create a new branch** for your feature or bug fix.
4.  **Install the pre-commit hooks:**
    ```bash
    pip install pre-commit
    pre-commit install
    ```

### Making Changes

1.  **Make your changes** to the codebase.
2.  **Write tests** for your changes. This project currently lacks a test suite, so we encourage you to add tests for any new features or bug fixes you introduce.
3.  **Run the tests** to ensure that your changes don't break anything.
4.  **Format your code** using `black` for Python and `prettier` for TypeScript/JavaScript.

### Submitting a Pull Request

1.  **Push your changes** to your fork on GitHub.
2.  **Create a pull request** from your fork to the `main` branch of the original repository.
3.  **Provide a clear and descriptive title and description** for your pull request.
4.  **Request a review** from one of the project maintainers.
