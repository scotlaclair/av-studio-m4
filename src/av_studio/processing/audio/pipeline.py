"""
Audio processing pipeline optimized for M4 Max.
Uses MPS (Metal) for GPU acceleration where possible.
"""
import torch
import torchaudio
from pathlib import Path
from typing import Optional, Literal, Union
from dataclasses import dataclass
import numpy as np
from pedalboard import Pedalboard, Reverb, Compressor, Gain, LowpassFilter, HighpassFilter
from pedalboard.io import AudioFile
import demucs.api


# Ensure we're using MPS (Metal) on Apple Silicon
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Audio pipeline using device: {DEVICE}")


@dataclass
class AudioMetadata:
    """Metadata for an audio file."""
    sample_rate: int
    channels: int
    duration_seconds: float
    format: str
    bit_depth: Optional[int] = None


@dataclass
class StemSeparationResult:
    """Result of stem separation."""
    vocals: Path
    drums: Path
    bass: Path
    other: Path
    original: Path
    model_used: str


class AudioProcessor:
    """
    Comprehensive audio processing using M4 Max GPU acceleration.
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._demucs_separator = None
    
    def get_metadata(self, audio_path: Path) -> AudioMetadata:
        """Extract metadata from an audio file."""
        info = torchaudio.info(str(audio_path))
        return AudioMetadata(
            sample_rate=info.sample_rate,
            channels=info.num_channels,
            duration_seconds=info.num_frames / info.sample_rate,
            format=audio_path.suffix.lstrip("."),
            bit_depth=info.bits_per_sample,
        )
    
    def separate_stems(
        self,
        audio_path: Path,
        model: Literal["htdemucs", "htdemucs_ft", "mdx_extra"] = "htdemucs_ft",
    ) -> StemSeparationResult:
        """
        Separate audio into stems (vocals, drums, bass, other).
        Uses Demucs with MPS acceleration.
        
        htdemucs_ft is the fine-tuned model with best quality.
        """
        # Initialize separator if needed
        if self._demucs_separator is None or self._demucs_separator.model != model:
            self._demucs_separator = demucs.api.Separator(
                model=model,
                device=DEVICE,
            )
        
        # Perform separation
        origin, separated = self._demucs_separator.separate_audio_file(str(audio_path))
        
        # Save stems
        stem_dir = self.output_dir / audio_path.stem / "stems"
        stem_dir.mkdir(parents=True, exist_ok=True)
        
        stem_paths = {}
        for stem_name, stem_audio in separated.items():
            stem_path = stem_dir / f"{stem_name}.wav"
            demucs.api.save_audio(
                stem_audio,
                str(stem_path),
                samplerate=self._demucs_separator.samplerate,
            )
            stem_paths[stem_name] = stem_path
        
        return StemSeparationResult(
            vocals=stem_paths.get("vocals"),
            drums=stem_paths.get("drums"),
            bass=stem_paths.get("bass"),
            other=stem_paths.get("other"),
            original=audio_path,
            model_used=model,
        )
    
    def apply_effects(
        self,
        audio_path: Path,
        effects: list[dict],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Apply audio effects using Pedalboard.
        
        Example effects:
        [
            {"type": "reverb", "room_size": 0.5, "wet_level": 0.3},
            {"type": "compressor", "threshold_db": -20, "ratio": 4},
            {"type": "gain", "gain_db": 3},
        ]
        """
        # Build pedalboard
        board = Pedalboard()
        
        for effect in effects:
            effect_type = effect.pop("type")
            if effect_type == "reverb":
                board.append(Reverb(**effect))
            elif effect_type == "compressor":
                board.append(Compressor(**effect))
            elif effect_type == "gain":
                board.append(Gain(**effect))
            elif effect_type == "lowpass":
                board.append(LowpassFilter(**effect))
            elif effect_type == "highpass":
                board.append(HighpassFilter(**effect))
        
        # Process audio
        output_path = output_path or self.output_dir / f"{audio_path.stem}_processed.wav"
        
        with AudioFile(str(audio_path)) as f:
            audio = f.read(f.frames)
            sample_rate = f.samplerate
        
        processed = board(audio, sample_rate)
        
        with AudioFile(str(output_path), "w", sample_rate, processed.shape[0]) as f:
            f.write(processed)
        
        return output_path
    
    def transcribe(
        self,
        audio_path: Path,
        model_size: Literal["tiny", "base", "small", "medium", "large-v3"] = "large-v3",
        language: Optional[str] = None,
    ) -> dict:
        """
        Transcribe audio using faster-whisper with GPU acceleration.
        """
        from faster_whisper import WhisperModel
        
        # faster-whisper doesn't support MPS yet, so we use CPU with optimizations
        # For M4 Max, the CPU is fast enough for most use cases
        model = WhisperModel(
            model_size,
            device="cpu",  # MPS not yet supported
            compute_type="int8",  # Optimized for Apple Silicon
            cpu_threads=14,  # Use most of the 14 cores
        )
        
        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=True,  # Voice activity detection
        )
        
        # Collect results
        transcript_segments = []
        full_text = []
        
        for segment in segments:
            transcript_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            })
            full_text.append(segment.text)
        
        return {
            "text": " ".join(full_text),
            "segments": transcript_segments,
            "language": info.language,
            "duration": info.duration,
        }
    
    def normalize_loudness(
        self,
        audio_path: Path,
        target_lufs: float = -14.0,  # Standard streaming loudness
        output_path: Optional[Path] = None,
    ) -> Path:
        """Normalize audio to target LUFS loudness."""
        import pyloudnorm as pyln
        
        waveform, sample_rate = torchaudio.load(str(audio_path))
        audio_np = waveform.numpy().T  # Convert to (samples, channels)
        
        # Measure current loudness
        meter = pyln.Meter(sample_rate)
        current_loudness = meter.integrated_loudness(audio_np)
        
        # Normalize
        normalized = pyln.normalize.loudness(audio_np, current_loudness, target_lufs)
        
        # Save
        output_path = output_path or self.output_dir / f"{audio_path.stem}_normalized.wav"
        torchaudio.save(
            str(output_path),
            torch.from_numpy(normalized.T),
            sample_rate,
        )
        
        return output_path


# Global processor instance
audio_processor = AudioProcessor(Path.home() / "av-studio" / "processed")