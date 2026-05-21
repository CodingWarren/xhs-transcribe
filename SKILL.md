---
name: xhs-transcribe
description: >
  Download a Xiaohongshu (小红书) video and transcribe it to text using local
  faster-whisper large-v3 model. No login required, no API key needed.

  Use this skill whenever the user:
  - shares a xiaohongshu.com or xhslink.com URL and asks to extract/transcribe/get the text
  - says "帮我提取小红书视频文字", "转录这个小红书视频", "把小红书视频转成文字"
  - shares any short video URL and asks for a transcript or text extraction
  - says "下载小红书视频并转文字", "xhs视频转文字", "提取视频内容"
---

# 小红书视频转文字

从小红书视频链接到文字稿的一键工作流，全程无需登录、无需 API Key。

## 工作流

### 第一步：下载视频

```bash
mkdir -p /tmp/xhs
yt-dlp -o "/tmp/xhs/%(title).60s/%(title).60s.%(ext)s" "用户提供的链接"
```

> **链接要求**：必须包含 `xsec_token` 参数的完整链接，或 `xhslink.com` 短链。
> 用户应从小红书 App「分享 → 复制链接」获取，裸 note_id 无法下载。

### 第二步：转录

```bash
python3 ~/.claude/skills/xhs-transcribe/scripts/transcribe.py "/tmp/xhs/视频标题/视频标题.mp4"
# 文字稿自动保存在同目录，文件名与视频相同但扩展名为 .md
# 结果：/tmp/xhs/视频标题/视频标题.md
```

### 第三步：整理并展示结果

转录完成后，在展示前做两步清理：

1. **合并重复行**：如果同一行文字连续出现 3 次以上，合并为一行（转录末尾常见）
2. **还原章节结构**：如果文字稿中出现明显的结构标记（如"第一遍""第三遍""第X章"），将其提升为 Markdown 标题（`###`），让输出更易读

然后展示：
- 文字稿保存路径
- 视频时长和语言
- 按章节整理后的完整文字稿内容
- 如有字幕误识别（如"中文字幕 XXX"反复出现），在末尾说明这是正常现象

## 注意事项

- **首次运行**：large-v3 模型约 1.5GB，自动从 HuggingFace 下载，需要几分钟
- **后续运行**：模型缓存在 `~/.cache/huggingface/`，无需重复下载
- **转录速度**：CPU 下约每分钟音频耗时 1.5 分钟（12核）；视频较长时建议后台运行
- **中文字幕干扰**：视频若有叠加字幕，可能被误识别进文字稿，属正常现象
- **环境依赖**：
  ```bash
  # 检查并安装所需依赖
  pip install faster-whisper yt-dlp
  ```
