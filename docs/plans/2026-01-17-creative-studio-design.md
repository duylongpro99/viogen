# Creative Studio: Multi-Model Orchestration Platform

## Overview

A chat-based creative studio where users collaborate with a team of AI specialists to generate images and videos. Users type requests naturally, watch the AI team discuss and plan in real-time, and can jump in anytime to steer the creative direction.

**Key Technologies:**
- **Ollama** - Runs multiple Small Language Models as specialists
- **ComfyUI** - Handles actual image/video generation
- **FastAPI** - Python backend with SSE streaming
- **Next.js** - React frontend for chat interface
- **Supabase** - PostgreSQL database + file storage (local Docker for dev)

---

## User Experience

### Core Flow

1. User opens the app and sees a chat interface
2. User types: "Create a cyberpunk street scene at night with neon signs"
3. The 5 specialists begin discussing - their conversation streams in real-time:
   - *Style Specialist:* "I'm thinking high contrast, neon pinks and blues against dark shadows..."
   - *Composition Expert:* "Low angle shot would emphasize the towering buildings..."
   - *Story Guide:* "Let's add a lone figure to create narrative tension..."
4. User can interject anytime: "I want it more rainy and melancholic"
5. Specialists adapt and continue refining
6. Technical Director synthesizes into ComfyUI parameters
7. Quality Critic reviews the plan, suggests improvements
8. Generation happens, result appears in chat
9. User iterates: "Make the neon signs brighter" → specialists discuss adjustments → regenerate

### Key UX Principles

