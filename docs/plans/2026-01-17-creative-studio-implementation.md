# Creative Studio Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a chat-based creative studio where users collaborate with AI specialists to generate images/videos using Ollama SLMs and ComfyUI.

**Architecture:** FastAPI backend with SSE streaming handles orchestration between 5 specialist SLMs. Next.js frontend provides real-time chat interface. Supabase (PostgreSQL + Storage) persists sessions, conversations, and generated media.

**Tech Stack:** Python 3.11+, FastAPI, Ollama, ComfyUI API, Next.js 14, TypeScript, Supabase, Docker

---

## Phase 1: Project Foundation

### Task 1: Initialize Backend Project

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`

**Step 1: Create backend directory structure**

```bash
mkdir -p backend/app/api/routes backend/app/core/specialists backend/app/services backend/app/models backend/app/workflows/templates backend/tests
```

**Step 2: Create requirements.txt**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
httpx==0.26.0
pydantic==2.5.3
pydantic-settings==2.1.0
sse-starlette==2.0.0
supabase==2.3.4
pytest==7.4.4
pytest-asyncio==0.23.3
```

**Step 3: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = "http://localhost:54321"
    supabase_key: str = "your-anon-key"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # ComfyUI
    comfyui_base_url: str = "http://localhost:8188"

    # App
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
```

**Step 4: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="Creative Studio API",
    description="Multi-model orchestration for image/video generation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "debug": settings.debug}
```

**Step 5: Create __init__.py**

```python
# backend/app/__init__.py
```

**Step 6: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Step 7: Run backend to verify**

```bash
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
```

Expected: Server starts, http://localhost:8000/health returns `{"status": "healthy", "debug": true}`

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: initialize FastAPI backend with health check"
```

---

### Task 2: Initialize Frontend Project

**Files:**
- Create: `frontend/` (Next.js project)
- Modify: `frontend/package.json`
- Create: `frontend/src/app/page.tsx`

**Step 1: Create Next.js project**

```bash
cd /Users/onedayin20902/personal/threejs-skill/.worktrees/creative-studio
npx create-next-app@14 frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias
```

**Step 2: Install additional dependencies**

```bash
cd frontend && npm install @supabase/supabase-js uuid && npm install -D @types/uuid
```

**Step 3: Create basic landing page**

Replace `frontend/src/app/page.tsx`:

```tsx
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Creative Studio</h1>
      <p className="text-gray-600 mb-8">
        Collaborate with AI specialists to create images and videos
      </p>
      <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
        Start Creating
      </button>
    </main>
  );
}
```

**Step 4: Run frontend to verify**

```bash
cd frontend && npm run dev
```

Expected: http://localhost:3000 shows landing page with "Creative Studio" heading

**Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: initialize Next.js frontend with landing page"
```

---

### Task 3: Setup Supabase Local Development

**Files:**
- Create: `supabase/config.toml`
- Create: `supabase/migrations/00001_initial_schema.sql`
- Create: `docker-compose.yml`

**Step 1: Initialize Supabase**

```bash
cd /Users/onedayin20902/personal/threejs-skill/.worktrees/creative-studio
npx supabase init
```

**Step 2: Create initial migration**

Create `supabase/migrations/00001_initial_schema.sql`:

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    model_assignments JSONB DEFAULT '{}'::jsonb,
    settings JSONB DEFAULT '{}'::jsonb
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'ideation' CHECK (status IN ('ideation', 'refinement', 'synthesis', 'review', 'generating', 'complete')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'style', 'composition', 'story', 'technical', 'critic', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generations table
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    workflow_json JSONB,
    parameters JSONB DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'complete', 'failed')),
    progress INTEGER DEFAULT 0,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_generations_conversation ON generations(conversation_id);

-- Storage bucket for generated media
INSERT INTO storage.buckets (id, name, public)
VALUES ('generations', 'generations', true);
```

**Step 3: Create docker-compose.yml for full stack**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=http://supabase-kong:8000
      - SUPABASE_KEY=${SUPABASE_ANON_KEY}
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - COMFYUI_BASE_URL=http://host.docker.internal:8188
    volumes:
      - ./backend:/app
    depends_on:
      - supabase-db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

networks:
  default:
    name: creative-studio
```

**Step 4: Create .env.example**

```bash
# Supabase (get from supabase start output)
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# ComfyUI
COMFYUI_BASE_URL=http://localhost:8188
```

**Step 5: Start Supabase and verify**

```bash
npx supabase start
```

Expected: Supabase starts, outputs URLs and keys. Save the anon key.

**Step 6: Apply migrations**

```bash
npx supabase db reset
```

Expected: Tables created successfully

**Step 7: Commit**

```bash
git add supabase/ docker-compose.yml .env.example
git commit -m "feat: add Supabase schema and docker-compose setup"
```

---

## Phase 2: Backend Core Services

### Task 4: Create Supabase Service

**Files:**
- Create: `backend/app/services/supabase.py`
- Create: `backend/tests/test_supabase.py`

**Step 1: Write failing test**

Create `backend/tests/__init__.py`:
```python
```

Create `backend/tests/conftest.py`:
```python
import pytest
from app.config import settings


@pytest.fixture
def supabase_client():
    from app.services.supabase import get_supabase_client
    return get_supabase_client()
```

Create `backend/tests/test_supabase.py`:
```python
import pytest


def test_supabase_client_connects(supabase_client):
    # Should be able to query sessions table
    result = supabase_client.table("sessions").select("*").limit(1).execute()
    assert result.data is not None
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_supabase.py -v
```

Expected: FAIL - module not found

**Step 3: Implement supabase service**

Create `backend/app/services/__init__.py`:
```python
```

Create `backend/app/services/supabase.py`:
```python
from supabase import create_client, Client

from app.config import settings

_client: Client | None = None


def get_supabase_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_supabase.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/ backend/tests/
git commit -m "feat: add Supabase client service"
```

---

### Task 5: Create Ollama Service

**Files:**
- Create: `backend/app/services/ollama.py`
- Create: `backend/tests/test_ollama.py`

**Step 1: Write failing test**

Create `backend/tests/test_ollama.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_ollama_generate_streams_response():
    from app.services.ollama import OllamaClient

    client = OllamaClient()

    # Mock the httpx response
    mock_response = AsyncMock()
    mock_response.aiter_lines = AsyncMock(return_value=iter([
        '{"response": "Hello", "done": false}',
        '{"response": " world", "done": true}'
    ]))
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    with patch.object(client._client, 'stream', return_value=mock_response):
        chunks = []
        async for chunk in client.generate("test-model", "Hello"):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0]["response"] == "Hello"
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_ollama.py -v
```

Expected: FAIL - module not found

**Step 3: Implement Ollama service**

Create `backend/app/services/ollama.py`:
```python
import json
from typing import AsyncGenerator

import httpx

from app.config import settings


class OllamaClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        context: list | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Stream generate response from Ollama."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
        }
        if system:
            payload["system"] = system
        if context:
            payload["context"] = context

        async with self._client.stream("POST", "/api/generate", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    yield json.loads(line)

    async def list_models(self) -> list[dict]:
        """List available models."""
        response = await self._client.get("/api/tags")
        response.raise_for_status()
        return response.json().get("models", [])

    async def check_health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = await self._client.get("/api/tags")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def close(self):
        await self._client.aclose()


# Singleton instance
_ollama_client: OllamaClient | None = None


def get_ollama_client() -> OllamaClient:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_ollama.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/ollama.py backend/tests/test_ollama.py
git commit -m "feat: add Ollama client service with streaming"
```

