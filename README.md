# AI-First CRM HCP Interaction Logger

An assignment-ready AI-first Healthcare Professional (HCP) CRM module focused on the **Log Interaction Screen**. The project includes a React + Redux frontend, a FastAPI backend, SQL persistence, and a LangGraph agent that uses Groq-hosted LLMs to help field representatives log and manage sales interactions.

## What This Builds

- Structured interaction logging form for medical sales representatives.
- Conversational chat logger for natural-language HCP visit notes.
- LangGraph agent with six sales tools:
  - Log Interaction
  - Edit Interaction
  - Retrieve HCP Profile
  - Suggest Next Best Action
  - Schedule Follow-Up
  - Compliance Check
- Groq LLM integration configured for `gemma2-9b-it` by default.
- Optional fallback model: `llama-3.3-70b-versatile`.
- SQLAlchemy persistence with SQLite for local demos and Postgres/MySQL via `DATABASE_URL`.

## Features

- AI-assisted HCP interaction logging using natural language.
- Structured CRM interaction form for medical representatives.
- LangGraph-powered workflow orchestration.
- Groq LLM integration for intent detection and information extraction.
- Retrieve Healthcare Professional (HCP) profiles.
- Edit previously logged interactions.
- Suggest Next Best Actions based on previous interactions.
- Schedule follow-up visits automatically.
- Compliance checking for off-label and policy-sensitive conversations.
- Persistent storage using SQLAlchemy with SQLite or PostgreSQL.
- Interactive Swagger API documentation.

## Technology Stack

### Frontend
- React 19
- TypeScript
- Redux Toolkit
- Material UI (MUI)
- Axios
- Vite

### Backend
- FastAPI
- Python 3.11+
- SQLAlchemy
- Pydantic
- Uvicorn

### AI & Workflow
- LangGraph
- LangChain
- Groq LLM
- Gemma2-9B-IT (default)
- Llama-3.3-70B-Versatile (fallback)

### Database
- SQLite (default)
- PostgreSQL (optional)

### Development Tools
- Swagger UI
- Docker & Docker Compose
- Git & GitHub

## System Architecture

```text
                   +-------------------------+
                   |     React + Redux UI    |
                   +------------+------------+
                                |
                                | REST API
                                |
                   +------------v------------+
                   |     FastAPI Backend     |
                   +------------+------------+
                                |
                                |
                   +------------v------------+
                   |     LangGraph Agent     |
                   +------------+------------+
                                |
          +---------------------+----------------------+
          |          |           |          |          |
          |          |           |          |          |
+---------v--+ +-----v-----+ +---v------+ +--v-----+ +--v-----------+
| Log        | | Edit      | | HCP      | | Next   | | Compliance   |
| Interaction| |Interaction| | Profile  | | Action | | Check        |
+------------+ +-----------+ +----------+ +--------+ +--------------+
                                |
                                |
                        +-------v--------+
                        | SQL Database   |
                        | SQLite/Postgres|
                        +----------------+
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Verify backend health status |
| GET | `/api/hcps` | Retrieve all Healthcare Professional (HCP) profiles |
| GET | `/api/interactions` | Retrieve all logged interactions |
| POST | `/api/interactions` | Create a new interaction |
| PATCH | `/api/interactions/{interaction_id}` | Update an existing interaction |
| POST | `/api/agent/chat` | Send natural language requests to the LangGraph AI agent |
| POST | `/api/agent/tools/demo` | Execute all LangGraph tools for demonstration |

## Project Highlights

- Developed an AI-first Customer Relationship Management (CRM) module for Healthcare Professionals (HCPs).
- Implemented a dual interaction workflow supporting both structured forms and conversational AI.
- Integrated LangGraph to orchestrate AI workflows through specialized CRM tools.
- Utilized Groq-hosted Large Language Models (LLMs) for intent detection, entity extraction, and response generation.
- Implemented six AI-powered CRM tools:
  - Log Interaction
  - Edit Interaction
  - Retrieve HCP Profile
  - Suggest Next Best Action
  - Schedule Follow-Up
  - Compliance Check
- Designed RESTful APIs using FastAPI with automatic OpenAPI (Swagger) documentation.
- Implemented persistent data storage using SQLAlchemy with SQLite and optional PostgreSQL support.
- Built a responsive React + Redux frontend following an AI-first workflow where conversational input automatically populates structured CRM fields.

## AI Workflow

The application follows an AI-first workflow powered by LangGraph and Groq LLM.

1. The field representative enters interaction details through either:
   - A structured interaction form, or
   - A conversational AI chat interface.
2. The LangGraph agent analyzes the user's request.
3. Groq LLM identifies the user's intent and extracts structured CRM information.
4. LangGraph routes the request to the appropriate CRM tool.
5. The selected tool performs the requested operation.
6. Results are stored in the database and returned to the frontend.

Workflow:

User Input
      │
      ▼
Groq LLM
      │
      ▼
LangGraph Agent
      │
      ├── Log Interaction
      ├── Edit Interaction
      ├── Retrieve HCP Profile
      ├── Suggest Next Best Action
      ├── Schedule Follow-Up
      └── Compliance Check
      │
      ▼
SQLite / PostgreSQL Database
      │
      ▼
React + Redux Frontend

## Key Assignment Requirements Covered

| Assignment Requirement | Implementation Status |
|------------------------|-----------------------|
| React Frontend | ✅ Implemented |
| Redux State Management | ✅ Implemented |
| FastAPI Backend | ✅ Implemented |
| LangGraph Agent | ✅ Implemented |
| Groq LLM Integration | ✅ Implemented |
| Log Interaction Screen | ✅ Implemented |
| Structured Form Logging | ✅ Implemented |
| Conversational AI Logging | ✅ Implemented |
| Log Interaction Tool | ✅ Implemented |
| Edit Interaction Tool | ✅ Implemented |
| Retrieve HCP Profile Tool | ✅ Implemented |
| Suggest Next Best Action Tool | ✅ Implemented |
| Schedule Follow-Up Tool | ✅ Implemented |
| Compliance Check Tool | ✅ Implemented |
| Swagger API Documentation | ✅ Implemented |
| SQL Database Integration | ✅ Implemented |

# Screenshots

## Dashboard

<img src="screenshorts/Dashboard.png" width="1000"/>
<img src="screenshorts/Dashboard1.png" width="1000"/>

---

## AI Interaction Logging

<img src="screenshorts/Interaction.png" width="1000"/>

---

## LangGraph Tools

<img src="screenshorts/tools.png" width="1000"/>

---

## Swagger API

<img src="screenshorts/swagger.png" width="1000"/>
<img src="screenshorts/swagger1.png" width="1000"/>




## Project Structure

```text
backend/
  app/
    agent/          LangGraph workflow and Groq LLM adapter
    api/            FastAPI routers
    core/           settings and database setup
    models/         SQLAlchemy models
    schemas/        Pydantic request/response models
    services/       CRM business logic and agent tools
  requirements.txt
  .env.example
