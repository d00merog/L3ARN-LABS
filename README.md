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
