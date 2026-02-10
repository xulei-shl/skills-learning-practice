import json
from pathlib import Path

# Paths
base_dir = Path.cwd()
output_root = base_dir / "youtube_clips_pro"
context_file = output_root / "context.json"

# Existing files (from previous download)
video_dir = base_dir / "Hassabis_on_an_AI_Shift_Bigger_Than_Industrial_Age_BbIaYFHxW3Y"
video_path = video_dir / "BbIaYFHxW3Y.mp4"
subtitle_path = video_dir / "BbIaYFHxW3Y.en.vtt"

# Create output dir
output_root.mkdir(parents=True, exist_ok=True)

# Mock Context
context = {
  "step": "download_done",
  "video_info": {
    "video_path": str(video_path),
    "subtitle_path": str(subtitle_path),
    "title": "Hassabis on an AI Shift Bigger Than Industrial Age",
    "duration": 1563,
    "file_size": 394166791,
    "video_id": "BbIaYFHxW3Y"
  },
  "chapters": []
}

with open(context_file, 'w') as f:
    json.dump(context, f, indent=2)

print(f"✅ Mock context created at {context_file}")
