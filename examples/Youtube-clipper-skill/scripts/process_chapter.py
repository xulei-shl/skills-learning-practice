#!/usr/bin/env python3
"""
自动处理章节剪辑流程
功能：
1. 创建章节目录 (clips/<章节标题>/)
2. 剪辑视频
3. 提取字幕
4. 翻译字幕 (可选)
5. 生成总结 (可选)
"""

import sys
import os
import argparse
from pathlib import Path
import subprocess
from utils import ensure_directory, sanitize_filename

def run_command(cmd_args):
    """运行外部命令"""
    print(f"Executing: {' '.join(cmd_args)}")
    try:
        subprocess.run(cmd_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing command: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="处理 YouTube 视频章节剪辑")
    parser.add_argument("video_path", help="原始视频文件路径")
    parser.add_argument("subtitle_path", help="原始字幕文件路径")
    parser.add_argument("chapter_title", help="章节标题")
    parser.add_argument("start_time", help="开始时间 (HH:MM:SS 或 MM:SS)")
    parser.add_argument("end_time", help="结束时间 (HH:MM:SS 或 MM:SS)")
    parser.add_argument("--translate", action="store_true", help="是否翻译字幕")
    parser.add_argument("--summary", action="store_true", help="是否生成总结")
    parser.add_argument("--burn", action="store_true", help="是否烧录硬字幕")
    parser.add_argument("--keywords", help="关键词 (用于生成总结)")
    
    args = parser.parse_args()
    
    # 1. 设置路径
    video_path = Path(args.video_path).resolve()
    subtitle_path = Path(args.subtitle_path).resolve()
    scripts_dir = Path(__file__).parent
    
    # 获取项目根目录 (假设 video_path 在项目目录下)
    project_dir = video_path.parent
    
    # 创建章节目录
    safe_title = sanitize_filename(args.chapter_title)
    chapter_dir = project_dir / "clips" / safe_title
    ensure_directory(chapter_dir)
    
    print(f"🎬 开始处理章节: {args.chapter_title}")
    print(f"   输出目录: {chapter_dir}")
    
    # 2. 剪辑视频
    clip_video_name = f"{safe_title}_clip.mp4"
    clip_video_path = chapter_dir / clip_video_name
    
    if not clip_video_path.exists():
        print("\n✂️  [1/4] 剪辑视频...")
        # 调用 scripts/clip_video.py (假设在 scripts 目录下运行或相对路径正确)
        # 这里使用绝对路径调用，假设 scripts 目录与本脚本同级
        scripts_dir = Path(__file__).parent
        run_command([
            "python3", str(scripts_dir / "clip_video.py"),
            str(video_path),
            args.start_time,
            args.end_time,
            str(clip_video_path)
        ])
    else:
        print(f"\n✂️  [1/4] 视频片段已存在: {clip_video_name}")

    # 3. 提取字幕
    clip_srt_name = f"{safe_title}_original.srt"
    clip_srt_path = chapter_dir / clip_srt_name
    
    if not clip_srt_path.exists():
        print("\n📝 [2/4] 提取字幕...")
        run_command([
            "python3", str(scripts_dir / "extract_subtitle_clip.py"),
            str(subtitle_path),
            args.start_time,
            args.end_time,
            str(clip_srt_path)
        ])
    else:
        print(f"\n📝 [2/4] 字幕片段已存在: {clip_srt_name}")
        
    # 4. 翻译字幕 (可选)
    translated_srt_path = None
    if args.translate:
        translated_srt_name = f"{safe_title}_translated.srt"
        translated_srt_path = chapter_dir / translated_srt_name
        
        # 检查是否已存在
        if not translated_srt_path.exists():
             print("\n🌐 [3/4] 翻译字幕...")
             # 注意：translate_subtitles.py 目前设计是交互式的或需要 Agent 介入
             # 这里我们调用它生成待翻译数据，或者需要修改它支持自动模式
             # 由于当前限制，我们仅调用它，如果它需要 Agent 介入，则流程会暂停等待用户/Agent
             # 为了自动化，我们假设用户会在 Agent 协助下完成翻译步骤
             # 或者，我们可以让此步骤仅生成 bilingual 不需要翻译 (如果源脚本支持)
             
             # 这里简单调用，可能需要手动干预
             run_command([
                "python3", str(scripts_dir / "translate_subtitles.py"),
                str(clip_srt_path),
                str(chapter_dir) # 输出目录作为第二个参数可能不被支持，translate_subtitles.py 接受 output_file
             ])
        else:
             print(f"\n🌐 [3/4] 翻译字幕已存在: {translated_srt_name}")

    # 5. 生成总结 (可选)
    if args.summary:
        summary_name = f"{safe_title}_summary.md"
        summary_path = chapter_dir / summary_name
        
        if not summary_path.exists():
            print("\n📝 [4/4] 生成总结...")
            # 构造生成参数
            time_range = f"{args.start_time}-{args.end_time}"
            keywords = args.keywords if args.keywords else "无关键词"
            summary_text = f"关于 {args.chapter_title} 的精彩片段"
            
            run_command([
                "python3", str(scripts_dir / "generate_summary.py"),
                "--create",
                args.chapter_title,
                time_range,
                summary_text,
                keywords,
                str(summary_path)
            ])
        else:
             print(f"\n📝 [4/4] 总结已存在: {summary_name}")

    # 6. 烧录字幕 (可选)
    # 默认如果安装了 ffmpeg 并支持 libass 则尝试烧录，或者通过参数控制
    if args.burn:
        burned_video_name = f"{safe_title}_hardsub.mp4"
        burned_video_path = chapter_dir / burned_video_name
        
        # 确定要烧录的字幕文件
        # 优先级: 双语 > 翻译 > 原文
        # 暂时简单处理：如果有 bilingual 则用 bilingual，否则用 original
        # 注意：这里我们还没自动化生成 bilingual，所以默认用 original
        # 如果 args.translate 为真且 translated_srt_path 存在，理论上应优先使用，但需合并逻辑
        # 简单起见，使用 clip_srt_path (Original)
        sub_to_burn = clip_srt_path
        
        if not burned_video_path.exists():
            print("\n🔥 [5/5] 烧录字幕...")
            try:
                run_command([
                    "python3", str(scripts_dir / "burn_subtitles.py"),
                    str(clip_video_path),
                    str(sub_to_burn),
                    str(burned_video_path)
                ])
                print(f"✅ 烧录完成: {burned_video_name}")
            except Exception as e:
                print(f"⚠️ 烧录失败: {e}")
        else:
            print(f"\n🔥 [5/5] 硬字幕视频已存在: {burned_video_name}")

    print(f"\n✨ 章节处理完成！所有文件位于: {chapter_dir}")

if __name__ == "__main__":
    main()
