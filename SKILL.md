---
name: xhs-transcribe
description: >
  Download and transcribe videos from Xiaohongshu (小红书), Bilibili (B站), or YouTube to text
  using local faster-whisper large-v3. No login, no API key, works fully offline.

  ALWAYS use this skill when the user:
  - shares a xiaohongshu.com, xhslink.com, bilibili.com, or youtube.com URL and wants text/transcript
  - says "转录", "提取文字", "转成文字", "视频转文字", "帮我看看视频说了什么"
  - says "transcribe", "extract text", "video to text", "what does this video say"
  - shares any video link and asks for content summary or transcript
---

# 小红书视频转文字

从小红书/B站视频链接到文字稿的一键工作流，全程无需登录、无需 API Key。

## 目录结构

```
/Volumes/warren/xhs/
├── 博主名字A/
│   ├── 视频标题A.mp4
│   ├── 视频标题A.md
│   └── 视频标题B.mp4
└── 博主名字B/
    └── ...
```

---

##模式一：仅下载视频

如果用户只说"下载"、"download"，或明确只需要视频文件，则执行此步骤：

**B站/YouTube：**
```bash
mkdir -p "/Volumes/warren/xhs/%(uploader)s"
yt-dlp -S "vcodec:h264,res,acodec:m4a" --merge-output-format mp4 \
  -o "/Volumes/warren/xhs/%(uploader)s/%(title)s.mp4" "视频链接"
```

**小红书**（yt-dlp 无法提取博主昵称，需先抓取页面）：
```bash
VIDEO_URL="视频链接"
NICKNAME=$(python3 ~/.claude/skills/xhs-transcribe/scripts/get_xhs_nickname.py "$VIDEO_URL")
# Fallback to uploader_id if nickname extraction fails
if [ -z "$NICKNAME" ]; then
    NICKNAME=$(yt-dlp --dump-json --no-download "$VIDEO_URL" 2>/dev/null | grep -o '"uploader_id":"[^"]*"' | cut -d'"' -f4)
fi
mkdir -p "/Volumes/warren/xhs/${NICKNAME}"
yt-dlp -S "vcodec:h264,res,acodec:m4a" --merge-output-format mp4 \
  -o "/Volumes/warren/xhs/${NICKNAME}/%(title)s.mp4" "$VIDEO_URL"
```

> **小红书链接要求**：必须包含 `xsec_token` 参数的完整链接，或 `xhslink.com` 短链。
> 用户应从小红书 App「分享 → 复制链接」获取，裸 note_id 无法下载。
> **YouTube**：直接使用 `youtube.com/watch?v=ID` 或 `youtu.be/ID` 链接。

---

## 模式二：下载并转录

如果用户说"转录"、"提取文字"、"转成文字"等，则执行完整流程：

### 第一步：下载视频

**B站/YouTube：**
```bash
mkdir -p "/Volumes/warren/xhs/%(uploader)s"
yt-dlp -S "vcodec:h264,res,acodec:m4a" --merge-output-format mp4 \
  -o "/Volumes/warren/xhs/%(uploader)s/%(title).60s.mp4" "视频链接"
```

**小红书**：
```bash
VIDEO_URL="视频链接"
NICKNAME=$(python3 ~/.claude/skills/xhs-transcribe/scripts/get_xhs_nickname.py "$VIDEO_URL")
if [ -z "$NICKNAME" ]; then
    NICKNAME=$(yt-dlp --dump-json --no-download "$VIDEO_URL" 2>/dev/null | grep -o '"uploader_id":"[^"]*"' | cut -d'"' -f4)
fi
mkdir -p "/Volumes/warren/xhs/${NICKNAME}"
yt-dlp -S "vcodec:h264,res,acodec:m4a" --merge-output-format mp4 \
  -o "/Volumes/warren/xhs/${NICKNAME}/%(title).60s.mp4" "$VIDEO_URL"
```

### 第二步：转录
```bash
python3 ~/.claude/skills/xhs-transcribe/scripts/transcribe.py "/Volumes/warren/xhs/博主名字/视频标题.mp4"
# 文字稿自动保存在同目录，文件名与视频相同但扩展名为 .md
# 结果：/Volumes/warren/xhs/博主名字/视频标题.md
```

### 第三步：整理文字稿

转录完成后，做两步清理：

1. **合并重复行**：如果同一行文字连续出现 3 次以上，合并为一行（转录末尾常见）
2. **还原章节结构**：如果文字稿中出现明显的结构标记（如"第一遍""第三遍""第X章"），将其提升为 Markdown 标题（`###`），让输出更易读

### 第四步：加入视频链接

用 `Edit` 工具在 .md 文件的"语言"行后面插入视频链接（从用户提供的原始链接中提取，格式：`https://www.xiaohongshu.com/discovery/item/xxxxx`）。

### 第五步：生成并写入人工整理版

基于【完整文字稿】，由 Claude 生成一份人工整理版，要求：
- **不改变**口播原文的词语表达和意思
- **不增不改**原文内容，包括重复的表达也要保留
- **只修正**常见错别字，如同音字错误（的/得/地、这/那、着/了 等）
- 适当添加标点符号（句号、逗号），使语句通顺
- 可适当分段落（按话题或时间推进），但不重组句意

**关键：人工整理版生成后，必须先用 `Edit` 工具将其追加写入 .md 文件末尾（作为第三个板块【人工整理版】），然后再展示给用户。**

### 第六步：展示结果

展示给用户：
- 文字稿保存路径
- 视频时长和语言
- 按章节整理后的完整文字稿内容
- 【人工整理版】
- 如有字幕误识别（如"中文字幕 XXX"反复出现），在末尾说明这是正常现象

---

## 注意事项

- **首次运行**：large-v3 模型约 1.5GB，自动从 HuggingFace 下载，需要几分钟
- **后续运行**：模型缓存在 `~/.cache/huggingface/`，无需重复下载
- **转录速度**：CPU 下约每分钟音频耗时 1.5 分钟（12核）；视频较长时建议后台运行
- **中文字幕干扰**：视频若有叠加字幕，可能被误识别进文字稿，属正常现象
- **语言设置**：转录脚本默认 `language="zh"`，英文/日文视频传入语言参数，如 `--lang en` 或 `--lang auto`
- **环境依赖**：
  ```bash
  pip install faster-whisper yt-dlp
  ```