---

### Task 6: Create ComfyUI Service

**Files:**
- Create: `backend/app/services/comfyui.py`
- Create: `backend/tests/test_comfyui.py`

**Step 1: Write failing test**

Create `backend/tests/test_comfyui.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_comfyui_queue_workflow():
    from app.services.comfyui import ComfyUIClient

    client = ComfyUIClient()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"prompt_id": "test-123"}

    with patch.object(client._client, 'post', new_callable=AsyncMock, return_value=mock_response):
        prompt_id = await client.queue_workflow({"test": "workflow"})
        assert prompt_id == "test-123"
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_comfyui.py -v
```

Expected: FAIL - module not found

**Step 3: Implement ComfyUI service**

Create `backend/app/services/comfyui.py`:
```python
import httpx

from app.config import settings


class ComfyUIClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.comfyui_base_url
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=300.0)

    async def queue_workflow(self, workflow: dict) -> str:
        """Queue a workflow and return the prompt ID."""
        response = await self._client.post("/prompt", json={"prompt": workflow})
        response.raise_for_status()
        return response.json()["prompt_id"]

    async def get_history(self, prompt_id: str) -> dict:
        """Get the history/status of a prompt."""
        response = await self._client.get(f"/history/{prompt_id}")
        response.raise_for_status()
        return response.json()

    async def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Get generated image data."""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = await self._client.get("/view", params=params)
        response.raise_for_status()
        return response.content

    async def check_health(self) -> bool:
        """Check if ComfyUI is running."""
        try:
            response = await self._client.get("/system_stats")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def get_progress(self, prompt_id: str) -> dict:
        """Poll for generation progress."""
        history = await self.get_history(prompt_id)
        if prompt_id in history:
            return {"status": "complete", "outputs": history[prompt_id].get("outputs", {})}
        return {"status": "running", "progress": 0}

    async def close(self):
        await self._client.aclose()


_comfyui_client: ComfyUIClient | None = None


def get_comfyui_client() -> ComfyUIClient:
    global _comfyui_client
    if _comfyui_client is None:
        _comfyui_client = ComfyUIClient()
    return _comfyui_client
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_comfyui.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/comfyui.py backend/tests/test_comfyui.py
git commit -m "feat: add ComfyUI client service"
```

---

## Phase 3: Specialists & Orchestration

### Task 7: Create Base Specialist Class

**Files:**
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/specialists/__init__.py`
- Create: `backend/app/core/specialists/base.py`
- Create: `backend/tests/test_specialists.py`

**Step 1: Write failing test**

Create `backend/tests/test_specialists.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_specialist_generates_response():
    from app.core.specialists.base import BaseSpecialist

    class TestSpecialist(BaseSpecialist):
        role = "test"
        name = "Testy"
        system_prompt = "You are a test specialist."

    specialist = TestSpecialist(model="test-model")

    mock_chunks = [
        {"response": "Hello", "done": False},
        {"response": " there", "done": True},
    ]

    async def mock_generate(*args, **kwargs):
        for chunk in mock_chunks:
            yield chunk

    with patch('app.core.specialists.base.get_ollama_client') as mock_client:
        mock_client.return_value.generate = mock_generate

        response = ""
        async for chunk in specialist.respond("Test message", []):
            response += chunk

        assert response == "Hello there"
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_specialists.py -v
```

Expected: FAIL - module not found

**Step 3: Implement base specialist**

Create `backend/app/core/__init__.py`:
```python
```

Create `backend/app/core/specialists/__init__.py`:
```python
from .base import BaseSpecialist
from .style import StyleSpecialist
from .composition import CompositionSpecialist
from .story import StorySpecialist
from .technical import TechnicalSpecialist
from .critic import CriticSpecialist

__all__ = [
    "BaseSpecialist",
    "StyleSpecialist",
    "CompositionSpecialist",
    "StorySpecialist",
    "TechnicalSpecialist",
    "CriticSpecialist",
]
```

Create `backend/app/core/specialists/base.py`:
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.services.ollama import get_ollama_client


class BaseSpecialist(ABC):
    role: str = ""
    name: str = ""
    system_prompt: str = ""

    def __init__(self, model: str):
        self.model = model
        self._client = get_ollama_client()

    def _build_prompt(self, user_message: str, conversation_history: list[dict]) -> str:
        """Build prompt with conversation context."""
        history_text = ""
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            role_name = msg.get("role_name", msg["role"])
            history_text += f"{role_name}: {msg['content']}\n"

        return f"""Previous conversation:
{history_text}

Current request: {user_message}

Respond as {self.name}, focusing on your specialty."""

    async def respond(
        self,
        user_message: str,
        conversation_history: list[dict],
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        prompt = self._build_prompt(user_message, conversation_history)

        async for chunk in self._client.generate(
            model=self.model,
            prompt=prompt,
            system=self.system_prompt,
        ):
            if chunk.get("response"):
                yield chunk["response"]
```

**Step 4: Run test to verify it passes**

```bash
cd backend && pytest tests/test_specialists.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/core/
git commit -m "feat: add BaseSpecialist class for SLM specialists"
```

---

### Task 8: Create Five Specialist Implementations

**Files:**
- Create: `backend/app/core/specialists/style.py`
- Create: `backend/app/core/specialists/composition.py`
- Create: `backend/app/core/specialists/story.py`
- Create: `backend/app/core/specialists/technical.py`
- Create: `backend/app/core/specialists/critic.py`

**Step 1: Create Style Specialist (Luna)**

Create `backend/app/core/specialists/style.py`:
```python
from .base import BaseSpecialist


class StyleSpecialist(BaseSpecialist):
    role = "style"
    name = "Luna"
    system_prompt = """You are Luna, the Style Specialist in a creative team.

Your expertise:
- Artistic styles and movements (impressionism, cyberpunk, art nouveau, etc.)
- Color theory and palettes
- Mood and atmosphere
- Lighting techniques
- Visual aesthetics and texture

Personality: Expressive, uses vivid descriptive language, passionate about visual beauty.

When responding:
- Suggest specific color palettes (e.g., "deep teals against warm ambers")
- Reference artistic styles and influences
- Describe mood and emotional tone
- Consider lighting direction and quality
- Keep responses concise but evocative (2-4 sentences)

You're collaborating with Frame (composition), Saga (story), Pixel (technical), and Lens (critic)."""
```

**Step 2: Create Composition Specialist (Frame)**

Create `backend/app/core/specialists/composition.py`:
```python
from .base import BaseSpecialist


class CompositionSpecialist(BaseSpecialist):
    role = "composition"
    name = "Frame"
    system_prompt = """You are Frame, the Composition Expert in a creative team.

Your expertise:
- Camera angles and positioning
- Framing and focal length
- Rule of thirds, golden ratio
- Visual hierarchy and focal points
- Depth, foreground/background relationships
- Leading lines and visual flow

Personality: Precise, thinks in spatial terms, analytical but creative.

When responding:
- Specify camera positions (low angle, bird's eye, etc.)
- Suggest focal lengths (35mm, 85mm, etc.)
- Describe element placement using compositional rules
- Consider depth and layering
- Keep responses concise and spatial (2-4 sentences)

You're collaborating with Luna (style), Saga (story), Pixel (technical), and Lens (critic)."""
```

