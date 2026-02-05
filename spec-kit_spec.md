# AV-Studio Master Specification
## AI-Powered Audio/Video Production Studio for M4 Max

**Version:** 1.0.0  
**Status:** DRAFT → Awaiting GATE-1 Approval  
**Author:** Planner Agent | Human Director: @scotlaclair

---

## 1. Executive Summary

AV-Studio is a local-first, AI-powered audio/video production platform optimized for Apple M4 Max. It combines state-of-the-art processing capabilities (Demucs, Whisper, MLX) with an intelligent agent system that can autonomously execute production workflows while maintaining human oversight at critical gates.

### 1.1 Core Value Propositions
1. **Professional Quality**: Studio-grade stem separation, mastering, transcription
2. **Local-First**: Maximize M4 Max GPU; minimize external API costs
3. **AI-Native**: Built-in agent orchestration for automated workflows
4. **Extensible**: MCP protocol for tool extension; plugin architecture
5. **Cost-Aware**: Smart routing minimizes API spend while maintaining quality

---

## 2. Functional Requirements

### 2.1 Audio Processing (P0 - Critical)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| AUD-001 | Stem separation | Separate audio into vocals, drums, bass, other using Demucs with MPS acceleration |
| AUD-002 | Transcription | Transcribe audio to text with timestamps using faster-whisper, >95% accuracy on clear speech |
| AUD-003 | Effects pipeline | Apply reverb, compression, EQ, gain via Pedalboard; real-time preview |
| AUD-004 | Loudness normalization | Normalize to configurable LUFS target (default -14 for streaming) |
| AUD-005 | Format conversion | Convert between WAV, MP3, FLAC, AAC, OGG with quality presets |
| AUD-006 | Batch processing | Process multiple files with configurable parallelism |

### 2.2 Video Processing (P1 - High)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| VID-001 | Fast decoding | Decode video using TorchCodec with hardware acceleration |
| VID-002 | Frame extraction | Extract frames at specified intervals or scene changes |
| VID-003 | Audio extraction | Extract audio track from video for processing |
| VID-004 | Scene detection | Detect scene changes using OpenCV |
| VID-005 | Basic effects | Apply color correction, stabilization, speed changes |

### 2.3 AI/LLM Integration (P0 - Critical)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| LLM-001 | Local inference | MLX-native LLM inference with <50ms first-token latency |
| LLM-002 | Ollama integration | Support Ollama models as fallback/alternative |
| LLM-003 | External routing | Smart routing to OpenAI/Claude/Gemini based on task |
| LLM-004 | Token analysis | Accurate token counting for all supported models |
| LLM-005 | Cost tracking | Real-time cost calculation with budget alerts |
| LLM-006 | Streaming | Stream LLM responses for responsive UX |

### 2.4 Agent System (P0 - Critical)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| AGT-001 | Coordinator agent | Route tasks to specialized agents; manage state |
| AGT-002 | Audio agent | Execute audio processing tasks autonomously |
| AGT-003 | Video agent | Execute video processing tasks autonomously |
| AGT-004 | Multi-agent chat | Agents can converse to solve complex problems |
| AGT-005 | Tool use | Agents can invoke MCP tools |
| AGT-006 | Memory | Persist conversation/task context |

### 2.5 API Gateway (P0 - Critical)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| GW-001 | REST API | FastAPI-based REST endpoints for all features |
| GW-002 | WebSocket | Real-time updates for long-running tasks |
| GW-003 | Authentication | API key and JWT authentication |
| GW-004 | Rate limiting | Configurable rate limits per endpoint |
| GW-005 | Smart routing | Automatic model selection based on cost/latency/quality |

### 2.6 MCP Server (P1 - High)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| MCP-001 | Tool registry | Register audio/video/LLM tools |
| MCP-002 | Resource serving | Serve project files, configurations |
| MCP-003 | Prompt templates | Reusable prompts for common tasks |
| MCP-004 | External tools | Integrate ElevenLabs, BMI, DistroKid APIs |

### 2.7 External Integrations (P2 - Medium)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| EXT-001 | ElevenLabs TTS | Generate speech from text with voice cloning |
| EXT-002 | BMI API | Query song registration, royalty data |
| EXT-003 | DistroKid API | Check distribution status, analytics |
| EXT-004 | Suno/Udio | Generate music from prompts (if APIs available) |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Stem separation (3min song) | <30 seconds | Wall clock time on M4 Max |
| Transcription (1min audio) | <10 seconds | Wall clock time |
| LLM first token (local) | <50ms | P95 latency |
| LLM first token (external) | <500ms | P95 latency |
| API response (simple) | <100ms | P95 latency |
| Concurrent jobs | 4+ | Parallel processing |

