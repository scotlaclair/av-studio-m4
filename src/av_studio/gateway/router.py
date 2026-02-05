"""
Smart Router: Intelligent model selection based on task, cost, and performance.
"""

from dataclasses import dataclass
from enum import StrEnum

from av_studio.config.settings import ModelProvider


class TaskType(StrEnum):
    CHAT = "chat"
    CODE = "code"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"
    IMAGE_ANALYSIS = "image_analysis"
    VIDEO_ANALYSIS = "video_analysis"
    EMBEDDING = "embedding"
    SUMMARIZATION = "summarization"
    CREATIVE_WRITING = "creative_writing"


@dataclass
class ModelCapability:
    """Defines what a model can do and its characteristics."""

    provider: ModelProvider
    model_id: str
    supports: list[TaskType]
    max_context: int
    cost_per_1k_input: float  # USD
    cost_per_1k_output: float  # USD
    avg_latency_ms: int
    quality_score: float  # 0-1, subjective quality rating
    is_local: bool = False
    requires_gpu: bool = False


# Model registry - extend as needed
MODEL_REGISTRY: dict[str, ModelCapability] = {
    # Local Models (FREE, low latency on M4 Max)
    "ollama:llama3.2:8b": ModelCapability(
        provider=ModelProvider.OLLAMA,
        model_id="llama3.2:8b",
        supports=[TaskType.CHAT, TaskType.CODE, TaskType.SUMMARIZATION],
        max_context=128000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=50,
        quality_score=0.82,
        is_local=True,
        requires_gpu=True,
    ),
    "ollama:qwen2.5-coder:7b": ModelCapability(
        provider=ModelProvider.OLLAMA,
        model_id="qwen2.5-coder:7b",
        supports=[TaskType.CODE, TaskType.CHAT],
        max_context=32000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=45,
        quality_score=0.85,
        is_local=True,
        requires_gpu=True,
    ),
    "mlx:llama-3.2-8b": ModelCapability(
        provider=ModelProvider.MLX,
        model_id="mlx-community/Llama-3.2-8B-Instruct-4bit",
        supports=[TaskType.CHAT, TaskType.CODE, TaskType.SUMMARIZATION, TaskType.CREATIVE_WRITING],
        max_context=128000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        avg_latency_ms=30,  # MLX is faster on Apple Silicon
        quality_score=0.82,
        is_local=True,
        requires_gpu=True,
    ),
    # External Models
    "openai:gpt-4o": ModelCapability(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o",
        supports=[TaskType.CHAT, TaskType.CODE, TaskType.IMAGE_ANALYSIS, TaskType.CREATIVE_WRITING],
        max_context=128000,
        cost_per_1k_input=0.0025,
        cost_per_1k_output=0.01,
        avg_latency_ms=800,
        quality_score=0.95,
    ),
    "anthropic:claude-3.5-sonnet": ModelCapability(
        provider=ModelProvider.ANTHROPIC,
        model_id="claude-3-5-sonnet-20241022",
        supports=[TaskType.CHAT, TaskType.CODE, TaskType.CREATIVE_WRITING, TaskType.IMAGE_ANALYSIS],
        max_context=200000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        avg_latency_ms=1000,
        quality_score=0.96,
    ),
    "google:gemini-2.0-flash": ModelCapability(
        provider=ModelProvider.GOOGLE,
        model_id="gemini-2.0-flash",
        supports=[TaskType.CHAT, TaskType.CODE, TaskType.IMAGE_ANALYSIS, TaskType.VIDEO_ANALYSIS],
        max_context=1000000,
        cost_per_1k_input=0.000075,
        cost_per_1k_output=0.0003,
        avg_latency_ms=400,
        quality_score=0.90,
    ),
}


@dataclass
class RoutingDecision:
    """Result of the smart routing decision."""

    model_key: str
    model: ModelCapability
    reason: str
    estimated_cost: float
    estimated_latency_ms: int


@dataclass
class RouterConfig:
    """Configuration for the smart router."""

    prefer_local: bool = True
    max_cost_usd: float = 0.50
    max_latency_ms: int = 2000
    min_quality_score: float = 0.80
    fallback_model: str = "mlx:llama-3.2-8b"


