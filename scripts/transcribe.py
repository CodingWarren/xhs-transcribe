#!/usr/bin/env python3
"""
小红书/B站/YouTube 视频转录脚本
用法：python3 transcribe.py <video_path> [output_path] [--lang LANG]
  LANG 可选：zh (默认), en, ja, auto 等
"""
import sys
import argparse
from pathlib import Path

def transcribe(video_path: str, output_path: str = None, language: str = "zh"):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("请先安装依赖：pip install faster-whisper")
        sys.exit(1)

    video = Path(video_path)
    if not video.exists():
        print(f"文件不存在：{video_path}")
        sys.exit(1)

    out = Path(output_path) if output_path else video.with_suffix('.md')

    lang_display = language if language != "auto" else "自动检测"
    print(f"加载 large-v3 模型（首次运行需下载约 1.5GB）...")
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    print(f"开始转录：{video.name}（语言：{lang_display}）")
    segments, info = model.transcribe(
        str(video),
        language=None if language == "auto" else language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    texts = []
    timeline_lines = []
    for seg in segments:
        text = seg.text.strip()
        timeline_lines.append(f"[{seg.start:.1f}s → {seg.end:.1f}s] {text}")
        texts.append(text)

    with open(out, "w", encoding="utf-8") as f:
        f.write(f"视频：{video.name}\n")
        f.write(f"时长：{info.duration:.1f} 秒（{info.duration/60:.1f} 分钟）\n")
        f.write(f"语言：{info.language}\n\n")
        f.write("=" * 50 + "\n【逐段时间轴】\n" + "=" * 50 + "\n")
        f.write("\n".join(timeline_lines))
        f.write("\n\n" + "=" * 50 + "\n【完整文字稿】\n" + "=" * 50 + "\n")
        f.write("\n".join(texts))

    print(f"✅ 转录完成，已保存：{out}")
    print(f"   时长：{info.duration:.1f}s，共 {len(texts)} 段")
    return str(out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="视频转录脚本")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("output_path", nargs="?", default=None, help="输出文件路径（可选）")
    parser.add_argument("--lang", default="zh", help="语言：zh/en/ja/auto（默认 zh）")
    args = parser.parse_args()
    transcribe(args.video_path, args.output_path, args.lang)
