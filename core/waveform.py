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


def _lowpass(samples, window: int):
    """Crude moving-average low-pass. No numpy, no scipy, no new dependency.

    A moving average of N samples attenuates content above roughly rate/(2N).
    At 16 kHz with N=16 that puts the corner near 500 Hz, which separates the
    two things actually in this recording: vessel engine noise is low-frequency
    rumble, and snapping shrimp are broadband transients centred well above
    2 kHz. So the low band is, in practice, the vessel trace.

    This is a blunt filter and it is labelled as one on the console. It is not
    presented as a spectrogram and no frequency figure is claimed from it.
    """
    out = []
    acc = 0
    q = []
    for v in samples:
        q.append(v)
        acc += v
        if len(q) > window:
            acc -= q.pop(0)
        out.append(acc / len(q))
    return out


def _bucket(values, buckets: int):
    total = len(values)
    if total == 0:
        return []
    size = max(1, total // buckets)
    peaks = []
    for i in range(0, total, size):
        chunk = values[i:i + size]
        if not chunk:
            continue
        peaks.append(max(abs(min(chunk)), abs(max(chunk))))
        if len(peaks) >= buckets:
            break
    return peaks


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

    peaks = [p / 32768.0 for p in _bucket(samples, buckets)]

    # The low band, on the same time axis. This is what makes the picture
    # explain the agent's finding instead of merely decorating it: the acoustic
    # agent reported snapping shrimp plus a vessel engine, and the vessel is the
    # low-frequency component. Two traces, one shape each.
    low_win = max(2, rate // 1000)          # corner near 500 Hz at 16 kHz
    low = [p / 32768.0 for p in _bucket(_lowpass(samples, low_win), buckets)]

    top = max(peaks) or 1.0
    # Normalize to the clip's own peak. An absolute scale would render a quiet
    # but perfectly valid recording as a flat line, which reads as "no data"
    # when the truth is "no loud data".
    #
    # The low band is scaled by the SAME divisor, not its own peak. Normalizing
    # it separately would make a quiet rumble look as loud as the shrimp and
    # invert the comparison the picture exists to show.
    peaks_n = [round(p / top, 4) for p in peaks]
    low_n = [round(p / top, 4) for p in low]

    # And the same low band scaled to ITSELF, for a separate lane.
    #
    # Measured on this clip: the low band peaks around 0.05 of the full-band
    # peak, because snapping shrimp dominate the energy by more than an order
    # of magnitude. On a shared axis it is a flat line: true, and useless.
    # So both are returned. `low_band` preserves the honest relative energy,
    # `low_band_self` shows the shape, and the console renders the second in
    # its own lane with "scaled independently" printed on it so no one reads
    # height across lanes.
    low_top = max(low) or 1.0
    low_self = [round(p / low_top, 4) for p in low]

    loudest = max(range(len(peaks_n)), key=lambda i: peaks_n[i]) if peaks_n else 0
    low_peak = max(range(len(low_n)), key=lambda i: low_n[i]) if low_n else 0
    seconds = round(total / rate, 2)

    return {
        "peaks": peaks_n,
        "low_band": low_n,
        "low_band_self": low_self,
        "low_band_share_of_peak": round(low_top / top, 4),
        "seconds": seconds,
        "rate": rate,
        "normalized_to_clip_peak": True,
        "peak_bucket": loudest,
        "peak_at_seconds": round(loudest / max(1, len(peaks_n)) * seconds, 1),
        "low_peak_bucket": low_peak,
        "low_peak_at_seconds": round(low_peak / max(1, len(low_n)) * seconds, 1),
        "low_band_corner_hz": round(rate / (2 * low_win)),
    }
