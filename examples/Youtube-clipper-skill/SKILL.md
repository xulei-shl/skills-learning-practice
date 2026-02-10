---
name: youtube-clipper
description: >
  **YouTube 智能精剪 Pro**。
  采用最先进的 "Agentic Workflow" 架构,利用专家级 Subagent 进行内容分析、双语翻译和推特文案生成。
  支持交互式反馈循环和用户章节选择,确保剪辑逻辑、翻译质量和社交媒体文案完全符合用户意图。
  功能:环境检测 -> 下载视频 -> AI 智能切分 (交互式) -> 用户选择 -> 自动提取素材 -> AI 双语翻译 + 推特文案 -> 自动烧录硬字幕。
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
model: claude-sonnet-4-5-20250514
---

# YouTube 智能精剪 Pro (Agentic Workflow)

作为主智能体 (Main Agent),你的职责是 **"指挥官" (Orchestrator)**。
你不再需要亲自去处理正则表达式或逐字翻译,你的任务是协调 Python 脚本和专家 Subagent 来共同完成任务。

## 🗓️ 工作流概览

0.  **环境检测 (Environment Check)**: 确保所有依赖工具就绪。
1.  **下载 (Download)**: 下载视频与字幕素材。
2.  **规划 (Planning)**: 唤醒 `AnalysisAgent` 分析内容,直到用户满意。
3.  **选择 (Selection)**: 用户选择要处理的章节。
4.  **生产 (Production)**: 自动切分选中的章节。
5.  **并行处理 (Parallel Processing)**: 
    - 唤醒 `TranslationAgent` 翻译字幕
    - 唤醒 `TweetAgent` 生成推特文案
    - 自动烧录最终成品
6.  **交付 (Delivery)**: 展示最终成果。

---

## 🚦 执行步骤指南

> ⚠️ **重要**: 所有命令都必须在 Skill 目录下执行！
> 
> **Skill 目录位置**: `.agent/skills/Youtube-clipper-skill/` 或 `.claude/skills/Youtube-clipper-skill/`
> 
> **每次执行命令前，都必须先切换到 Skill 目录**。

请严格遵循以下剧本执行:

### Step 0: 环境检测 (Environment Check)
**确保所有必需工具和依赖都已安装。**

1. 检测 yt-dlp
   ```bash
   cd .agent/skills/Youtube-clipper-skill
   yt-dlp --version
   ```

2. 检测 FFmpeg 和 libass 支持
   ```bash
   cd .agent/skills/Youtube-clipper-skill
   ffmpeg -version
   ffmpeg -filters 2>&1 | grep subtitles
   ```

3. 检测 Python 依赖
   ```bash
   cd .agent/skills/Youtube-clipper-skill
   python3 -c "import yt_dlp; print('✅ yt-dlp available')"
   ```

**如果检测失败**:
- yt-dlp 未安装: `brew install yt-dlp` 或 `pip install yt-dlp`
- FFmpeg 无 libass: `brew install ffmpeg` (macOS)
- Python 依赖缺失: `pip install yt-dlp`

> 💡 必须通过环境检测才能继续

---

### Step 1: 准备素材 (Download)
询问用户 YouTube URL,然后执行:
```bash
cd .agent/skills/Youtube-clipper-skill
python3 scripts/video_clipper_pro.py download <URL> --browser chrome
```

> 💡 **为什么使用 `--browser chrome`?** 
> YouTube 现在会进行机器人检测,使用浏览器 Cookie 可以绕过验证。
> 如果您使用其他浏览器,可以改为 `--browser firefox` 或 `--browser safari`

下载完成后,继续执行:
```bash
cd .agent/skills/Youtube-clipper-skill
python3 scripts/video_clipper_pro.py prepare
```
> 💡 脚本会输出一个 `for_analysis_agent.txt` 文件路径。请记住它。

---

### Step 2: 智能分析 (Analysis Loop)
**这里是关键交互点。**
1.  **切换角色**: 此时,请你调用/扮演 **AnalysisAgent** (`.claude/agents/AnalysisAgent.md`)。
2.  **输入**: 读取 `for_analysis_agent.txt`。
3.  **任务**: 按照 AnalysisAgent 的 Prompt 要求,生成章节方案,并**询问用户反馈**。
4.  **循环**: 如果用户不满意,持续修改,直到用户确认。
5.  **输出**: 最终确认后,请手动将生成的 JSON 内容保存到 `youtube_clips_pro/chapters.json` 文件中。

