"""
Add meta descriptions to review pages that are missing them.
"""
import re
from pathlib import Path

# Meta descriptions for each review page
META_DESCRIPTIONS = {
    "ffmpeg.html": "FFmpeg is the Swiss Army knife of media processing. See how TechQuest.AI uses it for audio conversion and automation workflows.",
    "gemini.html": "Google's Gemini AI model offers powerful reasoning and multimodal capabilities. Read our in-depth review of its strengths and limitations.",
    "google-colab.html": "Google Colab provides free cloud GPUs for development. Learn how we use it for AI experiments and heavy compute tasks.",
    "index.html": "Browse in-depth reviews of tools and technologies that power TechQuest.AI. From AI models to automation platforms.",
    "itemfits.html": "ItemFits helps you find the perfect product dimensions instantly. A review of this practical shopping assistant tool.",
    "minimax.html": "MiniMax offers fast, affordable AI inference. See how this model provider fits into our automation stack.",
    "notebooklm.html": "NotebookLM turns your documents into a research assistant. Read our review of Google's unique AI-powered research tool.",
    "openai-whisper.html": "OpenAI's Whisper provides accurate speech recognition. See how we use it for voice-to-text transcription.",
    "openclaw.html": "OpenClaw provides AI orchestration for autonomous agent workflows. Read our review of this self-hosted platform.",
}

def add_meta_description(file_path: Path, description: str):
    """Add meta description to an HTML file if missing."""
    content = file_path.read_text(encoding='utf-8')
    
    # Check if meta description already exists
    if 'name="description"' in content:
        print(f"  Skipping {file_path.name} - meta description already exists")
        return False
    
    # Find the viewport meta tag and add description after it
    pattern = r'(<meta name="viewport" content="width=device-width, initial-scale=1\.0">)'
    replacement = r'\1\n    <meta name="description" content="' + description + '">'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"  Added meta description to {file_path.name}")
        return True
    else:
        print(f"  Could not find insertion point in {file_path.name}")
        return False

def main():
    reviews_dir = Path(__file__).parent / "reviews"
    count = 0
    
    print("Adding meta descriptions to review pages...\n")
    
    for filename, description in META_DESCRIPTIONS.items():
        file_path = reviews_dir / filename
        if file_path.exists():
            if add_meta_description(file_path, description):
                count += 1
        else:
            print(f"  Warning: {filename} not found")
    
    print(f"\nDone! Added {count} meta descriptions.")

if __name__ == "__main__":
    main()
