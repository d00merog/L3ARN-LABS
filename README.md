# L3ARN-LABS
ᴛʜᴇ ꜰᴜᴛᴜʀᴇ ᴡᴀɪᴛꜱ ꜰᴏʀ ɴᴏ ᴏɴᴇ. ʟᴇᴠᴇʟ ᴜᴘ ʏᴏᴜʀ ꜱᴋɪʟʟꜱ ɴᴏᴡ. ᴊᴏɪɴ ᴏᴜʀ ʟᴇᴀʀɴɪɴɢ ʜᴜʙ 🍎 | ʙʀɪɴɢɪɴɢ ᴛʜᴇ ʟᴀʏᴇʀ 3 ᴏꜰ ᴇᴅᴜᴄᴀᴛɪᴏɴ

![351919820-309d5534-f15a-4872-a854-f3fbd5f28e1c](https://github.com/user-attachments/assets/8b673575-b861-42f7-8b9e-a6a145ec24b1)

## Secrets management

Application secrets are no longer stored in a local `.env` file. Configure a self-hosted HashiCorp Vault and provide `VAULT_ADDR` and `VAULT_TOKEN` environment variables (or Docker secrets) when running the application. Secrets are looked up from Vault at `l3arn-labs/<SECRET_NAME>` and fallback to values in `/run/secrets/<SECRET_NAME>` or environment variables.

## Pre-commit hooks

This repository uses [pre-commit](https://pre-commit.com/) with `detect-secrets` to scan for secrets before every commit.

Install the hooks after cloning:

```bash
pip install pre-commit
pre-commit install
```

## Quick Start

This project consists of a Python backend and a TypeScript frontend.

### Backend

The backend is a FastAPI application.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the development server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

### Frontend

The frontend is a Next.js application.

**Note:** The frontend setup is unusual as it is missing a `package.json` file. The following instructions are based on a standard Next.js project and may need to be adapted.

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.

## How to Contribute

We welcome contributions to L3ARN-LABS! Please follow these guidelines to ensure a smooth development process.

### Branching

*   Create a new branch for each feature or bug fix.
*   Use a descriptive branch name, such as `feat/add-new-feature` or `fix/resolve-bug`.
*   Push your changes to your fork and submit a pull request to the `main` branch.

### Code Style

*   **Python:** We use [black](https://github.com/psf/black) for code formatting. Please run `black .` before committing your changes.
*   **TypeScript/JavaScript:** We recommend using [prettier](https://prettier.io/) for code formatting.

### Testing

This project currently lacks a test suite. We encourage you to add tests for any new features or bug fixes you introduce.

## API Map

The backend API is organized into the following modules:

*   **/auth**: User authentication and authorization.
    *   `POST /token`: Get an access token.
*   **/users**: User management.
    *   `GET /users/me`: Get the current user's profile.
    *   `PUT /users/me`: Update the current user's profile.
*   **/courses**: Course management.
    *   `GET /courses`: Get a list of all courses.
    *   `POST /courses`: Create a new course.
    *   `GET /courses/{course_id}`: Get a single course.
    *   `PUT /courses/{course_id}`: Update a course.
    *   `DELETE /courses/{course_id}`: Delete a course.
*   **/lessons**: Lesson management.
    *   `GET /courses/{course_id}/lessons`: Get all lessons for a course.
    *   `POST /courses/{course_id}/lessons`: Create a new lesson.
    *   `GET /lessons/{lesson_id}`: Get a single lesson.
    *   `PUT /lessons/{lesson_id}`: Update a lesson.
    *   `DELETE /lessons/{lesson_id}`: Delete a lesson.
*   **/achievements**: Gamification achievements.
*   **/analytics**: User analytics.
*   **/gamification**: Gamification utilities.
*   **/notifications**: User notifications.
*   **/recommendations**: Course recommendations.