class SmartRouter:
    """
    Intelligent router that selects the best model based on:
    - Task type
    - Cost constraints
    - Latency requirements
    - Quality needs
    - Local vs external preference
    """

    def __init__(self, config: RouterConfig | None = None):
        self.config = config or RouterConfig()
        self.model_registry = MODEL_REGISTRY.copy()
        self._latency_history: dict[str, list[float]] = {}

    def route(
        self,
        task: TaskType,
        input_tokens: int,
        expected_output_tokens: int = 500,
        require_local: bool = False,
        require_quality: float | None = None,
        max_cost: float | None = None,
    ) -> RoutingDecision:
        """
        Select the optimal model for a given task.

        Args:
            task: The type of task to perform
            input_tokens: Estimated input token count
            expected_output_tokens: Expected output token count
            require_local: Force local model selection
            require_quality: Minimum quality score required
            max_cost: Maximum cost allowed for this request

        Returns:
            RoutingDecision with the selected model and reasoning
        """
        candidates = []

        for key, model in self.model_registry.items():
            # Filter by task support
            if task not in model.supports:
                continue

            # Filter by local requirement
            if require_local and not model.is_local:
                continue

            # Filter by context length
            if input_tokens > model.max_context:
                continue

            # Calculate estimated cost
            cost = self._calculate_cost(model, input_tokens, expected_output_tokens)

            # Filter by cost - handle explicit zero max_cost
            effective_max_cost = self.config.max_cost_usd if max_cost is None else max_cost
            if cost > effective_max_cost:
                continue

            # Filter by quality
            min_quality = require_quality or self.config.min_quality_score
            if model.quality_score < min_quality:
                continue

            # Get dynamic latency estimate
            latency = self._get_latency_estimate(key, model)

            candidates.append((key, model, cost, latency))

        if not candidates:
            # Fallback to default
            fallback = self.model_registry[self.config.fallback_model]
            return RoutingDecision(
                model_key=self.config.fallback_model,
                model=fallback,
                reason="No suitable model found, using fallback",
                estimated_cost=0.0,
                estimated_latency_ms=fallback.avg_latency_ms,
            )

        # Score and sort candidates
        scored = []
        for key, model, cost, latency in candidates:
            score = self._score_model(model, cost, latency)
            scored.append((score, key, model, cost, latency))

        scored.sort(reverse=True, key=lambda x: x[0])
        best_score, best_key, best_model, best_cost, best_latency = scored[0]

        # Generate reason
        reason = self._generate_reason(best_model, best_cost, best_latency, task)

        return RoutingDecision(
            model_key=best_key,
            model=best_model,
            reason=reason,
            estimated_cost=best_cost,
            estimated_latency_ms=best_latency,
        )

    def _calculate_cost(
        self, model: ModelCapability, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate the estimated cost for a request."""
        input_cost = (input_tokens / 1000) * model.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model.cost_per_1k_output
        return input_cost + output_cost

    def _get_latency_estimate(self, key: str, model: ModelCapability) -> int:
        """Get latency estimate, using historical data if available."""
        if key in self._latency_history and self._latency_history[key]:
            # Use moving average of last 10 requests
            recent = self._latency_history[key][-10:]
            return int(sum(recent) / len(recent))
        return model.avg_latency_ms

    def _score_model(self, model: ModelCapability, cost: float, latency: int) -> float:
        """
        Score a model based on multiple factors.
        Higher score = better choice.
        """
        score = 0.0

        # Quality contributes 40%
        score += model.quality_score * 40

        # Cost efficiency contributes 30% (lower cost = higher score)
        if cost == 0:
            score += 30  # Free is best
        else:
            cost_score = max(0, 30 - (cost * 100))  # Penalize high cost
            score += cost_score

        # Latency contributes 20% (lower latency = higher score)
        latency_score = max(0, 20 - (latency / 100))
        score += latency_score

        # Local preference contributes 10%
        if self.config.prefer_local and model.is_local:
            score += 10

        return score

    def _generate_reason(
        self, model: ModelCapability, cost: float, latency: int, task: TaskType
    ) -> str:
        """Generate a human-readable reason for the selection."""
        parts = []

        if model.is_local:
            parts.append("local model (zero cost)")
        else:
            parts.append(f"cost: ${cost:.4f}")

        parts.append(f"latency: ~{latency}ms")
        parts.append(f"quality: {model.quality_score:.0%}")

        return f"Selected {model.model_id} for {task.value}: {', '.join(parts)}"

    def record_latency(self, model_key: str, latency_ms: float) -> None:
        """Record actual latency for future routing decisions."""
        if model_key not in self._latency_history:
            self._latency_history[model_key] = []
        self._latency_history[model_key].append(latency_ms)
        # Keep only last 100 measurements
        if len(self._latency_history[model_key]) > 100:
            self._latency_history[model_key] = self._latency_history[model_key][-100:]


# Global router instance
smart_router = SmartRouter()
