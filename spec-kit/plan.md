# AV-Studio Architecture Plan
## Technical Blueprint for Implementation

**Version:** 1.0.0  
**Status:** DRAFT → Awaiting GATE-2 Approval  
**Author:** Architect Agent | Reviewed by: Claude, Gemini

---

## 1. System Architecture

### 1.1 High-Level Component Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              AV-STUDIO                                      │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                         INTERFACE LAYER                              │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │  │
│  │  │  REST API │  │ WebSocket │  │    CLI    │  │    MCP    │        │  │
│  │  │ (FastAPI) │  │  (Real-   │  │  (Typer)  │  │  Server   │        │  │
│  │  │           │  │   time)   │  │           │  │           │        │  │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └───��─┬─────┘        │  │
│  └────────┼──────────────┼──────────────┼──────────────┼───────────────┘  │
│           └──────────────┴──────────────┴──────────────┘                   │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────────────┐  │
│  │                         GATEWAY LAYER                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │    Router    │  │   Auth &     │  │    Cost &    │               │  │
│  │  │  (Smart      │  │   Rate       │  │    Token     │               │  │
│  │  │   Model      │  │   Limiter    │  │   Analyzer   │               │  │
│  │  │   Selection) │  │              │  │              │               │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │  │
│  └─────────────────────────────────┬────────────────────────────────────┘  │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────────────┐  │
│  │                         AGENT LAYER                                  │  │
│  │                                                                      │  │
│  │   ┌─────────────────────────────────────────────────────────────┐   │  │
│  │   │                    ORCHESTRATOR                              │   │  │
│  │   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │   │  │
│  │   │  │ State   │  │ Task    │  │ Memory  │  │ Event   │        │   │  │
│  │   │  │ Machine │  │ Queue   │  │ Store   │  │ Bus     │        │   │  │
│  │   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │   │  │
│  │   └─────────────────────────────────────────────────────────────┘   │  │
│  │                                                                      │  │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │   │  Audio   │  │  Video   │  │ Research │  │  General │           │  │
│  │   │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │           │  │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘           │  │
│  └─────────────────────────────────┬────────────────────────────────────┘  │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────────────┐  │
│  │                       PROCESSING LAYER                               │  │
│  │                                                                      │  │
│  │  ┌─────────────────────────┐    ┌─────────────────────────┐         │  │
│  │  │    AUDIO PIPELINE       │    │    VIDEO PIPELINE       │         │  │
│  │  │  ┌───────┐ ┌───────┐   │    │  ┌───────┐ ┌───────┐   │         │  │
│  │  │  │Demucs │ │Whisper│   │    │  │Torch  │ │OpenCV │   │         │  │
│  │  │  │(MPS)  │ │(CPU)  │   │    │  │Codec  │ │(CPU)  │   │         │  │
│  │  │  └───────┘ └───────┘   │    │  └───────┘ └───────┘   │         │  │
│  │  │  ┌───────┐ ┌───────┐   │    │  ┌───────┐             │         │  │
│  │  │  │Pedal  │ │Librosa│   │    │  │Effects│             │         │  │
│  │  │  │board  │ │       │   │    │  │       │             │         │  │
│  │  │  └───────┘ └───────┘   │    │  └───────┘             │         │  │
│  │  └─────────────────────────┘    └─────────────────────────┘         │  │
│  │                                                                      │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │                    LLM PIPELINE                              │    │  │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │    │  │
│  │  │  │   MLX   │  │ Ollama  │  │ OpenAI  │  │ Claude  │        │    │  │
│  │  │  │ (Metal) │  │ (Local) │  │  (API)  │  │  (API)  │        │    │  │
│  │  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────────────┐  │
│  │                        STORAGE LAYER                                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │ SQLite   │  │ ChromaDB │  │  File    │  │  Redis   │             │  │
│  │  │ (Meta)   │  │ (Vector) │  │  System  │  │ (Cache)  │             │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │  │
│  └────────────────────────────────────────────���─────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Interface Layer