**Step 3: Create Story Specialist (Saga)**

Create `backend/app/core/specialists/story.py`:
```python
from .base import BaseSpecialist


class StorySpecialist(BaseSpecialist):
    role = "story"
    name = "Saga"
    system_prompt = """You are Saga, the Story/Narrative Guide in a creative team.

Your expertise:
- Emotional context and meaning
- Narrative elements and storytelling
- Character motivation and intent
- Scene-building and world-building
- Symbolic and thematic depth

Personality: Thoughtful, introspective, asks "why" questions, finds meaning.

When responding:
- Add narrative context to scenes
- Suggest emotional undertones
- Consider what story the image tells
- Ask thought-provoking questions about meaning
- Keep responses evocative but brief (2-4 sentences)

You're collaborating with Luna (style), Frame (composition), Pixel (technical), and Lens (critic)."""
```

**Step 4: Create Technical Specialist (Pixel)**

Create `backend/app/core/specialists/technical.py`:
```python
from .base import BaseSpecialist


class TechnicalSpecialist(BaseSpecialist):
    role = "technical"
    name = "Pixel"
    system_prompt = """You are Pixel, the Technical Director in a creative team.

Your expertise:
- Translating creative ideas into generation parameters
- Model selection (SD 1.5, SDXL, etc.)
- Sampler settings (DPM++, Euler, etc.)
- CFG scale and step counts
- LoRAs and embeddings
- ComfyUI workflow construction
- Resolution and aspect ratios

Personality: Practical, precise, translates abstract ideas into specs.

When responding:
- Suggest specific technical parameters
- Recommend appropriate models and LoRAs
- Consider feasibility and quality tradeoffs
- Speak in concrete, actionable terms
- Keep responses technical but accessible (2-4 sentences)

You're collaborating with Luna (style), Frame (composition), Saga (story), and Lens (critic)."""
```

**Step 5: Create Critic Specialist (Lens)**

Create `backend/app/core/specialists/critic.py`:
```python
from .base import BaseSpecialist


class CriticSpecialist(BaseSpecialist):
    role = "critic"
    name = "Lens"
    system_prompt = """You are Lens, the Quality Critic in a creative team.

Your expertise:
- Evaluating coherence and consistency
- Identifying potential issues before generation
- Suggesting improvements and refinements
- Ensuring all elements work together
- Catching contradictions or conflicts

Personality: Constructive, thorough, detail-oriented, supportive but honest.

When responding:
- Point out potential issues or conflicts
- Suggest specific improvements
- Confirm when ideas are well-aligned
- Ask clarifying questions if something is unclear
- Keep feedback constructive and brief (2-4 sentences)

You're collaborating with Luna (style), Frame (composition), Saga (story), and Pixel (technical)."""
```

**Step 6: Run all tests**

```bash
cd backend && pytest tests/ -v
```

Expected: All tests pass

**Step 7: Commit**

```bash
git add backend/app/core/specialists/
git commit -m "feat: add five specialist implementations (Luna, Frame, Saga, Pixel, Lens)"
```

---

### Task 9: Create Orchestration Engine

**Files:**
- Create: `backend/app/core/orchestrator.py`
- Create: `backend/app/core/phases.py`
- Create: `backend/tests/test_orchestrator.py`

**Step 1: Write failing test**

Create `backend/tests/test_orchestrator.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_orchestrator_runs_ideation_phase():
    from app.core.orchestrator import Orchestrator
    from app.core.phases import Phase

    model_assignments = {
        "style": "llama3.2",
        "composition": "llama3.2",
        "story": "llama3.2",
        "technical": "llama3.2",
        "critic": "llama3.2",
    }

    orchestrator = Orchestrator(model_assignments)

    # Mock all specialists to return simple responses
    async def mock_respond(*args, **kwargs):
        yield "Test response from specialist"

    for specialist in orchestrator.specialists.values():
        specialist.respond = mock_respond

    messages = []
    async for msg in orchestrator.process_user_message("Create a sunset scene"):
        messages.append(msg)

    assert len(messages) > 0
    assert orchestrator.current_phase == Phase.IDEATION
```

**Step 2: Run test to verify it fails**

```bash
cd backend && pytest tests/test_orchestrator.py -v
```

Expected: FAIL - module not found

**Step 3: Create phases module**

Create `backend/app/core/phases.py`:
```python
from enum import Enum


class Phase(Enum):
    IDEATION = "ideation"
    REFINEMENT = "refinement"
    SYNTHESIS = "synthesis"
    REVIEW = "review"
    GENERATING = "generating"
    COMPLETE = "complete"


PHASE_SPECIALISTS = {
    Phase.IDEATION: ["style", "composition", "story"],
    Phase.REFINEMENT: ["style", "composition", "story", "critic"],
    Phase.SYNTHESIS: ["technical"],
    Phase.REVIEW: ["critic"],
}


def get_next_phase(current: Phase) -> Phase:
    """Get the next phase in the workflow."""
    order = [Phase.IDEATION, Phase.REFINEMENT, Phase.SYNTHESIS, Phase.REVIEW, Phase.GENERATING, Phase.COMPLETE]
    current_idx = order.index(current)
    if current_idx < len(order) - 1:
        return order[current_idx + 1]
    return current
```

**Step 4: Create orchestrator**

Create `backend/app/core/orchestrator.py`:
```python
from typing import AsyncGenerator

from app.core.phases import Phase, PHASE_SPECIALISTS, get_next_phase
from app.core.specialists import (
    StyleSpecialist,
    CompositionSpecialist,
    StorySpecialist,
    TechnicalSpecialist,
    CriticSpecialist,
)


class Orchestrator:
    def __init__(self, model_assignments: dict[str, str]):
        self.model_assignments = model_assignments
        self.current_phase = Phase.IDEATION
        self.conversation_history: list[dict] = []
        self.round_count = 0
        self.max_rounds_per_phase = 3

        # Initialize specialists
        self.specialists = {
            "style": StyleSpecialist(model_assignments.get("style", "llama3.2")),
            "composition": CompositionSpecialist(model_assignments.get("composition", "llama3.2")),
            "story": StorySpecialist(model_assignments.get("story", "llama3.2")),
            "technical": TechnicalSpecialist(model_assignments.get("technical", "llama3.2")),
            "critic": CriticSpecialist(model_assignments.get("critic", "llama3.2")),
        }

    async def process_user_message(
        self,
        message: str,
    ) -> AsyncGenerator[dict, None]:
        """Process a user message and stream specialist responses."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "role_name": "User",
            "content": message,
        })

        yield {
            "type": "user_message",
            "content": message,
        }

        # Get specialists for current phase
        active_specialists = PHASE_SPECIALISTS.get(self.current_phase, [])

        # Each specialist responds
        for role in active_specialists:
            specialist = self.specialists[role]

            yield {
                "type": "specialist_start",
                "role": role,
                "name": specialist.name,
            }

            full_response = ""
            async for chunk in specialist.respond(message, self.conversation_history):
                full_response += chunk
                yield {
                    "type": "specialist_chunk",
                    "role": role,
                    "name": specialist.name,
                    "content": chunk,
                }

            # Add to history
            self.conversation_history.append({
                "role": role,
                "role_name": specialist.name,
                "content": full_response,
            })

            yield {
                "type": "specialist_end",
                "role": role,
                "name": specialist.name,
                "content": full_response,
            }

        self.round_count += 1

        # Check if we should advance phase
        if self.round_count >= self.max_rounds_per_phase:
            self.advance_phase()
            yield {
                "type": "phase_change",
                "phase": self.current_phase.value,
            }

    def advance_phase(self):
        """Move to the next phase."""
        self.current_phase = get_next_phase(self.current_phase)
        self.round_count = 0

    def inject_user_message(self, message: str):
        """Handle user interjection during orchestration."""
        self.conversation_history.append({
            "role": "user",
            "role_name": "User",
            "content": message,
        })
```

