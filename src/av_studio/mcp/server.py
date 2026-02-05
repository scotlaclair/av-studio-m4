"""
Model Context Protocol (MCP) server for extending studio capabilities.
"""

import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Create MCP server
app = Server("av-studio")

@app.list_tools()  # type: ignore[untyped-decorator]
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="separate_stems",
            description="Separate an audio file into stems (vocals, drums, bass, other)",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Path to the audio file",
                    },
                    "model": {
                        "type": "string",
                        "enum": ["htdemucs", "htdemucs_ft", "mdx_extra"],
                        "description": "Demucs model to use (htdemucs_ft recommended)",
                        "default": "htdemucs_ft",
                    },
                },
                "required": ["audio_path"],
            },
        ),
        Tool(
            name="transcribe_audio",
            description="Transcribe speech from an audio file to text",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Path to the audio file",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (e.g., 'en', 'es', 'fr')",
                    },
                },
                "required": ["audio_path"],
            },
        ),
        Tool(
            name="apply_audio_effects",
            description="Apply audio effects like reverb, compression, EQ",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string"},
                    "effects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["reverb", "compressor", "gain", "lowpass", "highpass"],
                                },
                            },
                        },
                    },
                },
                "required": ["audio_path", "effects"],
            },
        ),
        Tool(
            name="analyze_cost",
            description="Analyze token usage and cost for an LLM request",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to analyze"},
                    "model": {"type": "string", "description": "Model to estimate for"},
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="route_model",
            description="Get smart routing recommendation for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": ["chat", "code", "audio_transcription", "creative_writing"],
                    },
                    "input_length": {"type": "integer"},
                    "require_local": {"type": "boolean", "default": False},
                },
                "required": ["task_type"],
            },
        ),
    ]


@app.call_tool()  # type: ignore[untyped-decorator]
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool call."""

    if name == "separate_stems":
        from av_studio.processing.audio.pipeline import audio_processor

        result = audio_processor.separate_stems(
            Path(arguments["audio_path"]),
            model=arguments.get("model", "htdemucs_ft"),
        )
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "vocals": str(result.vocals) if result.vocals else None,
                        "drums": str(result.drums) if result.drums else None,
                        "bass": str(result.bass) if result.bass else None,
                        "other": str(result.other) if result.other else None,
                        "model": result.model_used,
                    },
                    indent=2,
                ),
            )
        ]

    if name == "transcribe_audio":
        from av_studio.processing.audio.pipeline import audio_processor

        transcribe_result: dict[str, Any] = audio_processor.transcribe(
            Path(arguments["audio_path"]),
            language=arguments.get("language"),
        )
        return [TextContent(type="text", text=json.dumps(transcribe_result, indent=2))]

    if name == "apply_audio_effects":
        from av_studio.processing.audio.pipeline import audio_processor

        output_path = audio_processor.apply_effects(
            Path(arguments["audio_path"]),
            effects=arguments["effects"],
        )
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "output_path": str(output_path),
                        "effects_applied": len(arguments["effects"]),
                    },
                    indent=2,
                ),
            )
        ]

    if name == "analyze_cost":
        from av_studio.gateway.token_analyzer import cost_calculator, token_analyzer

        tokens = token_analyzer.count_tokens(
            arguments["text"],
            arguments.get("model", "gpt-4o"),
        )
        cost = cost_calculator.estimate_cost(
            arguments.get("model", "gpt-4o"),
            tokens.input_tokens,
            tokens.estimated_output_tokens,
        )
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "tokens": tokens.__dict__,
                        "cost": cost.__dict__,
                    },
                    indent=2,
                ),
            )
        ]

    if name == "route_model":
        from av_studio.gateway.router import TaskType, smart_router

        decision = smart_router.route(
            TaskType(arguments["task_type"]),
            arguments.get("input_length", 1000),
            require_local=arguments.get("require_local", False),
        )
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "model": decision.model_key,
                        "reason": decision.reason,
                        "estimated_cost": decision.estimated_cost,
                        "estimated_latency_ms": decision.estimated_latency_ms,
                    },
                    indent=2,
                ),
            )
        ]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, write_stream, app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
