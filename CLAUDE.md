# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a renter chat application with a React TypeScript frontend and FastAPI Python backend. The application processes free-text messages from prospective renters and provides intelligent responses with actionable next steps.

## Project Structure

```
├── frontend/          # React TypeScript UI
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── types/         # TypeScript type definitions
│   │   └── services/      # API service layer
├── backend/           # FastAPI Python service
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models/       # Pydantic schemas
│   │   └── services/     # Business logic
└── requirement.pdf    # Original specifications
```

## Development Commands

### Frontend (React TypeScript)
```bash
cd frontend
npm install          # Install dependencies
npm start            # Start development server (http://localhost:3000)
npm run build        # Build for production
npm test             # Run tests
```

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
python -m app.main               # Start development server (http://localhost:8000)
# or
uvicorn app.main:app --reload    # Alternative start command
```

## API Contract

The backend implements a single endpoint:
- **POST /api/reply** - Processes renter messages and returns intelligent responses

## Architecture Notes

- **Frontend**: Chat workspace UI with message list, input bar, and action buttons
- **Backend**: FastAPI service with placeholder agent logic (ready for implementation)
- **Communication**: REST API between frontend and backend
- **Actions**: System supports `propose_tour`, `ask_clarification`, and `handoff_human` actions

## Development Workflow

1. Start backend server first: `cd backend && python -m app.main`
2. Start frontend server: `cd frontend && npm start`
3. Frontend communicates with backend via CORS-enabled API calls