- Conversation feels natural, not like filling forms
- Specialists have distinct personalities/voices
- User is a collaborator, not just a requester

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React/Next.js Frontend                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Chat View  │  │  Settings   │  │  Generation Gallery │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │ SSE (down) / HTTP (up)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Python Backend (FastAPI)                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Orchestration Engine                    │    │
│  │  - Manages conversation flow between specialists     │    │
│  │  - Handles user interjections                        │    │
│  │  - Decides when to move to generation                │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Ollama Client│  │ComfyUI Client│  │  Session Manager  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  Ollama Server  │  │  ComfyUI Server │
│  (Local SLMs)   │  │  (Generation)   │
└─────────────────┘  └─────────────────┘
```

### Key Design Decisions

- **FastAPI** for the Python backend - async support, great for SSE streaming
- **Orchestration Engine** is the brain - it coordinates which specialist speaks next, when to pause for user input, and when consensus is reached
- **Session Manager** tracks conversation history, user preferences, and model assignments per session
- **Stateless specialists** - each specialist call includes full context, making it easy to swap models
- **SSE (Server-Sent Events)** for real-time streaming - simpler than WebSockets, one-way from server to client

---

## Orchestration Engine

### Conversation Phases

**1. Ideation Phase** - Open discussion after user prompt
- Style, Composition, and Story specialists explore freely
- Engine encourages divergent thinking
- Lasts until initial concepts emerge (or user intervenes)

**2. Refinement Phase** - Narrowing down
- Specialists respond to each other's ideas
- Engine prompts for specifics: "Style, what exact color palette?"
- User interjections prioritized here

**3. Synthesis Phase** - Technical Director takes lead
- Translates creative consensus into ComfyUI workflow
- Specifies: model, sampler, CFG, LoRAs, control nets, etc.
- Other specialists can object/suggest adjustments

**4. Review Phase** - Quality Critic evaluates
- Reviews the full plan before generation
- Can send back to earlier phases if issues found

### Handling User Interjections

- User messages get priority - engine pauses current flow
- Relevant specialists respond to user directly
- Conversation resumes with new direction incorporated

### Consensus Detection

- Engine tracks when specialists stop introducing new ideas
- Prompts: "Team, are we ready to generate?"
- Moves to synthesis if no objections

---

## The Five Specialists

Each specialist has a distinct role, personality, and prompt structure:

### 1. Style Specialist (Luna)
- **Focus:** Artistic style, mood, color theory, lighting, visual aesthetics
- **Personality:** Expressive, uses vivid descriptive language
- **Outputs:** Style keywords, color palettes, artistic references, mood descriptors
- **Example:** "I see this with a Blade Runner 2049 palette - deep teals against warm ambers, volumetric fog catching neon light..."

### 2. Composition Expert (Frame)
- **Focus:** Layout, camera angle, framing, visual hierarchy, depth
- **Personality:** Precise, thinks in spatial terms
- **Outputs:** Camera position, focal length, rule-of-thirds placement, foreground/background elements
- **Example:** "Low angle, 35mm equivalent, subject at left third intersection, leading lines from the wet street drawing eye to the background..."

### 3. Story/Narrative Guide (Saga)
- **Focus:** Emotional context, narrative elements, scene meaning, character intent
- **Personality:** Thoughtful, asks "why" questions
- **Outputs:** Scene context, character motivations, emotional beats, story hooks
- **Example:** "What if they're waiting for someone who won't come? That loneliness would inform everything..."

### 4. Technical Director (Pixel)
- **Focus:** ComfyUI parameters, model selection, technical feasibility
- **Personality:** Practical, translates ideas into specs
- **Outputs:** Workflow nodes, model choices, sampler settings, LoRA suggestions

### 5. Quality Critic (Lens)
- **Focus:** Coherence, potential issues, improvement suggestions
- **Personality:** Constructive but thorough
- **Outputs:** Risk flags, enhancement ideas, consistency checks

### Model Assignment

Users can assign different Ollama models to each specialist role based on their hardware and preferences. Configuration stored per session.

---

## ComfyUI Integration

### Workflow Templates

- Pre-built ComfyUI workflow templates stored as JSON
- Templates for common scenarios: basic image, image-to-image, video generation, upscaling
- Technical Director selects and modifies templates based on team consensus

### Dynamic Workflow Building

```
Specialist Consensus → Technical Director → Workflow JSON → ComfyUI API
```

### Parameter Mapping

| Creative Concept | ComfyUI Parameter |
|------------------|-------------------|
| Style intensity | CFG Scale |
| Artistic style | Checkpoint model, LoRAs |
| Color mood | Positive/negative prompts |
| Composition | ControlNet, initial latent |
| Quality level | Steps, sampler, resolution |
| Video motion | AnimateDiff settings |

### ComfyUI API Integration

- Connect via ComfyUI's REST API (default port 8188)
- Queue workflow, poll for progress
- Stream progress updates to frontend ("Generating... 45%")
- Retrieve output images/videos when complete

### Error Handling

- If ComfyUI fails, Quality Critic analyzes the error
- Team adjusts parameters and retries
- User informed throughout: "Generation failed due to memory - Pixel is reducing resolution..."

---

## Data Model (Supabase)

### Tables

**sessions**
```sql
- id: uuid primary key
- created_at: timestamptz
- model_assignments: jsonb  -- { "style": "mistral", "composition": "llama3.2", ... }
- settings: jsonb           -- user preferences
```

**conversations**
```sql
- id: uuid primary key
- session_id: uuid references sessions
- status: text              -- ideation | refinement | synthesis | review | generating | complete
- created_at: timestamptz
- updated_at: timestamptz
```

**messages**
```sql
- id: uuid primary key
- conversation_id: uuid references conversations
- role: text                -- user | style | composition | story | technical | critic | system
- content: text
- metadata: jsonb
- created_at: timestamptz
```

**generations**
```sql
- id: uuid primary key
- conversation_id: uuid references conversations
- workflow_json: jsonb
- parameters: jsonb
- status: text              -- queued | running | complete | failed
- progress: integer
- error: text
- created_at: timestamptz
```

### Supabase Storage

- Bucket: `generations` - stores output images/videos
- Path structure: `{session_id}/{generation_id}/{filename}`

### Development Setup

- Local Supabase via `supabase start` (runs in Docker)
- Same schema/migrations work locally and in production

---

## Frontend Structure (Next.js)

### Pages/Routes

```
/                    → Landing/new session
/chat/[sessionId]    → Main chat interface
/settings            → Model assignments, preferences
/gallery             → Browse past generations
```

### Main Chat Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Header: Session name | Settings gear | New chat button    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Message Stream                      │   │
│  │                                                      │   │
│  │  [User] Create a cyberpunk street scene...          │   │
│  │                                                      │   │
│  │  [Luna/Style] I'm envisioning deep teals...         │   │
│  │                                                      │   │
│  │  [Frame/Composition] Low angle would work...        │   │
│  │                                                      │   │
│  │  [Saga/Story] What if there's tension...            │   │
│  │                                                      │   │
│  │  (typing indicator when specialists active)         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  [Type your message... ]              [Send button] │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Generation Preview: [Image/Video output displays here]    │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- `MessageStream` - Renders conversation with role-based styling
- `SpecialistAvatar` - Visual identity per specialist (color, icon)
- `GenerationPreview` - Shows output with iteration controls
- `ModelSelector` - Dropdown per role in settings

### State Management

- React Context for session state
- SSE hook for streaming messages
- Optimistic updates for user messages

---

## Error Handling & Edge Cases

### Ollama Failures

- Model not found → Prompt user to pull model or select different one
- Ollama server down → Clear error message, retry button, check connection guide
- Model timeout → Increase timeout setting or suggest smaller model

### ComfyUI Failures

- Out of memory → Technical Director auto-reduces resolution, retries
- Missing model/LoRA → Inform user, suggest alternatives or skip
- Server unreachable → Guide user to start ComfyUI, show connection status

### Orchestration Edge Cases

- Specialists stuck in loop → Engine detects repetition, forces phase advancement
- No consensus after N rounds → Engine summarizes options, asks user to decide
- User inactive too long → Pause orchestration, resume when user returns

### Network/SSE Issues

- SSE connection dropped → Auto-reconnect, fetch missed messages via HTTP
- Partial message received → Buffer until complete, show loading state

### User Experience Guards

- Generation taking too long → Show progress, allow cancel
- User rapid-fires messages → Queue and process in order
- Empty/unclear prompts → Specialists ask clarifying questions before proceeding

### Graceful Degradation

- If one specialist's model fails → Others continue, note the gap
- If ComfyUI down → Allow brainstorming, queue generation for later

---

## Project Structure

```
creative-studio/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Environment config
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── chat.py         # SSE streaming, message handling
│   │   │   │   ├── sessions.py     # Session CRUD
│   │   │   │   ├── generations.py  # Generation status, outputs
│   │   │   │   └── settings.py     # Model assignments, preferences
│   │   │   └── deps.py             # Dependency injection
│   │   ├── core/
│   │   │   ├── orchestrator.py     # Main orchestration engine
│   │   │   ├── specialists/
│   │   │   │   ├── base.py         # Base specialist class
│   │   │   │   ├── style.py        # Luna
│   │   │   │   ├── composition.py  # Frame
│   │   │   │   ├── story.py        # Saga
│   │   │   │   ├── technical.py    # Pixel
│   │   │   │   └── critic.py       # Lens
│   │   │   └── phases.py           # Phase management logic
│   │   ├── services/
│   │   │   ├── ollama.py           # Ollama API client
│   │   │   ├── comfyui.py          # ComfyUI API client
│   │   │   └── supabase.py         # Supabase client wrapper
│   │   ├── models/
│   │   │   ├── session.py          # Pydantic models
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   └── generation.py
│   │   └── workflows/
│   │       ├── templates/          # ComfyUI workflow JSONs
│   │       └── builder.py          # Dynamic workflow construction
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Landing
│   │   │   ├── chat/[id]/page.tsx  # Main chat
│   │   │   ├── settings/page.tsx
│   │   │   └── gallery/page.tsx
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── MessageStream.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── SpecialistAvatar.tsx
│   │   │   │   └── ChatInput.tsx
│   │   │   ├── generation/
│   │   │   │   ├── GenerationPreview.tsx
│   │   │   │   └── ProgressBar.tsx
│   │   │   └── settings/
│   │   │       └── ModelSelector.tsx
│   │   ├── hooks/
│   │   │   ├── useSSE.ts           # SSE connection hook
│   │   │   ├── useSession.ts
│   │   │   └── useGeneration.ts
│   │   ├── lib/
│   │   │   ├── api.ts              # Backend API client
│   │   │   └── supabase.ts         # Supabase client
│   │   └── types/
│   │       └── index.ts            # TypeScript types
│   ├── package.json
│   └── Dockerfile
│
├── supabase/
│   ├── migrations/                 # SQL migrations
│   ├── seed.sql                    # Dev seed data
│   └── config.toml                 # Local Supabase config
│
├── docker-compose.yml              # Local dev: Supabase + backend + frontend
├── .env.example
└── README.md
```

---

## Next Steps

1. Set up git repository and initial project structure
2. Create detailed implementation plan using superpowers:writing-plans
3. Begin with backend orchestration engine as foundation
4. Build frontend chat interface with mock responses
5. Integrate Ollama and ComfyUI services
6. Add Supabase persistence layer