#### REST API (FastAPI)
```python
# Endpoints Structure
/api/v1/
├── /audio/
│   ├── POST /separate          # Stem separation
│   ├── POST /transcribe        # Speech-to-text
│   ├── POST /effects           # Apply effects
│   └── POST /normalize         # Loudness normalization
├── /video/
│   ├── POST /decode            # Decode video
│   ├── POST /extract-audio     # Extract audio track
│   └── POST /analyze           # Scene detection
├── /llm/
│   ├── POST /chat              # Chat completion
│   ├── POST /stream            # Streaming chat
│   └── GET  /models            # List available models
├── /agents/
│   ├── POST /task              # Submit task to agent
│   ├── GET  /task/{id}         # Get task status
│   └── WS   /stream/{id}       # Stream task updates
├── /gateway/
│   ├── GET  /cost              # Get cost summary
│   ├── GET  /tokens            # Token analysis
│   └── POST /route             # Get routing decision
└── /system/
    ├── GET  /health            # Health check
    └── GET  /metrics           # Prometheus metrics
```

#### WebSocket Protocol
```yaml
events:
  task.started:
    payload: { task_id, type, started_at }
  task.progress:
    payload: { task_id, percent, message }
  task.completed:
    payload: { task_id, result, duration }
  task.failed:
    payload: { task_id, error, traceback }
  llm.token:
    payload: { request_id, token, done }
  agent.message:
    payload: { agent, message, metadata }
```

### 2.2 Gateway Layer

#### Smart Router Algorithm
```python
def route(task: Task) -> Model:
    """
    Selection Priority:
    1. If task.require_local → MLX or Ollama
    2. If estimated_cost > budget_threshold → Local
    3. If task.require_quality > 0.9 → Claude/GPT-4o
    4. If task.type == CODE → Qwen-Coder or Copilot
    5. If task.type == CREATIVE → Mistral or Claude
    6. Default → MLX (free, fast)
    """
```

### 2.3 Agent Layer

#### Agent Communication Protocol
```yaml
message_format:
  id: uuid
  from_agent: string
  to_agent: string | "broadcast"
  type: "request" | "response" | "event"
  payload:
    action: string
    params: object
    context: object
  metadata:
    timestamp: datetime
    priority: int
    correlation_id: uuid
```

#### Orchestrator State Machine
```python
class TaskState(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

transitions = {
    PENDING: [ASSIGNED, BLOCKED],
    ASSIGNED: [IN_PROGRESS, BLOCKED],
    IN_PROGRESS: [AWAITING_REVIEW, FAILED, BLOCKED],
    AWAITING_REVIEW: [COMPLETED, IN_PROGRESS],  # Back if review fails
    FAILED: [PENDING],  # Retry
    BLOCKED: [PENDING],  # Unblock
}
```

### 2.4 Processing Layer

#### GPU Memory Management
```python
# M4 Max has 36GB unified memory
# Reserve allocations:
MEMORY_BUDGET = {
    "demucs": 8_000,      # 8GB for stem separation
    "whisper": 4_000,     # 4GB for large-v3
    "mlx_llm": 12_000,    # 12GB for 70B quantized
    "opencv": 2_000,      # 2GB for video processing
    "system": 10_000,     # 10GB for OS + overhead
}

# Sequential processing for large models
# Parallel only for small models that fit together
```

### 2.5 Storage Layer

#### Database Schema Summary
```sql
-- Core entities
projects, media_files, tasks, jobs

-- Agent system
agents, agent_messages, agent_memory

-- Cost tracking
api_calls, token_usage, cost_records

-- Results
transcriptions, stem_separations, effects_applied
```

---

## 3. Data Flow Diagrams

### 3.1 Audio Stem Separation Flow
```
User Request
     │
     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   REST API  │────▶│   Gateway   │────▶│   Router    │
└─────────────┘     │  Validate   │     │  Assign to  │
                    │  Auth       │     │  Local GPU  │
                    └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐             │
                    │   Audio     │◀────────────┘
                    │   Agent     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Demucs    │
                    │   (MPS)     │
                    │  GPU Accel  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐  ┌────────┐  ┌────────┐
         │ Vocals │  │ Drums  │  │  Bass  │ ...
         └────────┘  └────────┘  └────────┘
              │            │            │
              └────────────┴────────────┘
                           │
                    ┌──────▼──────┐
                    │   Storage   │
                    │  Save Stems │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  WebSocket  │
                    │  Notify     │
                    └─────────────┘
```

