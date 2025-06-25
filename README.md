# Renter Chat Application

A full-stack chat application for prospective renters with intelligent response handling and actionable next steps.

## Requirements Summary

This is a take-home exercise implementing a **Mini Leasing Assistant API** that processes prospective renter inquiries and provides intelligent responses.

### Core Scenario
- Prospective renter sends free-text message (email/SMS)
- Microservice must:
  - Decide which domain tool(s) to call for information
  - Craft human-ready reply
  - Return next-action for front-end execution

### Required Components
1. **LLM-Agent Logic**: Lightweight agent using LLM (OpenAI/Claude/Gemini) to orchestrate domain tools
2. **Domain Tools**: Three required tools for property information
3. **React Frontend**: TypeScript chat workspace with message list and input
4. **Backend API**: FastAPI endpoints for chat message processing
5. **Data Layer**: Mock inventory with observability logging

### Domain Tools Required
- `check_availability(community_id, bedrooms)` → Unit availability information
- `check_pet_policy(community_id, pet_type)` → Pet policy and fees
- `get_pricing(community_id, unit_id, move_in_date)` → Rent and specials

### Action System
- `propose_tour`: System suggests specific tour slot
- `ask_clarification`: Question needs more details  
- `handoff_human`: Cannot fulfill automatically

## Overview

This application processes free-text messages (email or SMS) from prospective renters and provides intelligent responses with actionable next steps. The system decides which tools to call, crafts human-ready replies, and returns actions that the front-end can execute.

## Architecture

- **Frontend**: React TypeScript chat interface with message list, input bar, and dynamic action buttons
- **Backend**: FastAPI Python service with intelligent agent logic for processing renter inquiries
- **Communication**: REST API with CORS-enabled endpoints

## Key Features

- **Real-time Chat Interface**: Responsive chat workspace with message history
- **Intelligent Response System**: Context-aware responses based on inquiry type
- **Action-based UI**: Dynamic buttons for tour scheduling, clarification requests, and human handoff
- **Tour Scheduling**: Automated tour time proposals with confirmation workflow
- **Human Handoff**: Seamless escalation to human agents when needed

## API Contract

The system implements a single REST endpoint:

**POST /api/reply**

**Request:**
```json
{
  "lead": {
    "name": "Jane Doe",
    "email": "jane@example.com"
  },
  "message": "Hi, is a 2-bedroom still available and do you allow cats?",
  "preferences": {
    "bedrooms": 2,
    "move_in": "2025-07-01"
  },
  "community_id": "sunset-ridge"
}
```

**Response:**
```json
{
  "reply": "Hi Jane! Unit 12B is available and cats are welcome (one-time $50 fee). Tours are open this Saturday 10 am–2 pm—does 11 am work?",
  "action": "propose_tour",
  "proposed_time": "2025-06-14T18:00:00Z"
}
```

## Action Types

- **`propose_tour`**: System has enough info to suggest a specific tour slot
- **`ask_clarification`**: Lead's question is ambiguous or lacks key details  
- **`handoff_human`**: Request cannot be fulfilled automatically (e.g., no vacancies)

## Getting Started

For detailed setup instructions, testing guidelines, and development workflows, see [DEVELOPMENT.md](DEVELOPMENT.md).

Quick start:
```bash
make setup  # Install dependencies
make dev    # Start both servers
```

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
├── Makefile           # Development automation
└── DEVELOPMENT.md     # Setup and testing guide
```