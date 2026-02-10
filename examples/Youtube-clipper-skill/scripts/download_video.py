#!/usr/bin/env python3
"""
下载 YouTube 视频和字幕
使用 yt-dlp 下载视频（最高 1080p）和英文字幕
"""

import sys
import json
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("❌ Error: yt-dlp not installed")
    print("Please install: pip install yt-dlp")
    sys.exit(1)

from utils import (
    validate_url,
    sanitize_filename,
    format_file_size,
    get_video_duration_display,
    ensure_directory
)



def download_video(url: str, output_dir: str = None, browser: str = None) -> dict:
    """
    下载 YouTube 视频和字幕

    Args:
        url: YouTube URL
        output_dir: 输出目录，默认为当前目录
        browser: 提取 Cookie 的浏览器名称 (例如: chrome, firefox)

    Returns:
        dict: {
            'video_path': 视频文件路径,
            'subtitle_path': 字幕文件路径,
            'title': 视频标题,
            'duration': 视频时长（秒）,
            'file_size': 文件大小（字节）
        }

    Raises:
        ValueError: 无效的 URL
        Exception: 下载失败
    """
    # 验证 URL
    if not validate_url(url):
        raise ValueError(f"Invalid YouTube URL: {url}")

    # 设置输出目录
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    output_dir = ensure_directory(output_dir)

    print(f"🎬 开始下载视频...")
    print(f"   URL: {url}")
    print(f"   输出目录: {output_dir}")
    if browser:
        print(f"   使用浏览器 Cookie: {browser}")

    # 配置 yt-dlp 选项 - 第一阶段：仅获取信息
    ydl_opts_info = {
        'quiet': True,
        'no_warnings': True,
        'js_runtimes': {'node': {}},
        'remote_components': {'ejs:github': {}},
        'cookiesfrombrowser': (browser,) if browser else None,
    }

    try:
        # 1. 先获取视频信息
        print(f"📊 获取视频信息...")
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            video_id = info.get('id', 'unknown')
            duration = info.get('duration', 0)

            print(f"   标题: {title}")
            print(f"   时长: {get_video_duration_display(duration)}")
            print(f"   视频ID: {video_id}")

        # 2. 创建项目目录: <Title>_<ID>
        # 清理标题中的特殊字符
        safe_title = sanitize_filename(title)
        project_dir_name = f"{safe_title}_{video_id}"
        
        # 如果指定了 output_dir，则是将其作为父目录
        project_dir = output_dir / project_dir_name
        project_dir = ensure_directory(project_dir)
        
        print(f"   创建项目目录: {project_dir}")

        # 3. 配置下载选项
        ydl_opts = {
            # 视频格式：最高 1080p，优先 mp4
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',

            # 输出模板：直接保存到项目目录
            'outtmpl': str(project_dir / '%(id)s.%(ext)s'),

            # 下载字幕
            'writesubtitles': True,
            'writeautomaticsub': True,  # 自动字幕作为备选
            'subtitleslangs': ['en'],   # 英文字幕
            'subtitlesformat': 'vtt',   # VTT 格式

            # 不下载缩略图
            'writethumbnail': False,

            # 静默模式（减少输出）
            'quiet': False,
            'no_warnings': False,

            # 启用 Node.js 运行时解决 JS Challenge
            'js_runtimes': {'node': {}},
            'remote_components': {'ejs:github': {}},

            # 进度钩子
            'progress_hooks': [_progress_hook],
        }
        
        # 添加浏览器 Cookie 支持
        if browser:
            ydl_opts['cookiesfrombrowser'] = (browser,)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 下载视频
            print(f"\n📥 开始下载...")
            # 注意：此处不再重新 extract_info，直接下载
            # 但为了稳妥，还是让 yt-dlp 处理
            ydl.download([url])
            
            # 手动构建预期的文件路径
            video_path = project_dir / f"{video_id}.mp4"

            # 查找字幕文件
            subtitle_path = None
            subtitle_exts = ['.en.vtt', '.vtt']
            for ext in subtitle_exts:
                potential_sub = video_path.with_suffix(ext)
                # 处理带语言代码的字幕文件
                if not potential_sub.exists():
                    # 尝试 <filename>.en.vtt 格式
                    stem = video_path.stem
                    potential_sub = video_path.parent / f"{stem}.en.vtt"

                if potential_sub.exists():
                    subtitle_path = potential_sub
                    break

            # 获取文件大小
            file_size = video_path.stat().st_size if video_path.exists() else 0

            # 验证下载结果
            if not video_path.exists():
                raise Exception("Video file not found after download")

            print(f"\n✅ 视频下载完成: {video_path.name}")
            print(f"   大小: {format_file_size(file_size)}")

            if subtitle_path and subtitle_path.exists():
                print(f"✅ 字幕下载完成: {subtitle_path.name}")
            else:
                print(f"⚠️  未找到英文字幕")
                print(f"   提示：某些视频可能没有字幕或需要自动生成")

            return {
                'video_path': str(video_path),
                'subtitle_path': str(subtitle_path) if subtitle_path else None,
                'title': title,
                'duration': duration,
                'file_size': file_size,
                'video_id': video_id
            }

    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        raise


def _progress_hook(d):
    """下载进度回调"""
    if d['status'] == 'downloading':
        # 显示下载进度
        if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes']:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            downloaded = format_file_size(d['downloaded_bytes'])
            total = format_file_size(d['total_bytes'])
            speed = d.get('speed', 0)
            speed_str = format_file_size(speed) + '/s' if speed else 'N/A'

            # 使用 \r 实现进度条覆盖
            bar_length = 30
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)

            print(f"\r   [{bar}] {percent:.1f}% - {downloaded}/{total} - {speed_str}", end='', flush=True)
        elif 'downloaded_bytes' in d:
            # 无总大小信息时，只显示已下载
            downloaded = format_file_size(d['downloaded_bytes'])
            speed = d.get('speed', 0)
            speed_str = format_file_size(speed) + '/s' if speed else 'N/A'
            print(f"\r   下载中... {downloaded} - {speed_str}", end='', flush=True)

    elif d['status'] == 'finished':
        print()  # 换行


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="下载 YouTube 视频和字幕")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("output_dir", nargs="?", help="输出目录")
    parser.add_argument("--browser", help="提取 Cookie 的浏览器名称 (例如: chrome, firefox)")
    
    args = parser.parse_args()

    try:
        result = download_video(args.url, args.output_dir, args.browser)

        # 输出 JSON 结果（供其他脚本使用）
        print("\n" + "="*60)
        print("下载结果 (JSON):")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
