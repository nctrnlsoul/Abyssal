"""Peak envelope of the real hydrophone clip.

This is not decoration. It is the actual waveform of the SanctSound FK04
recording the acoustic agent analyzed, computed from the same file the model
was given. Drawing a fake sine wave would have been easier and would have been
the exact species of lie this project exists to avoid.

stdlib `wave` and `array` only. No numpy, no new dependency.
"""
from __future__ import annotations
import array
import os
import wave


def envelope(path: str, buckets: int = 320) -> dict:
    """Peak amplitude per bucket, normalized to 0..1."""
    with wave.open(path, "rb") as w:
        n_channels = w.getnchannels()
        width = w.getsampwidth()
        rate = w.getframerate()
        frames = w.getnframes()
        raw = w.readframes(frames)

    if width != 2:
        raise ValueError(f"expected 16-bit PCM, got {width * 8}-bit")

    samples = array.array("h")
    samples.frombytes(raw)
    if n_channels > 1:
        samples = samples[::n_channels]

    total = len(samples)
    if total == 0:
        return {"peaks": [], "seconds": 0.0, "rate": rate}

    size = max(1, total // buckets)
    peaks: list[float] = []
    for i in range(0, total, size):
        chunk = samples[i:i + size]
        if not chunk:
            continue
        peaks.append(max(abs(min(chunk)), abs(max(chunk))) / 32768.0)
        if len(peaks) >= buckets:
            break

    top = max(peaks) or 1.0
    # Normalize to the clip's own peak. An absolute scale would render a quiet
    # but perfectly valid recording as a flat line, which reads as "no data"
    # when the truth is "no loud data".
    peaks = [round(p / top, 4) for p in peaks]
    return {
        "peaks": peaks,
        "seconds": round(total / rate, 2),
        "rate": rate,
        "normalized_to_clip_peak": True,
    }