frontend/
  src/
    app/            Redux store
    components/     UI components
    features/       CRM screen and state slices
    services/       API client
  package.json
docker-compose.yml
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- A Groq API key from [Groq Console](https://console.groq.com/)

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_new_groq_api_key
GROQ_MODEL=gemma2-9b-it
DATABASE_URL=sqlite:///./hcp_crm.db
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Open API docs:

```text
http://localhost:8000/docs
```

## Postgres Option

The app runs with SQLite for fast demos, but the same code supports Postgres/MySQL. To use Postgres:

```bash
docker compose up -d db
```

Then set:

```env
DATABASE_URL=postgresql+psycopg://crm_user:crm_password@localhost:5432/hcp_crm
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Demo Flow For The 10-15 Minute Video

1. Start backend and frontend.
2. Show the Log Interaction screen.
3. Use the structured form:
   - Pick an HCP.
   - Add channel, date, products, samples, sentiment, topics, and notes.
   - Submit and show the timeline update.
4. Use the chat tab:
   - Example prompt:

```text
Log a visit with Dr. Meera Patel today. We discussed CardioMax adherence, she asked for renal safety data, sentiment was positive, and I promised a follow-up next Tuesday.
```

5. Open `/docs` and run `POST /api/agent/tools/demo` to show all tools working.
6. Explain the LangGraph agent:
   - Understands representative intent through Groq.
   - Routes to CRM tools.
   - Persists interaction records.
   - Produces next actions and compliance checks.

## LangGraph Agent Role

The LangGraph agent acts as the orchestration layer between field-rep input and CRM actions. It receives free-text notes, uses the Groq model to classify intent and extract structured CRM fields, chooses the correct tool, validates compliance-sensitive content, writes to the database, and returns an auditable response to the UI.

The workflow is intentionally simple and explainable:

```text
receive user message -> understand intent with LLM -> execute CRM tool -> return response
```

## Required Assignment Notes

- The backend imports and uses `langgraph.graph.StateGraph`.
- Groq is configured through `langchain-groq`.
- `gemma2-9b-it` is the default model in `.env.example` because the assignment asks for it.
- If the Groq account no longer exposes that model, set `GROQ_MODEL=llama-3.3-70b-versatile`.

## Submission Checklist

- Push this repository to GitHub.
- Record a 10-15 minute walkthrough covering the frontend, all tools, code structure, and task understanding.
- Submit the GitHub link and video link in the Google Form supplied in the assignment document.
