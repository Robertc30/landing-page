"""
Fix image issues:
1. Replace deleted TechQuestv1.png logo references with an existing image
2. Add missing title/width/height attributes to images
"""
import re
from pathlib import Path

def fix_images():
    base_path = Path(__file__).parent
    html_files = list(base_path.glob("**/*.html"))
    
    # Logo replacement: TechQuestv1.png → blog/images/kewl-kai.jpg (for root) or images/kewl-kai.jpg (for subfolders)
    # Root files need: blog/images/kewl-kai.jpg
    # Blog files need: images/kewl-kai.jpg
    
    logo_pattern_root = r'<img src="\.\./TechQuestv1\.png" alt="([^"]+)"'
    logo_replacement_root = '<img src="blog/images/kewl-kai.jpg" alt="\\1" title="KAI - TechQuest.AI" width="50" height="50"'
    
    logo_pattern_blog = r'<img src="\.\./TechQuestv1\.png" alt="([^"]+)"'
    logo_replacement_blog = '<img src="images/kewl-kai.jpg" alt="\\1" title="KAI - TechQuest.AI" width="50" height="50"'
    
    # Image attributes to add
    image_updates = {
        # Blog post images needing title/width/height
        "blog/2026-02-02-openclaw-setup.html": [
            {
                "pattern": r'<img src="images/kewl-kai\.jpg" alt="KAI Vibes" style="([^"]+)"',
                "replacement": '<img src="images/kewl-kai.jpg" alt="KAI Vibes" title="KAI Vibes" width="600" style="\\1"'
            },
        ],
        "blog/2026-02-03-landing-page-updates.html": [
            {
                "pattern": r'<img src="images/landing-page-mobile\.jpg" alt="TechQuest\.AI landing page on mobile" style="([^"]+)"',
                "replacement": '<img src="images/landing-page-mobile.jpg" alt="TechQuest.AI landing page on mobile" title="Mobile landing page" width="600" style="\\1"'
            },
            {
                "pattern": r'<img src="images/day-two-1\.jpg" alt="Landing page overview" style="([^"]+)"',
                "replacement": '<img src="images/day-two-1.jpg" alt="Landing page overview" title="Landing page overview" width="600" style="\\1"'
            },
            {
                "pattern": r'<img src="images/day-two-2\.jpg" alt="Tools section detail" style="([^"]+)"',
                "replacement": '<img src="images/day-two-2.jpg" alt="Tools section detail" title="Tools section detail" width="600" style="\\1"'
            },
            {
                "pattern": r'<img src="images/day-two-3\.jpg" alt="Reviews page" style="([^"]+)"',
                "replacement": '<img src="images/day-two-3.jpg" alt="Reviews page" title="Reviews page" width="600" style="\\1"'
            },
        ],
        # Reviews pages needing image attributes
        "reviews/itemfits.html": [
            {
                "pattern": r'<img src="images/itemfits\.png" alt="ItemFits interface"',
                "replacement": '<img src="images/itemfits.png" alt="ItemFits interface" title="ItemFits interface" width="600"'
            },
        ],
        "reviews/minimax.html": [
            {
                "pattern": r'<img src="images/minimax\.png" alt="MiniMax dashboard"',
                "replacement": '<img src="images/minimax.png" alt="MiniMax dashboard" title="MiniMax dashboard" width="600"'
            },
        ],
    }
    
    fixed_count = 0
    
    for html_file in html_files:
        content = html_file.read_text(encoding='utf-8')
        original = content
        
        # Determine which logo pattern to use based on file location
        rel_path = html_file.relative_to(base_path)
        if str(rel_path).startswith("blog/") or str(rel_path).startswith("reviews/"):
            # Subfolder files: ../TechQuestv1.png → images/kewl-kai.jpg
            pattern = logo_pattern_blog
            replacement = logo_replacement_blog
        else:
            # Root files: ../TechQuestv1.png → blog/images/kewl-kai.jpg
            pattern = logo_pattern_root
            replacement = logo_replacement_root
        
        # Fix logo references
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            print(f"  Fixed logo in {rel_path}")
            content = new_content
            fixed_count += 1
        
        # Apply file-specific image updates
        rel_path = html_file.relative_to(base_path)
        if str(rel_path) in image_updates:
            for update in image_updates[str(rel_path)]:
                new_content = re.sub(update["pattern"], update["replacement"], content)
                if new_content != content:
                    print(f"  Fixed images in {rel_path}")
                    content = new_content
                    fixed_count += 1
        
        if content != original:
            html_file.write_text(content, encoding='utf-8')
    
    print(f"\nFixed {fixed_count} image issue(s)")

if __name__ == "__main__":
    fix_images()
