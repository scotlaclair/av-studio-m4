"""
MLX-native LLM client optimized for Apple Silicon.
This provides the fastest local inference on M4 Max.
"""

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

import mlx.core as mx
from mlx_lm import generate, load, stream_generate


@dataclass
class MLXConfig:
    """Configuration for MLX models."""

    model_path: str = "mlx-community/Llama-3.2-8B-Instruct-4bit"
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    repetition_penalty: float = 1.1


class MLXClient:
    """
    High-performance LLM client using Apple's MLX framework.
    Optimized for M4 Max with unified memory architecture.
    """

    def __init__(self, config: MLXConfig | None = None):
        self.config = config or MLXConfig()
        self._model = None
        self._tokenizer = None
        self._loaded_model_path: str | None = None

    def load_model(self, model_path: str | None = None) -> None:
        """
        Load an MLX model into memory.
        Models are cached - only reloads if path changes.
        """
        path = model_path or self.config.model_path

        if self._model is not None and self._loaded_model_path == path:
            return  # Already loaded

        print(f"Loading MLX model: {path}")
        self._model, self._tokenizer = load(path)
        self._loaded_model_path = path
        print(f"Model loaded. Using GPU device: {mx.default_device()}")

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """
        Generate a complete response (non-streaming).
        """
        self.load_model()

        # Format prompt with system message if provided
        full_prompt = self._format_prompt(prompt, system_prompt)

        response = generate(
            model=self._model,
            tokenizer=self._tokenizer,
            prompt=full_prompt,
            max_tokens=max_tokens or self.config.max_tokens,
            temp=temperature or self.config.temperature,
            top_p=self.config.top_p,
            repetition_penalty=self.config.repetition_penalty,
        )

        return str(response)

    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream tokens as they're generated.
        This provides the best UX for longer responses.
        """
        self.load_model()

        full_prompt = self._format_prompt(prompt, system_prompt)

        # MLX stream_generate is synchronous, so we wrap it
        for token in stream_generate(
            model=self._model,
            tokenizer=self._tokenizer,
            prompt=full_prompt,
            max_tokens=max_tokens or self.config.max_tokens,
            temp=temperature or self.config.temperature,
        ):
            yield token
            await asyncio.sleep(0)  # Yield control to event loop

    def _format_prompt(self, prompt: str, system_prompt: str | None = None) -> str:
        """Format prompt for Llama-style chat models."""
        if system_prompt:
            return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the loaded model."""
        if self._model is None:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "model_path": self._loaded_model_path,
            "device": str(mx.default_device()),
            "memory_info": "Unified memory (M4 Max)",
        }


# Recommended models for M4 Max (36GB unified memory)
RECOMMENDED_MLX_MODELS = {
    "fast": "mlx-community/Llama-3.2-3B-Instruct-4bit",  # ~2GB, fastest
    "balanced": "mlx-community/Llama-3.2-8B-Instruct-4bit",  # ~5GB, good balance
    "quality": "mlx-community/Llama-3.3-70B-Instruct-4bit",  # ~40GB, best quality (fits in 36GB with offload)
    "code": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",  # ~4GB, optimized for code
    "creative": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",  # ~4GB, good for creative tasks
}


# Global client instance
mlx_client = MLXClient()
