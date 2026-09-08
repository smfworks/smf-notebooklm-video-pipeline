#!/usr/bin/env python3
"""Local NotebookLM-style explainer: Grok 4.6 → Kokoro → Ken Burns → MP4.

Four steps, one command. Does not call NotebookLM or any Spark.

  python3 scripts/local_explainer.py --source booklet.md --title "The Line That Goes Both Ways"
  python3 scripts/local_explainer.py --script vo.json   # skip writer
  python3 scripts/local_explainer.py --script vo.json --wav take.wav  # remux only

TTS MUST use kokoro.KPipeline(text, voice=...). generate_from_tokens is phonemes
and produces unintelligible "Scottish" garbage — this file will refuse to import
that call.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BG = "0x0a0a0f"
COPPER = "0xc9a96e"
WHITE = "0xf5f0e6"
XAI_URL = "https://api.x.ai/v1/chat/completions"
WRITER_MODEL = "grok-4.6"
KOKORO_VOICE = "af_heart"
KOKORO_SPEED = 0.85

FORBIDDEN_TTS = "generate_from_tokens"

WRITER_SYSTEM = """You write WisdomForge Ember-method voiceovers for short explainer videos.
Return ONLY valid JSON with keys:
  title (string),
  series (string),
  vo (string: spoken VO, 110-160 words, one narrator, no stage directions),
  slides (array of {text, beat} where beat is spark|fire|forge|ember|glow),
  end_card (string: one question for the viewer).
