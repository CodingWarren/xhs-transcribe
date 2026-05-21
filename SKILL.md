---
name: xhs-transcribe
description: >
  Download and transcribe videos from Xiaohongshu (小红书) or Bilibili (B站) to text
  using local faster-whisper large-v3. No login, no API key, works fully offline.

  ALWAYS use this skill when the user:
  - shares a xiaohongshu.com, xhslink.com, or bilibili.com URL and wants text/transcript
  - says "转录", "提取文字", "转成文字", "视频转文字", "帮我看看视频说了什么"
  - says "transcribe", "extract text", "video to text", "what does this video say"
  - shares any short video link and asks for content summary or transcript
---

# 小红书视频转文字

从小红书视频链接到文字稿的一键工作流，全程无需登录、无需 API Key。

## 工作流

### 第一步：下载视频

**小红书：**
```bash
mkdir -p /tmp/xhs
yt-dlp -o "/tmp/xhs/%(title).60s/%(title).60s.%(ext)s" "用户提供的链接"
```

> **链接要求**：必须包含 `xsec_token` 参数的完整链接，或 `xhslink.com` 短链。
> 用户应从小红书 App「分享 → 复制链接」获取，裸 note_id 无法下载。

**B站（Bilibili）：**
```bash
yt-dlp -o "/tmp/xhs/%(title).60s/%(title).60s.%(ext)s" "B站链接"
```

> B站视频和音频会分开下载（`.mp4` + `.m4a`），转录时传 `.m4a` 文件给 transcribe.py。

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
- **仅支持中文**：转录脚本默认 `language="zh"`，英文/日文视频需修改 `transcribe.py` 第27行的 language 参数
- **环境依赖**：
  ```bash
  # 检查并安装所需依赖
  pip install faster-whisper yt-dlp
  ```
