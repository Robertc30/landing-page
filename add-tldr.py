#!/usr/bin/env python3
"""
Daily TLDR Generator for TechQuest.AI Blog

This script runs at midnight and automatically generates a TLDR summary
for that day's blog entry, inserting it at the top of the post.

Usage:
    python add-tldr.py [--date YYYY-MM-DD] [--dry-run]
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime, date
from pathlib import Path

# Configuration
BLOG_DIR = Path(__file__).parent / "blog"
TLDR_TEMPLATE = '''
<div class="tldr">
    <strong>TL;DR:</strong> {summary}
</div>
'''

class TLDRGenerator:
    """Generates and inserts TLDR summaries into blog posts."""
    
    def __init__(self, blog_dir: Path):
        self.blog_dir = Path(blog_dir)
        
    def find_todays_post(self, target_date: date = None) -> Path:
        """Find the blog post for the given date."""
        if target_date is None:
            target_date = date.today()
            
        # Look for files matching YYYY-MM-DD-*.html pattern
        date_prefix = target_date.strftime("%Y-%m-%d")
        
        for f in self.blog_dir.glob(f"{date_prefix}-*.html"):
            if f.is_file() and f.name != "index.html":
                return f
                
        return None
    
    def extract_text_content(self, html_path: Path) -> str:
        """Extract readable text from HTML post, excluding headers/footers."""
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract body content between <div class="post"> tags
        post_match = re.search(r'<div class="post">(.*?)</div>\s*</div>\s*</body>', 
                               content, re.DOTALL)
        
        if not post_match:
            return ""
        
        post_html = post_match.group(1)
        
        # Strip HTML tags to get plain text
        text = re.sub(r'<[^>]+>', ' ', post_html)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def generate_summary(self, text: str, max_length: int = 280) -> str:
        """
        Generate a TLDR summary from the post content.
        
        Uses extractive summarization - grabs the first significant paragraph(s)
        that capture the essence of the post.
        """
        if not text:
            return "No content to summarize."
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Filter out very short sentences and headers
        meaningful = [s.strip() for s in sentences if len(s.strip()) > 40]
        
        if not meaningful:
            return text[:max_length]
        
        # First sentence is usually the hook
        summary = meaningful[0]
        
        # Add second sentence if it adds context and we're under the limit
        if len(meaningful) > 1:
            potential = summary + ". " + meaningful[1]
            if len(potential) <= max_length:
                summary = potential
            else:
                # Trim first sentence
                summary = summary[:max_length-3] + "..."
        
        # Add period if missing
        if not summary.endswith('.'):
            summary += '.'
            
        return summary
    
    def read_existing_tldr(self, html_path: Path) -> bool:
        """Check if TLDR already exists in the post."""
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return '<div class="tldr">' in content
    
    def insert_tldr(self, html_path: Path, summary: str) -> bool:
        """Insert TLDR at the top of the post content."""
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if TLDR already exists
        if self.read_existing_tldr(html_path):
            print(f"[SKIP] TLDR already exists in {html_path.name}")
            return False
        
        # Create TLDR block
        tldr_block = TLDR_TEMPLATE.format(summary=summary)
        
        # Insert after the <h1> tag (post title)
        pattern = r'(<h1[^>]*>.*?</h1>\s*)'
        replacement = r'\1\n\n' + tldr_block + '\n\n'
        
        new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
        
        # Also inject TLDR styles if not present
        if '<style>' in content and '.tldr {' not in content:
            style_block = '''
.tldr {
    background: linear-gradient(135deg, #1e3a5f 0%, #0d1117 100%);
    border-left: 4px solid #58a6ff;
    padding: 16px 20px;
    margin: 20px 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.95em;
    color: #c9d1d9;
}
.tldr strong {
    color: #58a6ff;
}
'''
            new_content = new_content.replace('</style>', style_block + '</style>', 1)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return True
    
    def process_date(self, target_date: date = None, dry_run: bool = False) -> dict:
        """Process a single date and add TLDR to that day's post."""
        result = {
            "date": (target_date or date.today()).isoformat(),
            "post_found": False,
            "tldr_added": False,
            "summary": None,
            "error": None
        }
        
        # Find today's post
        post_path = self.find_todays_post(target_date)
        
        if post_path is None:
            result["error"] = f"No blog post found for {(target_date or date.today()).isoformat()}"
            print(f"[ERR] {result['error']}")
            return result
        
        result["post_found"] = True
        result["post_path"] = str(post_path)
        print(f"[POST] Found: {post_path.name}")
        
        # Check for existing TLDR
        if self.read_existing_tldr(post_path):
            print(f"[SKIP] TLDR already exists, skipping")
            result["tldr_added"] = False
            result["message"] = "TLDR already present"
            return result
        
        # Extract and summarize
        text = self.extract_text_content(post_path)
        
        if not text:
            result["error"] = "Could not extract content from post"
            print(f"[ERR] {result['error']}")
            return result
        
        summary = self.generate_summary(text)
        result["summary"] = summary

        print(f"[TLDR] Generated: {summary[:100]}...")

        if dry_run:
            print(f"[DRY RUN] Would insert TLDR into {post_path.name}")
            return result
        
        # Insert TLDR
        if self.insert_tldr(post_path, summary):
            result["tldr_added"] = True
            print(f"[OK] Added TLDR to {post_path.name}")
        else:
            result["error"] = "Failed to insert TLDR"
            
        return result


def main():
    parser = argparse.ArgumentParser(description="Generate TLDR summaries for blog posts")
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--blog-dir", type=str, help="Path to blog directory")
    
    args = parser.parse_args()
    
    # Parse date
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Set blog directory
    blog_dir = Path(args.blog_dir) if args.blog_dir else BLOG_DIR
    
    if not blog_dir.exists():
        print(f"❌ Blog directory not found: {blog_dir}")
        sys.exit(1)
    
    # Process
    generator = TLDRGenerator(blog_dir)
    result = generator.process_date(target_date, args.dry_run)
    
    # Output result as JSON for cron logging
    print(f"\n--- Result ---")
    print(json.dumps(result, indent=2))
    
    return 0 if result["tldr_added"] or result.get("message") == "TLDR already present" else 1


if __name__ == "__main__":
    sys.exit(main())