### 3.2 Resource Utilization

| Resource | Target | Constraint |
|----------|--------|------------|
| GPU memory | <30GB peak | Leave headroom for OS |
| CPU utilization | <80% during processing | 14 cores available |
| RAM usage | <24GB baseline | 36GB unified available |
| Disk I/O | SSD-optimized | Use NVMe effectively |

### 3.3 Reliability

| Metric | Target |
|--------|--------|
| Uptime (local service) | 99.9% during active use |
| Data durability | No loss on crash; journaling enabled |
| Error recovery | Auto-retry with exponential backoff |
| Graceful degradation | Continue with reduced features if GPU unavailable |

### 3.4 Security

| Requirement | Implementation |
|-------------|----------------|
| API keys | Environment variables, never in code |
| Local storage | Encrypted at rest (FileVault) |
| Network | HTTPS only for external; localhost for internal |
| Secrets | macOS Keychain integration |

---

## 4. Technical Constraints

### 4.1 Hardware Target
- **Primary:** Apple Mac Studio M4 Max
- **CPU:** 14-core (10P + 4E)
- **GPU:** 40-core Apple GPU
- **RAM:** 36GB Unified Memory
- **Storage:** 1TB+ NVMe SSD

### 4.2 Software Stack (Locked Versions)

```yaml
runtime:
  python: "3.12"
  node: "20 LTS"  # If UI needed

ml_frameworks:
  torch: "2.10.0"
  torchaudio: "2.10.0"
  torchcodec: "0.10.0"
  mlx: "0.30.5"
  mlx-metal: "0.30.5"

audio_processing:
  demucs: "4.0.1"
  librosa: "0.11.0"
  pedalboard: "0.9.22"
  faster-whisper: "1.2.1"

video_processing:
  opencv-python: "4.13.0.90"
  av: "16.1.0"

ml_tools:
  coremltools: "9.0"
  transformers: "latest"
  
api_framework:
  fastapi: "0.115+"
  uvicorn: "0.34+"
  
local_llm:
  ollama: "latest"
  mlx-lm: "latest"
```

### 4.3 Repository Structure
```
av-studio/
├── .github/
│   ├── workflows/           # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/      # Issue templates for agents
│   └── copilot-instructions.md
├── spec-kit/                # This specification
│   ├── constitution.md
│   ├── spec.md
│   ├── plan.md
│   ├── data-model.md
│   └── tasks.md
├── src/
│   ├── av_studio/           # Main package
│   ├── tests/
│   └── benchmarks/
├── docs/
├── scripts/
└── config/
```

---

## 5. Success Metrics

### 5.1 MVP Success Criteria (v0.1.0)
- [ ] Stem separation working with MPS acceleration
- [ ] Transcription with >95% accuracy
- [ ] Local LLM inference <50ms first token
- [ ] Basic agent routing functional
- [ ] REST API serving all core features
- [ ] Cost tracking accurate to $0.001

### 5.2 v1.0.0 Success Criteria
- [ ] All P0 and P1 requirements implemented
- [ ] <5% external API usage for routine tasks
- [ ] Agent system can complete 80% of tasks without human intervention
- [ ] Full MCP tool suite operational
- [ ] Documentation 100% complete

---

## 6. Out of Scope (v1.0)

- Cloud deployment (local-first mandate)
- Mobile apps
- Multi-user collaboration
- Real-time audio streaming (processing only)
- Music generation (depends on external API availability)

---

## 7. Open Questions

1. **Q:** Should we support Windows/Linux or macOS only?  
   **A:** macOS only for v1.0 (M4 Max optimization focus)

2. **Q:** Web UI framework preference?  
   **A:** TBD - Svelte recommended for reactivity; could be CLI-first

3. **Q:** Vector database for agent memory?  
   **A:** ChromaDB (local, embedded) vs. Qdrant (more features)

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| MPS | Metal Performance Shaders - Apple's GPU acceleration |
| MLX | Apple's ML framework optimized for Apple Silicon |
| MCP | Model Context Protocol - Anthropic's tool standard |
| LUFS | Loudness Units Full Scale - audio loudness measurement |
| Spec-Kit | This specification system for AI-First development |

---

**Approval Chain:**
- [ ] Planner Agent: Drafted
- [ ] Architect Agent: Technical Review
- [ ] Human Director (@scotlaclair): **GATE-1 APPROVAL REQUIRED**