**Step 5: Run test to verify it passes**

```bash
cd backend && pytest tests/test_orchestrator.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/core/orchestrator.py backend/app/core/phases.py backend/tests/test_orchestrator.py
git commit -m "feat: add orchestration engine with phase management"
```

---

## Phase 4: API Routes

### Task 10: Create Session API Routes

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/routes/__init__.py`
- Create: `backend/app/api/routes/sessions.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/session.py`

**Step 1: Create Pydantic models**

Create `backend/app/models/__init__.py`:
```python
from .session import Session, SessionCreate, SessionUpdate

__all__ = ["Session", "SessionCreate", "SessionUpdate"]
```

Create `backend/app/models/session.py`:
```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionCreate(BaseModel):
    model_assignments: dict[str, str] = {}
    settings: dict = {}


class SessionUpdate(BaseModel):
    model_assignments: dict[str, str] | None = None
    settings: dict | None = None


class Session(BaseModel):
    id: UUID
    created_at: datetime
    model_assignments: dict[str, str]
    settings: dict

    class Config:
        from_attributes = True
```

**Step 2: Create API dependencies**

Create `backend/app/api/__init__.py`:
```python
```

Create `backend/app/api/deps.py`:
```python
from app.services.supabase import get_supabase_client
from app.services.ollama import get_ollama_client
from app.services.comfyui import get_comfyui_client


def get_db():
    return get_supabase_client()


def get_ollama():
    return get_ollama_client()


def get_comfyui():
    return get_comfyui_client()
