"""
Agent orchestrator coordinating multiple specialized agents.
"""
import asyncio
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json

from llm.mlx_client import mlx_client, MLXClient
from llm.ollama_client import OllamaClient
from gateway.router import smart_router, TaskType, RoutingDecision
from gateway.token_analyzer import token_analyzer, cost_calculator


class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    AUDIO = "audio"
    VIDEO = "video"
    RESEARCH = "research"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    role: AgentRole
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Task:
    """A task to be executed by an agent."""
    id: str
    description: str
    task_type: TaskType
    parameters: dict = field(default_factory=dict)
    priority: int = 5  # 1-10, higher = more important
    status: str = "pending"
    result: Optional[Any] = None


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(
        self,
        role: AgentRole,
        llm_client: Optional[MLXClient] = None,
    ):
        self.role = role
        self.llm = llm_client or mlx_client
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    async def process(self, task: Task) -> Any:
        """Process a task and return the result."""
        pass
    
    async def think(self, prompt: str) -> str:
        """Use LLM to reason about a problem."""
        return self.llm.generate(prompt, system_prompt=self.system_prompt)


class CoordinatorAgent(BaseAgent):
    """
    Main coordinator that routes tasks to specialized agents.
    """
    
    def __init__(self, llm_client: Optional[MLXClient] = None):
        super().__init__(AgentRole.COORDINATOR, llm_client)
        self.agents: dict[AgentRole, BaseAgent] = {}
        self.task_queue: asyncio.Queue[Task] = asyncio.Queue()
    
    def _get_system_prompt(self) -> str:
        return """You are the coordinator agent for an A/V production studio.
Your job is to:
1. Understand user requests related to audio/video production
2. Break down complex requests into smaller tasks
3. Route tasks to the appropriate specialized agents (audio, video, research)
4. Synthesize results from multiple agents into coherent responses

You have access to these specialized agents:
- AUDIO: Handles stem separation, transcription, effects, mastering
- VIDEO: Handles video processing, effects, analysis
- RESEARCH: Handles web research, API calls, information gathering

When you receive a request, analyze it and output a JSON plan like:
{
    "tasks": [
        {"agent": "AUDIO", "action": "separate_stems", "params": {...}},
        {"agent": "VIDEO", "action": "extract_frames", "params": {...}}
    ],
    "reasoning": "explanation of your plan"
}
"""
    
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent."""
        self.agents[agent.role] = agent
    
    async def process(self, task: Task) -> Any:
        """Process a task by routing to appropriate agent."""
        # Use LLM to understand and route the task
        routing_prompt = f"""
Analyze this task and determine which agent(s) should handle it:

Task: {task.description}
Parameters: {json.dumps(task.parameters)}

Available agents: {list(self.agents.keys())}

Respond with a JSON routing plan.
"""
        plan_response = await self.think(routing_prompt)
        
        try:
            plan = json.loads(plan_response)
            results = []
            
            for subtask in plan.get("tasks", []):
                agent_role = AgentRole(subtask["agent"].lower())
                if agent_role in self.agents:
                    agent = self.agents[agent_role]
                    sub_task = Task(
                        id=f"{task.id}_{len(results)}",
                        description=subtask.get("action", ""),
                        task_type=task.task_type,
                        parameters=subtask.get("params", {}),
                    )
                    result = await agent.process(sub_task)
                    results.append(result)
            
            return {"plan": plan, "results": results}
        except json.JSONDecodeError:
            return {"error": "Failed to parse routing plan", "raw": plan_response}
    
    async def handle_user_request(self, user_input: str) -> str:
        """Main entry point for user requests."""
        # Analyze the request
        task = Task(
            id=f"user_{hash(user_input) % 10000}",
            description=user_input,
            task_type=self._infer_task_type(user_input),
        )
        
        result = await self.process(task)
        
        # Synthesize response
        synthesis_prompt = f"""
Based on these results, provide a helpful response to the user:

Original request: {user_input}
Results: {json.dumps(result, default=str)}

Provide a clear, concise summary of what was accomplished.
"""
        return await self.think(synthesis_prompt)
    
    def _infer_task_type(self, text: str) -> TaskType:
        """Infer the task type from user input."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["transcribe", "speech", "whisper"]):
            return TaskType.AUDIO_TRANSCRIPTION
        if any(word in text_lower for word in ["separate", "stems", "vocals", "drums"]):
            return TaskType.AUDIO_GENERATION
        if any(word in text_lower for word in ["video", "frame", "scene"]):
            return TaskType.VIDEO_ANALYSIS
        if any(word in text_lower for word in ["write", "create", "compose"]):
            return TaskType.CREATIVE_WRITING
        
        return TaskType.CHAT


class AudioAgent(BaseAgent):
    """Agent specialized in audio processing tasks."""
    
    def __init__(self, llm_client: Optional[MLXClient] = None):
        super().__init__(AgentRole.AUDIO, llm_client)
        from processing.audio.pipeline import audio_processor
        self.processor = audio_processor
    
    def _get_system_prompt(self) -> str:
        return """You are an audio processing expert agent.
You can perform:
- Stem separation (vocals, drums, bass, other) using Demucs
- Audio transcription using Whisper
- Audio effects (reverb, compression, EQ, etc.)
- Loudness normalization
- Format conversion

When asked to process audio, determine the best approach and execute it.
Always explain what you're doing and why.
"""
    
    async def process(self, task: Task) -> Any:
        """Process an audio task."""
        action = task.description.lower()
        params = task.parameters
        
        if "separate" in action or "stems" in action:
            from pathlib import Path
            audio_path = Path(params.get("audio_path", ""))
            if audio_path.exists():
                return self.processor.separate_stems(audio_path)
            return {"error": f"Audio file not found: {audio_path}"}
        
        if "transcribe" in action:
            from pathlib import Path
            audio_path = Path(params.get("audio_path", ""))
            if audio_path.exists():
                return self.processor.transcribe(audio_path)
            return {"error": f"Audio file not found: {audio_path}"}
        
        # Use LLM to handle other requests
        return await self.think(f"How should I handle this audio task: {task.description}")


# Factory function
def create_agent_system() -> CoordinatorAgent:
    """Create and configure the full agent system."""
    coordinator = CoordinatorAgent()
    coordinator.register_agent(AudioAgent())
    # Add more agents as implemented
    return coordinator