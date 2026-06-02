# xhs-transcribe

A Claude Code skill that downloads and transcribes Xiaohongshu (小红书) or Bilibili (B站) videos to text — no login, no API key, fully local.

## How it works

1. Downloads the video using `yt-dlp` with a share link
2. Transcribes audio using `faster-whisper` large-v3 locally
3. Saves the transcript as a `.md` file in a title-named subdirectory

## Prerequisites

- [Claude Code](https://claude.ai/code)
- Python 3.8+

```bash
pip install faster-whisper yt-dlp
```

> **First run**: The large-v3 model (~1.5GB) is downloaded automatically from HuggingFace and cached at `~/.cache/huggingface/`.

## Installation

Clone this repo into your Claude Code skills directory:

```bash
git clone https://github.com/codingwarren/xhs-transcribe ~/.claude/skills/xhs-transcribe
```

Claude Code will automatically detect and load the skill.

## Usage

Just paste a video link and ask Claude to transcribe it:

**Xiaohongshu:**
```
转录这个视频：https://www.xiaohongshu.com/explore/xxx?xsec_token=xxx
```

**Bilibili:**
```
帮我提取这个视频的文字：https://www.bilibili.com/video/BVxxx
```

The transcript is saved as:
```
~/xhs-videos/<video title>/
├── <video title>.mp4   (or .m4a for Bilibili)
└── <video title>.md    ← transcript
```

## Notes

- **Chinese only**: The script defaults to `language="zh"`. Edit `scripts/transcribe.py` to change.
- **Bilibili**: Audio and video are downloaded separately; the `.m4a` file is used for transcription.
- **Speed**: ~1.5 min transcription time per minute of audio on CPU (12 cores).
- **XHS links**: Must include `xsec_token` — use the share link from the app, not a bare note ID.

## File structure

```
xhs-transcribe/
├── SKILL.md              # Skill instructions for Claude
├── scripts/
│   └── transcribe.py     # faster-whisper transcription script
└── evals/
    └── evals.json        # Test cases
```
