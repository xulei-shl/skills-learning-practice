
import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from burn_subtitles import burn_subtitles
from utils import format_file_size

def burn_all_chapters():
    base_dir = Path("/Users/blessed/Desktop/skills/.agent/skills/Youtube-clipper-skill/youtube-clips/20260124_173529")
    
    chapters = [
        "Robotics_Breakthrough",
        "China_AI_Competition",
        "AGI_Timeline_2030",
        "Post_Scarcity_Vision"
    ]

    print(f"🔥 Starting batch subtitle burn in {base_dir}")

    for chapter in chapters:
        chapter_dir = base_dir / chapter
        if not chapter_dir.exists():
            print(f"⚠️ Chapter directory not found: {chapter_dir}")
            continue

        print(f"\nProcessing Chapter: {chapter}")
        
        video_path = chapter_dir / f"{chapter}_clip.mp4"
        srt_path = chapter_dir / f"{chapter}_original.srt"
        output_path = chapter_dir / f"{chapter}_with_subtitles.mp4"

        if not video_path.exists():
            print(f"❌ Video file missing: {video_path}")
            continue
        
        if not srt_path.exists():
            print(f"❌ Subtitle file missing: {srt_path}")
            continue

        try:
            burn_subtitles(
                str(video_path),
                str(srt_path),
                str(output_path),
                # ffmpeg_path=None, # Let it detect or use default
                font_size=24,
                margin_v=30
            )
        except Exception as e:
            print(f"❌ Failed to burn subtitles for {chapter}: {e}")

    print("\n✅ Batch processing completed!")
    print(f"Output directory: {base_dir}")

if __name__ == "__main__":
    burn_all_chapters()
