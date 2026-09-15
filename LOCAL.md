# Local explainer (Grok + Kokoro + Ken Burns)

NotebookLM cloud path stays in `generate.sh`. This is the **Spark-free** path that
produced the locked WisdomForge clip: Grok 4.6 writes Ember VO → Kokoro `af_heart`
0.85 speaks it → ffmpeg Ken Burns stills → existing `overlay.sh` title/end card.

## One command

```bash
./scripts/run-local-explainer.sh \
  --source ./sources/example/epictetus-dichotomy-of-control.md \
  --title "The Dichotomy of Control" \
  --series "WisdomForge"
```

Outputs under `./output/<slug>/`: `.json` script, `.txt` VO, `.wav`, `.mp4`, and
`<slug>-final.mp4` after overlay.

Skip a step:

```bash
# Writer already done
./scripts/run-local-explainer.sh --script output/foo/foo.json

# Remux a new voice onto the same slides
./scripts/run-local-explainer.sh --script output/foo/foo.json --wav new.wav --skip-overlay
```

## Writer auth (no raw key in git)

1. `XAI_API_KEY` in the environment, or
2. Hermes `xai-oauth` in `~/.hermes/auth.json` (`hermes login` / desktop OAuth)

Model pin: **grok-4.6**. Do not point this at a Spark.

## TTS (the footgun)

Kokoro must be called as `pipeline(text, voice=...)`. **Never**
`generate_from_tokens` on raw text — that API is phonemes and sounds like a
nonsensical Scottish accent. Locked voice: `af_heart`, speed `0.85`. Piper
`en_US-lessac-medium` is the intelligibility floor only, not the ship voice.

```bash
pip install 'kokoro>=0.9.4'
```

CPU only. Phone-listen the WAV before YouTube.

## Overlay

Reuses `scripts/overlay.sh` (title card, watermark, end card). Pass
`--skip-overlay` if Ken Burns already carries branding.

## Not in this path

MiniMax H3, LTX, Wan, Open Notebook, draining a DGX Spark.
