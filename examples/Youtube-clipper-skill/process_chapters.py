
import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from analyze_subtitles import parse_vtt
from clip_video import clip_video, extract_subtitle_segment, save_subtitles_as_srt
from utils import create_output_dir, time_to_seconds

def process_chapters():
    video_path = "/Users/blessed/Desktop/skills/.agent/skills/Youtube-clipper-skill/Hassabis_on_an_AI_Shift_Bigger_Than_Industrial_Age_BbIaYFHxW3Y/BbIaYFHxW3Y.mp4"
    vtt_path = "/Users/blessed/Desktop/skills/.agent/skills/Youtube-clipper-skill/Hassabis_on_an_AI_Shift_Bigger_Than_Industrial_Age_BbIaYFHxW3Y/BbIaYFHxW3Y.en.vtt"
    
    chapters = [
        {
            "title": "Robotics_Breakthrough",
            "start": "04:00",
            "end": "05:45",
            "summary": "Demis Hassabis discusses the 'AlphaFold moment' for robotics and physical intelligence."
        },
        {
            "title": "China_AI_Competition",
            "start": "05:47",
            "end": "07:00",
            "summary": "Hassabis analyzes China's AI capabilities, mentioning ByteDance and the 'DeepSeek' reaction."
        },
        {
            "title": "AGI_Timeline_2030",
            "start": "07:00",
            "end": "08:30",
            "summary": "Hassabis predicts AGI by 2030 and defines it as a system capable of scientific creativity."
        },
        {
            "title": "Post_Scarcity_Vision",
            "start": "09:25",
            "end": "10:20",
            "summary": "The vision of a post-scarcity world driven by AI solving energy and material science."
        }
    ]

    print(f"Loading subtitles from {vtt_path}...")
    subtitles = parse_vtt(vtt_path)
    
    output_base_dir = create_output_dir()
    print(f"Output directory: {output_base_dir}")

    for i, chapter in enumerate(chapters, 1):
        print(f"\nProcessing Chapter {i}/{len(chapters)}: {chapter['title']}")
        
        # Clip Video
        chapter_dir = output_base_dir / chapter['title']
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        output_video = chapter_dir / f"{chapter['title']}_clip.mp4"
        clip_video(video_path, chapter['start'], chapter['end'], str(output_video))
        
        # Extract Subtitles
        start_sec = time_to_seconds(chapter['start'])
        end_sec = time_to_seconds(chapter['end'])
        
        segment_subs = extract_subtitle_segment(subtitles, start_sec, end_sec, adjust_timestamps=True)
        output_srt = chapter_dir / f"{chapter['title']}_original.srt"
        save_subtitles_as_srt(segment_subs, str(output_srt))
        
        # Create Summary File
        summary_path = chapter_dir / f"{chapter['title']}_summary.md"
        with open(summary_path, 'w') as f:
            f.write(f"# {chapter['title']}\n\n")
            f.write(f"**Time Range**: {chapter['start']} - {chapter['end']}\n\n")
            f.write(f"**Summary**:\n{chapter['summary']}\n")
            
        print(f"Finished Chapter {i}")

    print("\nAll chapters processed successfully!")
    print(f"Output location: {output_base_dir}")

if __name__ == "__main__":
    process_chapters()
