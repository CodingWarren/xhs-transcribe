#!/usr/bin/env python3
"""
小红书视频转录脚本
用法：python3 transcribe.py <video_path> [output_path]
"""
import sys
from pathlib import Path

def transcribe(video_path: str, output_path: str = None):
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

    print(f"加载 large-v3 模型（首次运行需下载约 1.5GB）...")
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    print(f"开始转录：{video.name}")
    segments, info = model.transcribe(
        str(video),
        language="zh",
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
    if len(sys.argv) < 2:
        print("用法：python3 transcribe.py <video_path> [output_path]")
        sys.exit(1)
    transcribe(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
