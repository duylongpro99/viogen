# Creative Studio

A chat-based creative studio where users collaborate with AI specialists to generate images and videos using Ollama SLMs and ComfyUI.

## Architecture

- **Backend**: FastAPI with SSE streaming
- **Frontend**: Next.js 14 with TypeScript
- **Database**: Supabase (PostgreSQL)
- **AI Models**: Ollama (local SLMs)
- **Generation**: ComfyUI

## The Creative Team

- **Luna** (Style) - Artistic style, mood, color theory
- **Frame** (Composition) - Camera angles, framing, visual hierarchy
- **Saga** (Story) - Narrative context, emotional depth
- **Pixel** (Technical) - ComfyUI parameters, model selection
- **Lens** (Critic) - Quality review, improvements

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Ollama with models pulled (e.g., `ollama pull llama3.2`)
- ComfyUI running locally

## Quick Start

### 1. Start Supabase

```bash
npx supabase start
```

Save the anon key from the output.

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Supabase keys
```

### 3. Start Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Start Ollama

```bash
ollama serve
```

### 6. Start ComfyUI

```bash
cd /path/to/ComfyUI
python main.py
```

### 7. Open App

Navigate to http://localhost:3000

## Development

### Run Tests

```bash
cd backend && pytest
```

### Database Migrations

```bash
npx supabase db reset  # Reset and apply all migrations
```

## License

MIT