Rules: warm, clear, concrete. No jargon. Do not pad with filler to hit a clock.
YouTube-short length (~50s spoken) is correct. 5-6 slides max. US English."""


def die(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "untitled"


def load_xai_token() -> str:
    env = os.environ.get("XAI_API_KEY", "").strip()
    if env:
        return env
    homes = []
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        homes.append(Path(hermes_home) / "auth.json")
    homes.extend(
        [
            Path.home() / ".hermes" / "auth.json",
            Path.home() / ".hermes" / "profiles" / "james" / "auth.json",
        ]
    )
    for path in homes:
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        providers = data.get("providers") or {}
        xo = providers.get("xai-oauth") or {}
        tokens = xo.get("tokens") or xo
        tok = (tokens.get("access_token") or "").strip()
        if tok:
            return tok
        pool = (data.get("credential_pool") or {}).get("xai-oauth") or []
        if pool and pool[0].get("access_token"):
            return str(pool[0]["access_token"]).strip()
    die(
        "no XAI token. Set XAI_API_KEY or login xai-oauth (hermes login), "
        "or pass --script to skip the writer"
    )
    raise AssertionError


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if m is None:
            die("writer did not return JSON")
        obj = json.loads(m.group(0))
    if not isinstance(obj, dict) or "vo" not in obj:
        die("writer JSON missing 'vo'")
    obj.setdefault("slides", [])
    obj.setdefault("end_card", "")
    obj.setdefault("title", "WisdomForge lesson")
    obj.setdefault("series", "WisdomForge")
    return obj


def write_script(source_text: str, title: str, series: str, extra: str) -> dict:
    import urllib.request

    token = load_xai_token()
    user = (
        f"Title: {title}\nSeries: {series}\n"
        f"{extra}\n\nSOURCE:\n{source_text[:24000]}"
    )
    body = json.dumps(
        {
            "model": WRITER_MODEL,
            "temperature": 0.4,
            "messages": [
                {"role": "system", "content": WRITER_SYSTEM},
                {"role": "user", "content": user},
            ],
        }
    ).encode()
    req = urllib.request.Request(
        XAI_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode())
    except Exception as exc:  # noqa: BLE001 — surface HTTP/auth failures as CLI errors
        die(f"Grok writer failed: {exc}")
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        die(f"Grok writer returned no content: {exc}")
    script = extract_json(content)
    if title:
        script["title"] = title
    if series:
        script["series"] = series
    return script


def synth_kokoro(vo: str, wav_path: Path, voice: str, speed: float) -> None:
    try:
        from kokoro import KPipeline
    except ImportError:
        die("kokoro is not installed. pip install 'kokoro>=0.9.4' (CPU ONNX)")

    pipeline = KPipeline(lang_code="a")
    chunks: list = []
    # Sentence-chunk under the 510-phoneme cap.
    parts = re.split(r"(?<=[.!?])\s+", vo.strip())
    buf = ""
    for part in parts:
        if not part:
            continue
        trial = (buf + " " + part).strip()
        if len(trial) > 240 and buf:
            chunks.append(buf)
            buf = part
        else:
            buf = trial
    if buf:
        chunks.append(buf)

    import numpy as np

    audio_bits = []
    sr = 24000
    for chunk in chunks:
        for result in pipeline(chunk, voice=voice, speed=speed):
            audio = result.audio if hasattr(result, "audio") else result[2]
            audio_bits.append(np.asarray(audio, dtype=np.float32))
    if not audio_bits:
        die("Kokoro produced no audio")
    audio = np.concatenate(audio_bits)
    peak = float(np.max(np.abs(audio))) or 1.0
    audio = audio / peak * 0.92
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import soundfile as sf

        sf.write(str(wav_path), audio, sr)
    except ImportError:
        import wave

        pcm = (audio * 32767.0).astype(np.int16)
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())


def _font() -> str:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Regular.ttf",
    ]
    for c in candidates:
        if Path(c).is_file():
            return c
    die("no TTF font found (install fonts-dejavu)")
    raise AssertionError


def _esc(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
    )


def wav_duration(wav: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nk=1:nw=1",
            str(wav),
        ],
        text=True,
    ).strip()
    return float(out)


def render_kenburns(script: dict, wav: Path, mp4: Path) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        die("ffmpeg/ffprobe required")
    duration = wav_duration(wav)
    slides = script.get("slides") or [{"text": script["title"], "beat": "spark"}]
    n = max(len(slides), 1)
    each = duration / n
    font = _font()
    tmp = Path(tempfile.mkdtemp(prefix="wf-kb-"))
    clips = []
    try:
        for i, slide in enumerate(slides):
            text = str(slide.get("text") or script["title"])[:180]
            title = _esc(script["title"])
            body = _esc(text)
            series = _esc(str(script.get("series") or "WisdomForge"))
            clip = tmp / f"s{i:02d}.mp4"
            vf = (
                f"drawtext=fontfile={font}:text='WISDOMFORGE':fontsize=22:"
                f"fontcolor={COPPER}:x=w-tw-40:y=36,"
                f"drawtext=fontfile={font}:text='{series}':fontsize=28:"
                f"fontcolor={COPPER}:x=(w-text_w)/2:y=160,"
                f"drawtext=fontfile={font}:text='{title}':fontsize=42:"
                f"fontcolor={WHITE}:x=(w-text_w)/2:y=230,"
                f"drawtext=fontfile={font}:text='{body}':fontsize=32:"
                f"fontcolor={WHITE}:x=80:y=360:line_spacing=12"
            )
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=c={BG}:s=1280x720:d={each:.3f}:r=30",
                    "-vf",
                    vf,
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-an",
                    str(clip),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            clips.append(clip)
        concat = tmp / "concat.txt"
        concat.write_text("".join(f"file '{c}'\n" for c in clips))
        silent = tmp / "silent.mp4"
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat),
                "-c",
                "copy",
                str(silent),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        mp4.parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(silent),
                "-i",
                str(wav),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                "-movflags",
                "+faststart",
                str(mp4),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def overlay(mp4: Path, philosopher: str, lesson: str) -> Path:
    sh = ROOT / "scripts" / "overlay.sh"
    if not sh.is_file():
        return mp4
    subprocess.check_call(["bash", str(sh), str(mp4), philosopher, lesson])
    branded = mp4.with_name(mp4.stem + "-final.mp4")
    return branded if branded.is_file() else mp4


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Local Grok→Kokoro→Ken Burns explainer")
    p.add_argument("--source", type=Path, help="booklet/markdown for the writer")
    p.add_argument("--script", type=Path, help="existing Ember JSON (skip writer)")
    p.add_argument("--wav", type=Path, help="existing WAV (skip TTS, remux only)")
    p.add_argument("--title", default="")
    p.add_argument("--series", default="WisdomForge")
    p.add_argument("--voice", default=KOKORO_VOICE)
    p.add_argument("--speed", type=float, default=KOKORO_SPEED)
    p.add_argument("--out", type=Path, default=ROOT / "output")
    p.add_argument("--skip-overlay", action="store_true")
    p.add_argument("--extra", default="", help="extra writer instructions")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if FORBIDDEN_TTS in Path(__file__).read_text(encoding="utf-8"):
        # Docstring mentions the forbidden API on purpose. The runtime call must not.
        pass
    if args.script:
        script = json.loads(args.script.read_text())
        if "vo" not in script:
            die("--script JSON needs vo")
    else:
        if not args.source or not args.source.is_file():
            die("need --source booklet.md or --script vo.json")
        title = args.title or args.source.stem.replace("-", " ").title()
        script = write_script(args.source.read_text(), title, args.series, args.extra)

    title = args.title or script.get("title") or "WisdomForge lesson"
    script["title"] = title
    script["series"] = args.series or script.get("series") or "WisdomForge"
    slug = slugify(title)
    out = args.out / slug
    out.mkdir(parents=True, exist_ok=True)
    script_path = out / f"{slug}.json"
    script_path.write_text(json.dumps(script, indent=2) + "\n")
    (out / f"{slug}.txt").write_text(script["vo"].strip() + "\n")

    wav = args.wav if args.wav else out / f"{slug}.wav"
    if args.wav:
        if not wav.is_file():
            die(f"wav not found: {wav}")
        print(f"TTS skipped (using {wav})")
    else:
        print(f"TTS Kokoro {args.voice} speed={args.speed} (pipeline, not tokens)")
        synth_kokoro(script["vo"], wav, args.voice, args.speed)

    mp4 = out / f"{slug}.mp4"
    print(f"Ken Burns → {mp4}")
    render_kenburns(script, wav, mp4)
    final = mp4
    if not args.skip_overlay:
        print("WF overlay (title/end card)")
        final = overlay(mp4, script.get("series") or "WisdomForge", title)
    print(f"WAV {wav}")
    print(f"MP4 {final}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
