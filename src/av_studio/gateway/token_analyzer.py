"""
Token analysis and cost calculation for LLM requests.
"""

from dataclasses import dataclass
from typing import Any

import tiktoken
from transformers import AutoTokenizer


@dataclass
class TokenCount:
    """Token count breakdown."""

    input_tokens: int
    estimated_output_tokens: int
    total_tokens: int
    method: str  # Which tokenizer was used


@dataclass
class CostEstimate:
    """Cost estimate for a request."""

    input_cost: float
    output_cost: float
    total_cost: float
    currency: str = "USD"
    model: str = ""
    breakdown: dict | None = None


class TokenAnalyzer:
    """
    Analyze token counts for various models.
    Uses appropriate tokenizer based on model family.
    """

    def __init__(self):
        self._tokenizers: dict[str, Any] = {}
        self._tiktoken_encodings: dict[str, tiktoken.Encoding] = {}

    def count_tokens(self, text: str | list[dict], model: str = "gpt-4o") -> TokenCount:
        """
        Count tokens for the given text or messages.

        Args:
            text: Either a string or a list of chat messages
            model: The model to count tokens for

        Returns:
            TokenCount with detailed breakdown
        """
        # Convert messages to string if needed
        if isinstance(text, list):
            text = self._messages_to_text(text)

        # Select appropriate tokenizer
        if "gpt" in model.lower() or "openai" in model.lower():
            count = self._count_tiktoken(text, model)
            method = "tiktoken"
        elif "llama" in model.lower():
            count = self._count_llama(text)
            method = "llama-tokenizer"
        elif "claude" in model.lower():
            # Claude uses similar tokenization to GPT-4
            count = self._count_tiktoken(text, "gpt-4")
            method = "tiktoken-approximation"
        else:
            # Fallback: rough estimate (4 chars per token average)
            count = len(text) // 4
            method = "character-estimate"

        # Estimate output tokens (configurable ratio)
        estimated_output = min(count // 2, 2000)  # Reasonable default

        return TokenCount(
            input_tokens=count,
            estimated_output_tokens=estimated_output,
            total_tokens=count + estimated_output,
            method=method,
        )

    def _messages_to_text(self, messages: list[dict]) -> str:
        """Convert chat messages to text for token counting."""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")
        return "\n".join(parts)

    def _count_tiktoken(self, text: str, model: str) -> int:
        """Count tokens using tiktoken (OpenAI's tokenizer)."""
        try:
            if model not in self._tiktoken_encodings:
                try:
                    self._tiktoken_encodings[model] = tiktoken.encoding_for_model(model)
                except KeyError:
                    self._tiktoken_encodings[model] = tiktoken.get_encoding("cl100k_base")

            return len(self._tiktoken_encodings[model].encode(text))
        except Exception:
            return len(text) // 4

    def _count_llama(self, text: str) -> int:
        """Count tokens using Llama tokenizer."""
        try:
            if "llama" not in self._tokenizers:
                self._tokenizers["llama"] = AutoTokenizer.from_pretrained(
                    "meta-llama/Llama-3.2-8B", use_fast=True
                )
            return len(self._tokenizers["llama"].encode(text))
        except Exception:
            # Fallback if model not available
            return len(text) // 4


class CostCalculator:
    """
    Calculate costs for LLM API usage.
    Tracks cumulative costs and provides budgeting.
    """

    # Pricing per 1K tokens (as of early 2025, update as needed)
    PRICING = {
        # OpenAI
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        # Anthropic
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku": {"input": 0.0008, "output": 0.004},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        # Google
        "gemini-2.0-flash": {"input": 0.000075, "output": 0.0003},
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
        # Local (free)
        "ollama": {"input": 0.0, "output": 0.0},
        "mlx": {"input": 0.0, "output": 0.0},
        # ElevenLabs (per character)
        "elevenlabs": {"per_character": 0.00003},
    }

    def __init__(self):
        self.total_spent: float = 0.0
        self.budget_limit: float | None = None
        self.spending_history: list[CostEstimate] = []

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> CostEstimate:
        """Estimate the cost for a request before making it."""
        pricing = self._get_pricing(model)

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total = input_cost + output_cost

        return CostEstimate(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total,
            model=model,
            breakdown={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_rate": pricing["input"],
                "output_rate": pricing["output"],
            },
        )

    def record_cost(self, estimate: CostEstimate):
        """Record an actual cost after a request completes."""
        self.total_spent += estimate.total_cost
        self.spending_history.append(estimate)

    def check_budget(self, estimated_cost: float) -> tuple[bool, str]:
        """Check if a request would exceed the budget."""
        if self.budget_limit is None:
            return True, "No budget limit set"

        if self.total_spent + estimated_cost > self.budget_limit:
            remaining = self.budget_limit - self.total_spent
            return False, f"Would exceed budget. Remaining: ${remaining:.4f}"

        return True, "Within budget"

    def set_budget(self, limit: float):
        """Set a spending budget limit."""
        self.budget_limit = limit

    def get_summary(self) -> dict:
        """Get a summary of spending."""
        by_model: dict[str, float] = {}
        for estimate in self.spending_history:
            model = estimate.model
            by_model[model] = by_model.get(model, 0) + estimate.total_cost

        return {
            "total_spent": self.total_spent,
            "budget_limit": self.budget_limit,
            "remaining": (self.budget_limit - self.total_spent) if self.budget_limit else None,
            "by_model": by_model,
            "request_count": len(self.spending_history),
        }

    def _get_pricing(self, model: str) -> dict:
        """Get pricing for a model, with fallback."""
        # Normalize model name
        model_lower = model.lower()

        for key, pricing in self.PRICING.items():
            if key in model_lower:
                return pricing

        # Default to free (assume local)
        return {"input": 0.0, "output": 0.0}


# Global instances
token_analyzer = TokenAnalyzer()
cost_calculator = CostCalculator()