### 3.2 Agent Task Execution Flow
```
User: "Separate this song and transcribe the vocals"
                    │
                    ▼
            ┌───────────────┐
            │  Coordinator  │
            │    Agent      │
            └───────┬───────┘
                    │ Decompose into subtasks
                    ▼
        ┌───────────────────────┐
        │      Task Queue       │
        │  1. separate_stems    │
        │  2. transcribe_vocals │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│  Audio Agent  │       │  Audio Agent  │
│  Task 1       │       │  Task 2       │
│  (parallel if │       │  (waits for   │
│   possible)   │       │   Task 1)     │
└───────┬───────┘       └───────┬───────┘
        │                       │
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│    Demucs     │       │   Whisper     │
│   Separate    │──────▶│  Transcribe   │
└───────────────┘ vocals└───────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
            ┌───────────────┐
            │  Coordinator  │
            │  Synthesize   │
            │   Results     │
            └───────────────┘
```

---

## 4. Security Architecture

### 4.1 Authentication Flow
```
┌──────────┐      ┌──────────┐      ┌──────────┐
│  Client  │─────▶│  Gateway │─────▶│   Auth   │
│          │      │          │      │  Service │
└──────────┘      └──────────┘      └────┬─────┘
                                         │
                       ┌─────────────────┴─────────────────┐
                       ▼                                   ▼
               ┌───────────────┐                   ┌───────────────┐
               │   API Key     │                   │     JWT       │
               │   (Simple)    │                   │   (Sessions)  │
               └───────────────┘                   └───────────────┘
```

### 4.2 Secret Management
```yaml
secrets:
  storage: macOS Keychain
  access: 
    - Environment variables at runtime
    - Never committed to git
    - Rotated monthly
  
  required_secrets:
    - OPENAI_API_KEY
    - ANTHROPIC_API_KEY
    - GOOGLE_API_KEY
    - ELEVENLABS_API_KEY
    - JWT_SECRET
```

---

## 5. Deployment Architecture

### 5.1 Local Development
```yaml
services:
  av-studio:
    runtime: Python 3.12
    server: Uvicorn
    host: localhost
    port: 8000
    
  ollama:
    runtime: Native binary
    host: localhost
    port: 11434
    
  redis:
    runtime: Docker or native
    host: localhost
    port: 6379
    
  chromadb:
    runtime: Embedded (Python)
    path: ~/.av-studio/chroma
```

### 5.2 Process Supervision
```yaml
supervisor: launchd (macOS native)

services:
  - name: av-studio-api
    command: uvicorn av_studio.main:app
    auto_restart: true
    
  - name: av-studio-mcp
    command: python -m av_studio.mcp.server
    auto_restart: true
    
  - name: ollama
    command: ollama serve
    auto_restart: true
```

---

## 6. Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API Framework | FastAPI | Async native, auto OpenAPI docs, fast |
| Local LLM | MLX primary, Ollama backup | MLX is fastest on Apple Silicon |
| Vector DB | ChromaDB | Embedded, simple, sufficient for local |
| Cache | Redis | Fast, optional (can use in-memory) |
| Task Queue | asyncio.Queue | Simple, sufficient for local single-user |
| Database | SQLite | Zero config, fast for local use |
| MCP | Official SDK | Standard protocol, future-proof |

---

## 7. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| GPU memory exhaustion | Sequential processing for large models; memory monitoring |
| External API outage | Local fallbacks for all critical functions |
| Cost overrun | Hard limits in gateway; alerts at 60% |
| Data loss | Auto-save; journaling; backup to iCloud (optional) |
| Model quality regression | Pinned versions; benchmark suite |

---

**Approval Chain:**
- [ ] Architect Agent: Drafted
- [ ] Claude: Technical Review ✓
- [ ] Gemini: Cross-validation Review ✓
- [ ] Human Director (@scotlaclair): **GATE-2 APPROVAL REQUIRED**