```

**Step 3: Create sessions routes**

Create `backend/app/api/routes/__init__.py`:
```python
```

Create `backend/app/api/routes/sessions.py`:
```python
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import get_db
from app.models.session import Session, SessionCreate, SessionUpdate

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=Session)
async def create_session(session: SessionCreate):
    db = get_db()
    result = db.table("sessions").insert({
        "model_assignments": session.model_assignments,
        "settings": session.settings,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return result.data[0]


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: UUID):
    db = get_db()
    result = db.table("sessions").select("*").eq("id", str(session_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    return result.data[0]


@router.patch("/{session_id}", response_model=Session)
async def update_session(session_id: UUID, session: SessionUpdate):
    db = get_db()

    update_data = {}
    if session.model_assignments is not None:
        update_data["model_assignments"] = session.model_assignments
    if session.settings is not None:
        update_data["settings"] = session.settings

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = db.table("sessions").update(update_data).eq("id", str(session_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Session not found")

    return result.data[0]


@router.delete("/{session_id}")
async def delete_session(session_id: UUID):
    db = get_db()
    result = db.table("sessions").delete().eq("id", str(session_id)).execute()

    return {"deleted": True}
```

**Step 4: Register routes in main.py**

Update `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import sessions

app = FastAPI(
    title="Creative Studio API",
    description="Multi-model orchestration for image/video generation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(sessions.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "debug": settings.debug}
```

**Step 5: Verify API works**

```bash
cd backend && uvicorn app.main:app --reload --port 8000
```

Test: `curl http://localhost:8000/api/sessions/ -X POST -H "Content-Type: application/json" -d '{}'`

Expected: Returns created session with UUID

**Step 6: Commit**

```bash
git add backend/app/api/ backend/app/models/ backend/app/main.py
git commit -m "feat: add session CRUD API routes"
```

---

### Task 11: Create Chat SSE Route

**Files:**
- Create: `backend/app/api/routes/chat.py`
- Create: `backend/app/models/message.py`
- Create: `backend/app/models/conversation.py`

**Step 1: Create message and conversation models**

Create `backend/app/models/conversation.py`:
```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    session_id: UUID


class Conversation(BaseModel):
    id: UUID
    session_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

Create `backend/app/models/message.py`:
```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class Message(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: dict
    created_at: datetime

    class Config:
        from_attributes = True
```

Update `backend/app/models/__init__.py`:
```python
from .session import Session, SessionCreate, SessionUpdate
from .conversation import Conversation, ConversationCreate
from .message import Message, MessageCreate

__all__ = [
    "Session", "SessionCreate", "SessionUpdate",
    "Conversation", "ConversationCreate",
    "Message", "MessageCreate",
]
```

**Step 2: Create chat route with SSE**

Create `backend/app/api/routes/chat.py`:
```python
import json
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_db
from app.core.orchestrator import Orchestrator
from app.models.message import MessageCreate
from app.models.conversation import Conversation, ConversationCreate

router = APIRouter(prefix="/chat", tags=["chat"])

# Store active orchestrators by conversation ID
active_orchestrators: dict[str, Orchestrator] = {}


@router.post("/conversations", response_model=Conversation)
async def create_conversation(data: ConversationCreate):
    db = get_db()

    # Get session for model assignments
    session = db.table("sessions").select("*").eq("id", str(data.session_id)).execute()
    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create conversation
    result = db.table("conversations").insert({
        "session_id": str(data.session_id),
        "status": "ideation",
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create conversation")

    # Initialize orchestrator
    conv_id = result.data[0]["id"]
    model_assignments = session.data[0].get("model_assignments", {})
    active_orchestrators[conv_id] = Orchestrator(model_assignments)

    return result.data[0]


@router.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: UUID, message: MessageCreate):
    db = get_db()
    conv_id_str = str(conversation_id)

    # Verify conversation exists
    conv = db.table("conversations").select("*").eq("id", conv_id_str).execute()
    if not conv.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get or create orchestrator
    if conv_id_str not in active_orchestrators:
        session = db.table("sessions").select("*").eq("id", conv.data[0]["session_id"]).execute()
        model_assignments = session.data[0].get("model_assignments", {}) if session.data else {}
        active_orchestrators[conv_id_str] = Orchestrator(model_assignments)

    # Save user message
    db.table("messages").insert({
        "conversation_id": conv_id_str,
        "role": "user",
        "content": message.content,
        "metadata": {},
    }).execute()

    async def event_generator():
        orchestrator = active_orchestrators[conv_id_str]

        async for event in orchestrator.process_user_message(message.content):
            # Save specialist messages to DB
            if event["type"] == "specialist_end":
                db.table("messages").insert({
                    "conversation_id": conv_id_str,
                    "role": event["role"],
                    "content": event["content"],
                    "metadata": {"name": event["name"]},
                }).execute()

            yield {
                "event": event["type"],
                "data": json.dumps(event),
            }

        # Update conversation status
        db.table("conversations").update({
            "status": orchestrator.current_phase.value,
        }).eq("id", conv_id_str).execute()

    return EventSourceResponse(event_generator())


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: UUID):
    db = get_db()

    result = db.table("messages")\
        .select("*")\
        .eq("conversation_id", str(conversation_id))\
        .order("created_at")\
        .execute()

    return result.data
```

**Step 3: Register chat routes**

Update `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import sessions, chat

app = FastAPI(
    title="Creative Studio API",
    description="Multi-model orchestration for image/video generation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(sessions.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "debug": settings.debug}
```

**Step 4: Commit**

```bash
git add backend/app/api/routes/chat.py backend/app/models/ backend/app/main.py
git commit -m "feat: add chat SSE route for real-time orchestration"
```

---

## Phase 5: Frontend Chat Interface

### Task 12: Create API Client and Types

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/types/index.ts`

**Step 1: Create TypeScript types**

Create `frontend/src/types/index.ts`:
```typescript
export interface Session {
  id: string;
  created_at: string;
  model_assignments: Record<string, string>;
  settings: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  session_id: string;
  status: 'ideation' | 'refinement' | 'synthesis' | 'review' | 'generating' | 'complete';
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'style' | 'composition' | 'story' | 'technical' | 'critic' | 'system';
  content: string;
  metadata: {
    name?: string;
  };
  created_at: string;
}

export interface SSEEvent {
  type: 'user_message' | 'specialist_start' | 'specialist_chunk' | 'specialist_end' | 'phase_change';
  role?: string;
  name?: string;
  content?: string;
  phase?: string;
}

export type SpecialistRole = 'style' | 'composition' | 'story' | 'technical' | 'critic';

export const SPECIALIST_INFO: Record<SpecialistRole, { name: string; color: string; icon: string }> = {
  style: { name: 'Luna', color: 'purple', icon: '🎨' },
  composition: { name: 'Frame', color: 'blue', icon: '📐' },
  story: { name: 'Saga', color: 'amber', icon: '📖' },
  technical: { name: 'Pixel', color: 'green', icon: '⚙️' },
  critic: { name: 'Lens', color: 'red', icon: '🔍' },
};
```

**Step 2: Create API client**

Create `frontend/src/lib/api.ts`:
```typescript
import type { Session, Conversation, Message } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function createSession(modelAssignments: Record<string, string> = {}): Promise<Session> {
  const res = await fetch(`${API_URL}/api/sessions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_assignments: modelAssignments, settings: {} }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function getSession(sessionId: string): Promise<Session> {
  const res = await fetch(`${API_URL}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error('Failed to get session');
  return res.json();
}

export async function createConversation(sessionId: string): Promise<Conversation> {
  const res = await fetch(`${API_URL}/api/chat/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function getMessages(conversationId: string): Promise<Message[]> {
  const res = await fetch(`${API_URL}/api/chat/conversations/${conversationId}/messages`);
  if (!res.ok) throw new Error('Failed to get messages');
  return res.json();
}

export function sendMessageSSE(
  conversationId: string,
  content: string,
  onEvent: (event: MessageEvent) => void,
  onError: (error: Event) => void,
): () => void {
  // First POST the message, which returns SSE
  const controller = new AbortController();

  fetch(`${API_URL}/api/chat/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
    signal: controller.signal,
  }).then(async (res) => {
    if (!res.ok || !res.body) {
      onError(new Event('error'));
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          onEvent(new MessageEvent('message', { data }));
        }
      }
    }
  }).catch((err) => {
    if (err.name !== 'AbortError') {
      onError(new Event('error'));
    }
  });

  return () => controller.abort();
}
```

**Step 3: Commit**

```bash
cd frontend && git add src/lib/api.ts src/types/index.ts
git commit -m "feat: add API client and TypeScript types"
```

---

### Task 13: Create SSE Hook

**Files:**
- Create: `frontend/src/hooks/useSSE.ts`

**Step 1: Create useSSE hook**

Create `frontend/src/hooks/useSSE.ts`:
```typescript
import { useState, useCallback, useRef } from 'react';
import { sendMessageSSE } from '@/lib/api';
import type { SSEEvent, Message } from '@/types';

interface UseSSEReturn {
  messages: Message[];
  streamingMessage: { role: string; name: string; content: string } | null;
  isStreaming: boolean;
  sendMessage: (conversationId: string, content: string) => void;
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
}

export function useSSE(): UseSSEReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingMessage, setStreamingMessage] = useState<{
    role: string;
    name: string;
    content: string;
  } | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<(() => void) | null>(null);

  const addMessage = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const sendMessage = useCallback((conversationId: string, content: string) => {
    // Cancel any existing stream
    if (abortRef.current) {
      abortRef.current();
    }

    setIsStreaming(true);

    // Add user message immediately
    const userMessage: Message = {
      id: crypto.randomUUID(),
      conversation_id: conversationId,
      role: 'user',
      content,
      metadata: {},
      created_at: new Date().toISOString(),
    };
    addMessage(userMessage);

    abortRef.current = sendMessageSSE(
      conversationId,
      content,
      (event) => {
        try {
          const data: SSEEvent = JSON.parse(event.data);

          switch (data.type) {
            case 'specialist_start':
              setStreamingMessage({
                role: data.role || '',
                name: data.name || '',
                content: '',
              });
              break;

            case 'specialist_chunk':
              setStreamingMessage((prev) => {
                if (!prev) return null;
                return { ...prev, content: prev.content + (data.content || '') };
              });
              break;

            case 'specialist_end':
              // Add completed message
              const specialistMessage: Message = {
                id: crypto.randomUUID(),
                conversation_id: conversationId,
                role: data.role as Message['role'],
                content: data.content || '',
                metadata: { name: data.name },
                created_at: new Date().toISOString(),
              };
              addMessage(specialistMessage);
              setStreamingMessage(null);
              break;

            case 'phase_change':
              // Could emit an event or update state
              console.log('Phase changed to:', data.phase);
              break;
          }
        } catch (e) {
          console.error('Failed to parse SSE event:', e);
        }
      },
      (error) => {
        console.error('SSE error:', error);
        setIsStreaming(false);
        setStreamingMessage(null);
      }
    );

    // Cleanup when all specialists done
    setTimeout(() => {
      setIsStreaming(false);
    }, 30000); // Timeout after 30s
  }, [addMessage]);

  return {
    messages,
    streamingMessage,
    isStreaming,
    sendMessage,
    addMessage,
    setMessages,
  };
}
```

**Step 2: Commit**

```bash
cd frontend && git add src/hooks/useSSE.ts
git commit -m "feat: add useSSE hook for streaming chat"
```

---

### Task 14: Create Chat Components

**Files:**
- Create: `frontend/src/components/chat/MessageStream.tsx`
- Create: `frontend/src/components/chat/MessageBubble.tsx`
- Create: `frontend/src/components/chat/SpecialistAvatar.tsx`
- Create: `frontend/src/components/chat/ChatInput.tsx`

**Step 1: Create SpecialistAvatar**

```bash
mkdir -p frontend/src/components/chat
```

Create `frontend/src/components/chat/SpecialistAvatar.tsx`:
```tsx
import { SPECIALIST_INFO, type SpecialistRole } from '@/types';

interface SpecialistAvatarProps {
  role: SpecialistRole | 'user';
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'w-6 h-6 text-xs',
  md: 'w-8 h-8 text-sm',
  lg: 'w-10 h-10 text-base',
};

const colorClasses: Record<string, string> = {
  purple: 'bg-purple-100 text-purple-700 border-purple-300',
  blue: 'bg-blue-100 text-blue-700 border-blue-300',
  amber: 'bg-amber-100 text-amber-700 border-amber-300',
  green: 'bg-green-100 text-green-700 border-green-300',
  red: 'bg-red-100 text-red-700 border-red-300',
  gray: 'bg-gray-100 text-gray-700 border-gray-300',
};

export function SpecialistAvatar({ role, size = 'md' }: SpecialistAvatarProps) {
  if (role === 'user') {
    return (
      <div
        className={`${sizeClasses[size]} ${colorClasses.gray} rounded-full border flex items-center justify-center font-medium`}
      >
        U
      </div>
    );
  }

  const info = SPECIALIST_INFO[role];
  if (!info) return null;

  return (
    <div
      className={`${sizeClasses[size]} ${colorClasses[info.color]} rounded-full border flex items-center justify-center`}
      title={info.name}
    >
      {info.icon}
    </div>
  );
}
```

**Step 2: Create MessageBubble**

Create `frontend/src/components/chat/MessageBubble.tsx`:
```tsx
import { SpecialistAvatar } from './SpecialistAvatar';
import { SPECIALIST_INFO, type SpecialistRole } from '@/types';

interface MessageBubbleProps {
  role: SpecialistRole | 'user' | 'system';
  name?: string;
  content: string;
  isStreaming?: boolean;
}

export function MessageBubble({ role, name, content, isStreaming }: MessageBubbleProps) {
  const isUser = role === 'user';
  const displayName = isUser ? 'You' : name || SPECIALIST_INFO[role as SpecialistRole]?.name || role;

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <SpecialistAvatar role={role as SpecialistRole | 'user'} />
      <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
        <div className="text-xs text-gray-500 mb-1">{displayName}</div>
        <div
          className={`inline-block rounded-lg px-4 py-2 max-w-[80%] ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          <p className="whitespace-pre-wrap">{content}</p>
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
          )}
        </div>
      </div>
    </div>
  );
}
```

**Step 3: Create MessageStream**

Create `frontend/src/components/chat/MessageStream.tsx`:
```tsx
import { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import type { Message, SpecialistRole } from '@/types';

interface MessageStreamProps {
  messages: Message[];
  streamingMessage?: { role: string; name: string; content: string } | null;
}

export function MessageStream({ messages, streamingMessage }: MessageStreamProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          role={message.role as SpecialistRole | 'user'}
          name={message.metadata?.name}
          content={message.content}
        />
      ))}
      {streamingMessage && (
        <MessageBubble
          role={streamingMessage.role as SpecialistRole}
          name={streamingMessage.name}
          content={streamingMessage.content}
          isStreaming
        />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
```

**Step 4: Create ChatInput**

Create `frontend/src/components/chat/ChatInput.tsx`:
```tsx
import { useState, type FormEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="border-t p-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe what you want to create..."
          disabled={disabled}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          Send
        </button>
      </div>
    </form>
  );
}
```

**Step 5: Create index export**

Create `frontend/src/components/chat/index.ts`:
```typescript
export { MessageStream } from './MessageStream';
export { MessageBubble } from './MessageBubble';
export { SpecialistAvatar } from './SpecialistAvatar';
export { ChatInput } from './ChatInput';
```

**Step 6: Commit**

```bash
cd frontend && git add src/components/
git commit -m "feat: add chat components (MessageStream, MessageBubble, ChatInput)"
```

---

### Task 15: Create Chat Page

**Files:**
- Create: `frontend/src/app/chat/[id]/page.tsx`
- Modify: `frontend/src/app/page.tsx`

**Step 1: Create chat page**

```bash
mkdir -p frontend/src/app/chat/\[id\]
```

Create `frontend/src/app/chat/[id]/page.tsx`:
```tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { MessageStream, ChatInput } from '@/components/chat';
import { useSSE } from '@/hooks/useSSE';
import { getSession, createConversation, getMessages } from '@/lib/api';
import type { Session, Conversation } from '@/types';

export default function ChatPage() {
  const params = useParams();
  const sessionId = params.id as string;

  const [session, setSession] = useState<Session | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { messages, streamingMessage, isStreaming, sendMessage, setMessages } = useSSE();

  useEffect(() => {
    async function init() {
      try {
        const sess = await getSession(sessionId);
        setSession(sess);

        // Create a new conversation
        const conv = await createConversation(sessionId);
        setConversation(conv);

        // Load existing messages if any
        const msgs = await getMessages(conv.id);
        setMessages(msgs);
      } catch (e) {
        setError('Failed to initialize chat');
        console.error(e);
      } finally {
        setLoading(false);
      }
    }

    init();
  }, [sessionId, setMessages]);

  const handleSend = (content: string) => {
    if (!conversation) return;
    sendMessage(conversation.id, content);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b px-4 py-3 flex items-center justify-between">
        <h1 className="font-semibold">Creative Studio</h1>
        <span className="text-sm text-gray-500">
          Phase: {conversation?.status || 'ideation'}
        </span>
      </header>

      <MessageStream messages={messages} streamingMessage={streamingMessage} />

      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
```

**Step 2: Update landing page**

Replace `frontend/src/app/page.tsx`:
```tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createSession } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    try {
      // Create session with default model assignments
      const session = await createSession({
        style: 'llama3.2',
        composition: 'llama3.2',
        story: 'llama3.2',
        technical: 'llama3.2',
        critic: 'llama3.2',
      });
      router.push(`/chat/${session.id}`);
    } catch (e) {
      console.error('Failed to create session:', e);
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Creative Studio</h1>
      <p className="text-gray-600 mb-8 text-center max-w-md">
        Collaborate with AI specialists to create images and videos.
        Watch Luna, Frame, Saga, Pixel, and Lens work together on your vision.
      </p>
      <button
        onClick={handleStart}
        disabled={loading}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
      >
        {loading ? 'Creating session...' : 'Start Creating'}
      </button>
    </main>
  );
}
```

**Step 3: Commit**

```bash
cd frontend && git add src/app/
git commit -m "feat: add chat page with SSE integration"
```

---

## Phase 6: ComfyUI Integration

### Task 16: Create Workflow Builder

**Files:**
- Create: `backend/app/workflows/builder.py`
- Create: `backend/app/workflows/templates/basic_txt2img.json`

**Step 1: Create basic txt2img template**

Create `backend/app/workflows/templates/basic_txt2img.json`:
```json
{
  "3": {
    "inputs": {
      "seed": 0,
      "steps": 20,
      "cfg": 7,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler"
  },
  "4": {
    "inputs": {
      "ckpt_name": "sd_xl_base_1.0.safetensors"
    },
    "class_type": "CheckpointLoaderSimple"
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage"
  },
  "6": {
    "inputs": {
      "text": "",
      "clip": ["4", 1]
    },
    "class_type": "CLIPTextEncode"
  },
  "7": {
    "inputs": {
      "text": "ugly, blurry, low quality",
      "clip": ["4", 1]
    },
    "class_type": "CLIPTextEncode"
  },
  "8": {
    "inputs": {
      "samples": ["3", 0],
      "vae": ["4", 2]
    },
    "class_type": "VAEDecode"
  },
  "9": {
    "inputs": {
      "filename_prefix": "creative_studio",
      "images": ["8", 0]
    },
    "class_type": "SaveImage"
  }
}
```

**Step 2: Create workflow builder**

Create `backend/app/workflows/__init__.py`:
```python
```

Create `backend/app/workflows/builder.py`:
```python
import json
import random
from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_template(name: str) -> dict:
    """Load a workflow template by name."""
    template_path = TEMPLATES_DIR / f"{name}.json"
    with open(template_path) as f:
        return json.load(f)


def build_txt2img_workflow(
    prompt: str,
    negative_prompt: str = "ugly, blurry, low quality",
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    cfg: float = 7.0,
    seed: int | None = None,
    checkpoint: str = "sd_xl_base_1.0.safetensors",
    sampler: str = "euler",
) -> dict:
    """Build a txt2img workflow from parameters."""
    workflow = load_template("basic_txt2img")

    # Set seed (random if not provided)
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    # Update KSampler
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["steps"] = steps
    workflow["3"]["inputs"]["cfg"] = cfg
    workflow["3"]["inputs"]["sampler_name"] = sampler

    # Update checkpoint
    workflow["4"]["inputs"]["ckpt_name"] = checkpoint

    # Update latent size
    workflow["5"]["inputs"]["width"] = width
    workflow["5"]["inputs"]["height"] = height

    # Update prompts
    workflow["6"]["inputs"]["text"] = prompt
    workflow["7"]["inputs"]["text"] = negative_prompt

    return workflow


def parse_technical_parameters(technical_response: str) -> dict:
    """Parse Technical Director's response into workflow parameters."""
    params = {
        "steps": 20,
        "cfg": 7.0,
        "width": 1024,
        "height": 1024,
        "sampler": "euler",
    }

    response_lower = technical_response.lower()

    # Parse steps
    if "steps" in response_lower:
        for word in response_lower.split():
            if word.isdigit() and 10 <= int(word) <= 150:
                params["steps"] = int(word)
                break

    # Parse CFG
    if "cfg" in response_lower:
        for word in response_lower.split():
            try:
                val = float(word)
                if 1 <= val <= 30:
                    params["cfg"] = val
                    break
            except ValueError:
                continue

    # Parse resolution keywords
    if "portrait" in response_lower:
        params["width"] = 768
        params["height"] = 1024
    elif "landscape" in response_lower:
        params["width"] = 1024
        params["height"] = 768
    elif "square" in response_lower:
        params["width"] = 1024
        params["height"] = 1024

    # Parse sampler
    samplers = ["euler", "euler_ancestral", "dpm++", "ddim", "heun"]
    for sampler in samplers:
        if sampler in response_lower:
            params["sampler"] = sampler
            break

    return params
```

**Step 3: Commit**

```bash
git add backend/app/workflows/
git commit -m "feat: add ComfyUI workflow builder with txt2img template"
```

---

### Task 17: Add Generation Route

**Files:**
- Create: `backend/app/api/routes/generations.py`
- Create: `backend/app/models/generation.py`

**Step 1: Create generation model**

Create `backend/app/models/generation.py`:
```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GenerationCreate(BaseModel):
    conversation_id: UUID
    prompt: str
    negative_prompt: str = "ugly, blurry, low quality"
    parameters: dict = {}


class Generation(BaseModel):
    id: UUID
    conversation_id: UUID
    workflow_json: dict | None
    parameters: dict
    status: str
    progress: int
    error: str | None
    created_at: datetime

    class Config:
        from_attributes = True
```

Update `backend/app/models/__init__.py`:
```python
from .session import Session, SessionCreate, SessionUpdate
from .conversation import Conversation, ConversationCreate
from .message import Message, MessageCreate
from .generation import Generation, GenerationCreate

__all__ = [
    "Session", "SessionCreate", "SessionUpdate",
    "Conversation", "ConversationCreate",
    "Message", "MessageCreate",
    "Generation", "GenerationCreate",
]
```

**Step 2: Create generations route**

Create `backend/app/api/routes/generations.py`:
```python
import asyncio
from uuid import UUID

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.api.deps import get_db, get_comfyui
from app.models.generation import Generation, GenerationCreate
from app.workflows.builder import build_txt2img_workflow
from app.services.supabase import get_supabase_client

router = APIRouter(prefix="/generations", tags=["generations"])


async def run_generation(generation_id: str, workflow: dict):
    """Background task to run generation and poll for completion."""
    db = get_supabase_client()
    comfyui = get_comfyui()

    try:
        # Update status to running
        db.table("generations").update({
            "status": "running",
            "progress": 0,
        }).eq("id", generation_id).execute()

        # Queue workflow
        prompt_id = await comfyui.queue_workflow(workflow)

        # Poll for completion
        max_attempts = 300  # 5 minutes max
        for attempt in range(max_attempts):
            progress = await comfyui.get_progress(prompt_id)

            if progress["status"] == "complete":
                # Get output images
                outputs = progress.get("outputs", {})

                db.table("generations").update({
                    "status": "complete",
                    "progress": 100,
                    "parameters": {**outputs, "prompt_id": prompt_id},
                }).eq("id", generation_id).execute()
                return

            # Update progress (estimated)
            estimated_progress = min(95, (attempt / max_attempts) * 100)
            db.table("generations").update({
                "progress": int(estimated_progress),
            }).eq("id", generation_id).execute()

            await asyncio.sleep(1)

        # Timeout
        db.table("generations").update({
            "status": "failed",
            "error": "Generation timed out",
        }).eq("id", generation_id).execute()

    except Exception as e:
        db.table("generations").update({
            "status": "failed",
            "error": str(e),
        }).eq("id", generation_id).execute()


@router.post("/", response_model=Generation)
async def create_generation(data: GenerationCreate, background_tasks: BackgroundTasks):
    db = get_db()

    # Build workflow
    workflow = build_txt2img_workflow(
        prompt=data.prompt,
        negative_prompt=data.negative_prompt,
        **data.parameters,
    )

    # Create generation record
    result = db.table("generations").insert({
        "conversation_id": str(data.conversation_id),
        "workflow_json": workflow,
        "parameters": data.parameters,
        "status": "queued",
        "progress": 0,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create generation")

    generation = result.data[0]

    # Start background generation
    background_tasks.add_task(run_generation, generation["id"], workflow)

    return generation


@router.get("/{generation_id}", response_model=Generation)
async def get_generation(generation_id: UUID):
    db = get_db()
    result = db.table("generations").select("*").eq("id", str(generation_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Generation not found")

    return result.data[0]


@router.get("/conversation/{conversation_id}")
async def get_conversation_generations(conversation_id: UUID):
    db = get_db()
    result = db.table("generations")\
        .select("*")\
        .eq("conversation_id", str(conversation_id))\
        .order("created_at", desc=True)\
        .execute()

    return result.data
```

**Step 3: Register route**

Update `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import sessions, chat, generations

app = FastAPI(
    title="Creative Studio API",
    description="Multi-model orchestration for image/video generation",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(sessions.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(generations.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "debug": settings.debug}
```

**Step 4: Commit**

```bash
git add backend/app/api/routes/generations.py backend/app/models/generation.py backend/app/main.py
git commit -m "feat: add generation API with background ComfyUI execution"
```

---

## Phase 7: Polish & Integration

### Task 18: Add Settings Page

**Files:**
- Create: `frontend/src/app/settings/page.tsx`
- Create: `frontend/src/components/settings/ModelSelector.tsx`

**Step 1: Create ModelSelector component**

```bash
mkdir -p frontend/src/components/settings
```

Create `frontend/src/components/settings/ModelSelector.tsx`:
```tsx
'use client';

import { SPECIALIST_INFO, type SpecialistRole } from '@/types';

interface ModelSelectorProps {
  role: SpecialistRole;
  value: string;
  onChange: (value: string) => void;
  availableModels: string[];
}

export function ModelSelector({ role, value, onChange, availableModels }: ModelSelectorProps) {
  const info = SPECIALIST_INFO[role];

  return (
    <div className="flex items-center gap-4 p-4 border rounded-lg">
      <div className="text-2xl">{info.icon}</div>
      <div className="flex-1">
        <div className="font-medium">{info.name}</div>
        <div className="text-sm text-gray-500 capitalize">{role} Specialist</div>
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border rounded-lg px-3 py-2"
      >
        {availableModels.map((model) => (
          <option key={model} value={model}>
            {model}
          </option>
        ))}
      </select>
    </div>
  );
}
```

**Step 2: Create settings page**

Create `frontend/src/app/settings/page.tsx`:
```tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ModelSelector } from '@/components/settings/ModelSelector';
import { getSession } from '@/lib/api';
import type { SpecialistRole } from '@/types';

const SPECIALIST_ROLES: SpecialistRole[] = ['style', 'composition', 'story', 'technical', 'critic'];
const DEFAULT_MODELS = ['llama3.2', 'llama3.1', 'mistral', 'phi3', 'gemma2'];

export default function SettingsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session');

  const [assignments, setAssignments] = useState<Record<string, string>>({
    style: 'llama3.2',
    composition: 'llama3.2',
    story: 'llama3.2',
    technical: 'llama3.2',
    critic: 'llama3.2',
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (sessionId) {
      getSession(sessionId).then((session) => {
        if (session.model_assignments) {
          setAssignments({ ...assignments, ...session.model_assignments });
        }
      });
    }
  }, [sessionId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${API_URL}/api/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_assignments: assignments }),
      });
      router.push(`/chat/${sessionId}`);
    } catch (e) {
      console.error('Failed to save:', e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Model Settings</h1>
      <p className="text-gray-600 mb-8">
        Assign Ollama models to each specialist role
      </p>

      <div className="space-y-4 mb-8">
        {SPECIALIST_ROLES.map((role) => (
          <ModelSelector
            key={role}
            role={role}
            value={assignments[role]}
            onChange={(value) => setAssignments({ ...assignments, [role]: value })}
            availableModels={DEFAULT_MODELS}
          />
        ))}
      </div>

      <div className="flex gap-4">
        <button
          onClick={() => router.back()}
          className="px-6 py-2 border rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {saving ? 'Saving...' : 'Save & Continue'}
        </button>
      </div>
    </main>
  );
}
```

**Step 3: Commit**

```bash
cd frontend && git add src/app/settings/ src/components/settings/
git commit -m "feat: add settings page for model assignments"
```

---

### Task 19: Add Generation Preview Component

**Files:**
- Create: `frontend/src/components/generation/GenerationPreview.tsx`
- Create: `frontend/src/components/generation/ProgressBar.tsx`

**Step 1: Create ProgressBar**

```bash
mkdir -p frontend/src/components/generation
```

Create `frontend/src/components/generation/ProgressBar.tsx`:
```tsx
interface ProgressBarProps {
  progress: number;
  status: string;
}

export function ProgressBar({ progress, status }: ProgressBarProps) {
  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-1">
        <span className="capitalize">{status}</span>
        <span>{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
```

**Step 2: Create GenerationPreview**

Create `frontend/src/components/generation/GenerationPreview.tsx`:
```tsx
'use client';

import { useState, useEffect } from 'react';
import { ProgressBar } from './ProgressBar';

interface Generation {
  id: string;
  status: 'queued' | 'running' | 'complete' | 'failed';
  progress: number;
  parameters?: {
    prompt_id?: string;
    images?: Array<{ filename: string; subfolder: string }>;
  };
  error?: string;
}

interface GenerationPreviewProps {
  conversationId: string;
}

export function GenerationPreview({ conversationId }: GenerationPreviewProps) {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGenerations = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/generations/conversation/${conversationId}`);
        if (res.ok) {
          setGenerations(await res.json());
        }
      } catch (e) {
        console.error('Failed to fetch generations:', e);
      } finally {
        setLoading(false);
      }
    };

    fetchGenerations();

    // Poll for updates
    const interval = setInterval(fetchGenerations, 2000);
    return () => clearInterval(interval);
  }, [conversationId]);

  if (loading) {
    return <div className="p-4 text-gray-500">Loading generations...</div>;
  }

  if (generations.length === 0) {
    return null;
  }

  return (
    <div className="border-t p-4 space-y-4">
      <h3 className="font-medium">Generations</h3>
      {generations.map((gen) => (
        <div key={gen.id} className="border rounded-lg p-4">
          {gen.status === 'running' || gen.status === 'queued' ? (
            <ProgressBar progress={gen.progress} status={gen.status} />
          ) : gen.status === 'failed' ? (
            <div className="text-red-500">Failed: {gen.error}</div>
          ) : gen.status === 'complete' ? (
            <div className="text-green-600">Complete! Check ComfyUI output folder.</div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
```

**Step 3: Create index export**

Create `frontend/src/components/generation/index.ts`:
```typescript
export { GenerationPreview } from './GenerationPreview';
export { ProgressBar } from './ProgressBar';
```

**Step 4: Commit**

```bash
cd frontend && git add src/components/generation/
git commit -m "feat: add generation preview with progress tracking"
```

---

### Task 20: Final Integration and README

**Files:**
- Create: `README.md`
- Verify all components work together

**Step 1: Create README**

Create `README.md`:
```markdown
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
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

**Step 3: Final verification**

```bash
# Verify project structure
ls -la
ls -la backend/
ls -la frontend/
ls -la supabase/
```

---

## Summary

This plan creates a complete Creative Studio platform with:

1. **Phase 1**: Project foundation (FastAPI backend, Next.js frontend, Supabase)
2. **Phase 2**: Core services (Supabase, Ollama, ComfyUI clients)
3. **Phase 3**: Specialists and orchestration engine
4. **Phase 4**: API routes (sessions, chat with SSE, generations)
5. **Phase 5**: Frontend chat interface
6. **Phase 6**: ComfyUI workflow integration
7. **Phase 7**: Settings, generation preview, documentation

Each task follows TDD principles with exact file paths, complete code, and commit points.
