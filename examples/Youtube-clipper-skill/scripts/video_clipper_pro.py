#!/usr/bin/env python3
"""
Video Clipper Pro - Orchestrator
负责协调整个剪辑流程，管理文件资产，并与 AI Agent 进行交互（通过 CLI 提示）。
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add current directory to path to import from scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from download_video import download_video
from analyze_subtitles import parse_vtt, prepare_analysis_data
from clip_video import clip_video, extract_subtitle_segment, save_subtitles_as_srt
from burn_subtitles import burn_subtitles
from utils import create_output_dir, time_to_seconds

class VideoClipperPro:
    def __init__(self, output_dir=None, project_name=None):
        """
        初始化 Video Clipper Pro
        
        Args:
            output_dir: 可选的输出目录路径。如果不指定,会智能检测:
                       - 如果在 Skill 目录内运行,使用项目根目录
                       - 否则使用当前工作目录
            project_name: 可选的项目名称。如果不指定,会从 .active_project 读取
        """
        # 1. 确定总输出根目录 (base_output_root)
        if output_dir:
            base_root = Path(output_dir).resolve()
        else:
            # 智能检测输出目录
            current = Path.cwd().resolve()
            
            # 检测是否在 Skill 目录内 (.agent/skills/ 或 .claude/skills/)
            current_str = str(current)
            if "/.agent/skills/" in current_str or "/.claude/skills/" in current_str:
                # 在 Skill 目录内,向上查找到项目根目录
                # 查找包含 .agent 或 .claude 目录的父目录
                while current.parent != current:
                    if (current / ".agent").exists() or (current / ".claude").exists():
                        # 找到项目根目录
                        break
                    current = current.parent
                
                print(f"🔍 检测到在 Skill 目录内运行")
                print(f"   使用项目根目录: {current}")
            
            base_root = current / "youtube_clips_pro"
        
        self.base_output_root = base_root
        self.base_output_root.mkdir(parents=True, exist_ok=True)
        
        # 2. 确定当前项目目录 (project_root)
        if project_name:
            # 用户指定项目
            self.project_root = self.base_output_root / project_name
            self.project_root.mkdir(parents=True, exist_ok=True)
        else:
            # 读取 .active_project
            active_file = self.base_output_root / ".active_project"
            if active_file.exists():
                project_name = active_file.read_text().strip()
                self.project_root = self.base_output_root / project_name
                print(f"📂 当前项目: {project_name}")
            else:
                # 没有活跃项目，使用根目录 (向后兼容旧项目)
                self.project_root = self.base_output_root
                print(f"⚠️  未找到活跃项目，使用根目录 (向后兼容模式)")
        
        # 3. 设置上下文文件路径
        self.context_file = self.project_root / "context.json"
        
        print(f"📁 输出根目录: {self.base_output_root}")
        print(f"📁 项目目录: {self.project_root}")
        
        # Load or initialize context
        self.context = self._load_context()


    def _load_context(self):
        if self.context_file.exists():
            with open(self.context_file, 'r') as f:
                return json.load(f)
        return {"step": "init", "video_info": {}, "chapters": []}

    def _save_context(self):
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2, ensure_ascii=False)

    def step_1_download(self, url, browser=None):
        """Phase 1: Download Video & Subtitles"""
        print(f"🎬 [Phase 1] Downloading Video: {url}")
        if browser:
            print(f"   Using browser cookies: {browser}")
        
        # Call existing download script (下载到总根目录，download_video 会创建项目子目录)
        try:
            result = download_video(url, output_dir=str(self.base_output_root), browser=browser)
            
            # 从返回的路径中提取项目目录
            video_path = Path(result['video_path'])
            project_dir = video_path.parent  # 项目目录: Hassabis.../
            project_name = project_dir.name
            
            # 设置为活跃项目
            self.project_root = project_dir
            active_file = self.base_output_root / ".active_project"
            active_file.write_text(project_name)
            
            # 更新上下文文件路径
            self.context_file = self.project_root / "context.json"
            
            # 保存上下文
            self.context["video_info"] = result
            self.context["step"] = "download_done"
            self._save_context()
            
            print(f"\n✅ Download Complete!")
            print(f"   项目名称: {project_name}")
            print(f"   项目目录: {self.project_root}")
            print(f"   Video: {result['video_path']}")
            print(f"   Subtitles: {result['subtitle_path']}")
            print(f"\n👉 NEXT: Please call 'AnalysisAgent' to analyze the subtitles.")
            print(f"   Command: Provide the subtitle content to AnalysisAgent and ask for a chapter plan.")
            
        except Exception as e:
            print(f"❌ Download Failed: {e}")
            sys.exit(1)

    def step_2_prepare_analysis(self):
        """Phase 2: Prepare Data for Analysis Agent"""
        video_info = self.context.get("video_info")
        if not video_info or not video_info.get("subtitle_path"):
            print("❌ No subtitle file found. Please run step 1 first.")
            return

        vtt_path = video_info["subtitle_path"]
        subtitles = parse_vtt(vtt_path)
        data = prepare_analysis_data(subtitles)
        
        # Save a clean text file for the Agent to read easily
        analysis_txt_path = self.project_root / "for_analysis_agent.txt"
        with open(analysis_txt_path, "w") as f:
            f.write(data["subtitle_text"])
            
        print(f"\n📝 [Phase 2] Data Prepared for Analysis")
        print(f"   Analysis File: {analysis_txt_path}")
        print(f"\n🤖 AGENT INSTRUCTION:")
        print(f"   1. Switch to 'AnalysisAgent'.")
        print(f"   2. Read the file: {analysis_txt_path}")
        print(f"   3. Generate a JSON chapter plan based on the content.")
        print(f"   4. Save the plan to: {self.project_root}/chapters.json")

    def step_3_split_assets(self):
        """Phase 3: Split Video & Subtitles based on chapters.json"""
        chapters_file = self.project_root / "chapters.json"
        
        if not chapters_file.exists():
            print(f"❌ '{chapters_file}' not found.")
            print("   Please ensure AnalysisAgent has saved the chapter plan.")
            return

        with open(chapters_file, 'r') as f:
            chapters_data = json.load(f)
            
        # Handle both array format and object format
        if isinstance(chapters_data, list):
            chapters = chapters_data
        else:
            chapters = chapters_data.get("chapters", [])
            
        if not chapters:
            print("❌ No chapters found in JSON.")
            return

        video_path = self.context["video_info"]["video_path"]
        vtt_path = self.context["video_info"]["subtitle_path"]
        subtitles = parse_vtt(vtt_path)
        
        print(f"\n✂️ [Phase 3] Splitting {len(chapters)} Chapters...")

        for chap in chapters:
            title = chap["title"]
            start = chap["start_time"]
            end = chap["end_time"]
            
            # 1. Create Atomic Folder
            chap_dir = self.project_root / title
            chap_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n   📂 Processing: {title}")
            
            # 2. Clip Video
            output_video = chap_dir / f"{title}_source.mp4"
            if not output_video.exists():
                clip_video(video_path, start, end, str(output_video))
            
            # 3. Extract English Subtitles
            start_sec = time_to_seconds(start)
            end_sec = time_to_seconds(end)
            seg_subs = extract_subtitle_segment(subtitles, start_sec, end_sec)
            
            en_srt_path = chap_dir / "en.srt"
            save_subtitles_as_srt(seg_subs, str(en_srt_path))
            
            # 4. Save Metadata
            with open(chap_dir / "meta.json", "w") as f:
                json.dump(chap, f, indent=2, ensure_ascii=False)

        print(f"\n✅ All Assets Split!")
        print(f"\n🤖 AGENT INSTRUCTION:")
        print(f"   1. Switch to 'TranslationAgent'.")
        print(f"   2. For each folder in {self.project_root}:")
        print(f"      a. Read 'en.srt'")
        print(f"      b. Translate to Chinese (Bilingual style)")
        print(f"      c. Save as 'zh_en.srt'")

    def step_4_burn_final(self):
        """Phase 4: Burn Subtitles (looking for zh_en.srt)"""
        print(f"\n🔥 [Phase 4] Burning Subtitles...")
        
        chapters_file = self.project_root / "chapters.json"
        with open(chapters_file, 'r') as f:
            chapters_data = json.load(f)
            chapters = chapters_data if isinstance(chapters_data, list) else chapters_data.get("chapters", [])
            
        for chap in chapters:
            title = chap["title"]
            chap_dir = self.project_root / title
            
            video_src = chap_dir / f"{title}_source.mp4"
            # Prioritize bilingual, fallback to English
            srt_bi = chap_dir / "zh_en.srt"
            srt_en = chap_dir / "en.srt"
            
            if srt_bi.exists():
                srt_target = srt_bi
                suffix = "bilingual"
            elif srt_en.exists():
                srt_target = srt_en
                suffix = "english"
            else:
                print(f"   ⚠️ No subtitles found for {title}, skipping burn.")
                continue
                
            output_final = chap_dir / f"{title}_final_{suffix}.mp4"
            
            try:
                burn_subtitles(
                    str(video_src),
                    str(srt_target),
                    str(output_final),
                    ffmpeg_path=None, # Auto-detect
                    font_size=24,
                    margin_v=30
                )
            except Exception as e:
                print(f"   ❌ Burn failed for {title}: {e}")

        print("\n✨ Workflow Complete!")

def main():
    clipper = VideoClipperPro()
    
    if len(sys.argv) < 2:
        print("Usage: python video_clipper_pro.py [command]")
        print("Commands:")
        print("  download <url> [--browser <browser>]  - Step 1: Download video")
        print("                                           Optional: --browser chrome|firefox|safari")
        print("  prepare                                - Step 2: Prepare for Analysis")
        print("  split                                  - Step 3: Split assets (after chapters.json exists)")
        print("  burn                                   - Step 4: Burn final subtitles (after translation)")
        return

    cmd = sys.argv[1]
    
    if cmd == "download":
        if len(sys.argv) < 3:
            print("Error: URL required")
            print("Usage: python video_clipper_pro.py download <url> [--browser <browser>]")
            return
        
        url = sys.argv[2]
        browser = None
        
        # Parse optional --browser argument
        if len(sys.argv) >= 5 and sys.argv[3] == "--browser":
            browser = sys.argv[4]
        
        clipper.step_1_download(url, browser=browser)
        
    elif cmd == "prepare":
        clipper.step_2_prepare_analysis()
        
    elif cmd == "split":
        clipper.step_3_split_assets()
        
    elif cmd == "burn":
        clipper.step_4_burn_final()
        
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