**✅ 检查点 (必须验证)**:
- 确认 `chapters.json` 已生成
- 验证每个章节都包含以下 7 个字段:
  - `id`: 整数序号 (从 1 开始)
  - `title`: 章节标题 (无特殊字符)
  - `start_time`: 开始时间 (`HH:MM:SS` 格式)
  - `end_time`: 结束时间 (`HH:MM:SS` 格式)
  - `duration_seconds`: 时长(秒)
  - `description`: 章节描述
  - `selected`: 布尔值 (默认 `false`)
- 如格式错误,请参考 `.claude/agents/AnalysisAgent.md` 的输出示例修复

---

### Step 3: 用户选择章节 (User Selection)
**让用户选择要处理的章节。**

1. 展示所有章节列表(带编号):
   ```
   📊 章节列表:
   
   1. [00:00 - 02:00] Google's AI Comeback
   2. [02:00 - 04:00] Google's Full Stack Advantage
   3. [04:00 - 06:00] Robotics Breakthrough Coming
   ...
   ```

2. 询问用户选择:
   ```
   请选择要处理的章节编号:
   - 单个: 输入 "1"
   - 多个: 输入 "1,3,5"
   - 全部: 输入 "all"
   ```

3. 更新 `chapters.json`,为选中的章节添加 `"selected": true` 字段

> 💡 仅处理 selected=true 的章节

---

### Step 4: 原子化生产 (Asset Splitting)
确认 `chapters.json` 存在后,执行:
```bash
cd .agent/skills/Youtube-clipper-skill
python3 scripts/video_clipper_pro.py split
```
> 💡 脚本会为每个**选中的**章节创建独立的文件夹,并生成 `en.srt`。

---

### Step 5: 并行处理 (Parallel Processing)
**对每个选中的章节,并行执行三个任务:**

#### 5.1 翻译字幕 (TranslationAgent)
1. **切换角色**: 调用/扮演 **TranslationAgent** (`.claude/agents/TranslationAgent.md`)
2. **遍历**: 遍历每个 selected=true 的章节文件夹
3. **输入**: 读取 `en.srt`
4. **任务**: 翻译为中英双语
5. **输出**: 保存为 `zh_en.srt`

#### 5.2 生成推特文案 (TweetAgent) ⭐ 新增
1. **切换角色**: 调用/扮演 **TweetAgent** (`.claude/agents/TweetAgent.md`)
2. **遍历**: 遍历每个 selected=true 的章节文件夹
3. **输入**: 读取 `meta.json` (标题、描述)
4. **任务**: 生成推特风格的分享文案
5. **输出**: 保存为 `tweet.md`

#### 5.3 烧录字幕 (Burn Subtitles)
当所有章节都已生成 `zh_en.srt` 后,执行:
```bash
cd .agent/skills/Youtube-clipper-skill
python3 scripts/video_clipper_pro.py burn
```
> 💡 脚本会自动遍历所有目录,检测双语字幕并烧录。

> ⚡ **并行优化**: 翻译、文案生成、烧录可以交替进行,无需等待全部完成。

---

### Step 6: 交付 (Delivery)
向用户展示最终生成的文件列表:

```
✨ 处理完成!

📁 输出目录: /Users/blessed/Desktop/skills/youtube_clips_pro/

已处理章节:
  🎬 Google's AI Comeback/
     ├── Google's AI Comeback_source.mp4 (27.6 MB)
     ├── en.srt
     ├── zh_en.srt
     ├── Google's AI Comeback_final_bilingual.mp4 (28.9 MB)
     ├── meta.json
     └── tweet.md ⭐

  🎬 Robotics Breakthrough Coming/
     ├── ...
     └── tweet.md ⭐

快速预览:
open "/Users/blessed/Desktop/skills/youtube_clips_pro/Google's AI Comeback/Google's AI Comeback_final_bilingual.mp4"
```

---

## 🛠️ 故障排查
*   如果 AnalysisAgent 表现不佳,提醒用户可以提供更具体的指令(如"只切3段")。
*   如果 TranslationAgent 术语不准,可以在 Context 中补充术语表。
*   如果 TweetAgent 文案不够吸引,可以要求重新生成并提供具体方向。
