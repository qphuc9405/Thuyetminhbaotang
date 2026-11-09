#!/usr/bin/env python3
"""Build small mouth timing tracks from the existing MP3s; never change audio files."""
from __future__ import annotations
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

AUDIO_DIR = Path(__file__).resolve().parents[1] / 'public' / 'audio'
STEP = 0.04
SAMPLE_RATE = 16000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default=shutil.which('ffmpeg'), help='Path to an FFmpeg executable')
    args = parser.parse_args()
    if not args.ffmpeg:
        parser.error('FFmpeg is required to rebuild cues; pass --ffmpeg /path/to/ffmpeg.')
    recordings = {}
    for source in sorted(AUDIO_DIR.glob('*.mp3')):
        result = subprocess.run([args.ffmpeg, '-v', 'error', '-i', str(source), '-f', 'f32le', '-ac', '1', '-ar', str(SAMPLE_RATE), 'pipe:1'], capture_output=True, check=True)
        samples = array.array('f')
        samples.frombytes(result.stdout)
        if sys.byteorder != 'little':
            samples.byteswap()
        window = round(STEP * SAMPLE_RATE)
        energy = []
        for start in range(0, len(samples), window):
            values = samples[start:start + window]
            energy.append(math.sqrt(sum(value * value for value in values) / len(values)))
        if not energy:
            raise ValueError(f'No decoded samples in {source.name}')
        reference = sorted(energy)[min(len(energy) - 1, round(len(energy) * 0.9))]
        threshold = max(0.006, min(0.025, reference * 0.16))
        bits = ''.join('1' if value >= threshold else '0' for value in energy)
        recordings[source.name] = {'duration': round(len(samples) / SAMPLE_RATE, 6), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'mouth': bits}
        print(f'{source.name}: {len(samples) / SAMPLE_RATE:.2f}s, {bits.count("1") / len(bits):.0%} voiced frames')
    output = AUDIO_DIR / 'narration-mouth-cues.json'
    output.write_text(json.dumps({'version': 1, 'step': STEP, 'recordings': recordings}, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'Wrote {output}')


if __name__ == '__main__':
    main()
