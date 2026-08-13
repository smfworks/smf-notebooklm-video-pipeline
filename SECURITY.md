# Security

This pipeline shells out to `notebooklm` and `ffmpeg`.

- Overlay titles are escaped for ffmpeg `drawtext`.
- Scripts refuse missing inputs and unknown format/style values.
- Do not pass untrusted remote filenames into overlay without review.

Report issues via GitHub security advisories.
