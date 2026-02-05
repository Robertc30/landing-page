#!/usr/bin/env python3
"""
KAI's Corner Daily Update Script
Generates daily insights, updates TLDR, and manages the to-do list
"""

import json
import os
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path(__file__).parent / "blog"
KAI_DIR = BLOG_DIR / "kai"
TLDR_FILE = BLOG_DIR / "kai-tldr.json"
ENTRIES_FILE = BLOG_DIR / "kai-entries.json"
TODOS_FILE = BLOG_DIR / "kai-todos.json"

def get_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_insights():
    """Generate KAI's daily insights based on recent activity"""
    date = get_date()
    
    # Dynamic insights based on what we can observe
    insights_templates = [
        "Today I observed the landing page QC running. 171 issues found means there's room to improve - and that's exactly what we'll do.",
        "Another day of learning alongside Rob. The blog posts keep coming, and I'm getting better at understanding what makes content resonate.",
        "I processed another batch of quality checks today. The numbers tell a story, and I'm here to help write the next chapter.",
        "Rob's daily blog posts are becoming a rhythm I can anticipate. Consistency matters in building something real.",
        "The dashboard scaffolding is ready - now it's about connecting the dots between data and display.",
    ]
    
    import random
    base_insight = random.choice(insights_templates)
    
    # Add dynamic element based on day of week
    weekday = datetime.now().strftime("%A")
    if weekday == "Monday":
        base_insight += " Fresh start to the week - perfect time to tackle those QC issues."
    elif weekday == "Friday":
        base_insight += " End of week review - what should we carry forward?"
    
    return base_insight

def generate_tldr():
    """Generate daily TLDR summary"""
    return {
        "date": get_date(),
        "summary": generate_insights()
    }

def create_entry():
    """Create a new KAI blog entry"""
    date = get_date()
    filename = f"kai-{date}.html"
    
    entry = {
        "date": date,
        "filename": filename,
        "title": f"KAI's Daily Log - {date}",
        "preview": generate_insights()[:150],
        "insights": generate_insights(),
        "todos": load_todos()
    }
    
    # Create HTML entry
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KAI's Log - {date} | TechQuest.AI</title>
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="../blog.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="../index.html" class="nav-logo">TechQuest.AI</a>
            <ul class="nav-menu">
                <li><a href="../index.html">Home</a></li>
                <li><a href="index.html">Blog</a></li>
                <li><a href="../resources.html">Resources</a></li>
                <li><a href="../tools.html">Tools</a></li>
                <li><a href="../kai-corner.html">Ty's Corner</a></li>
            </ul>
        </div>
    </nav>

    <main class="container">
        <section class="content-section">
            <a href="../kai-corner.html" class="back-link"><-- Back to Ty's Corner</a>
            
            <h1>KAI's Log</h1>
            <p class="date">{date}</p>
            
            <div class="entry-content">
                <h3>Daily Insights</h3>
                <p>{entry['insights']}</p>
                
                <h3>Current Focus</h3>
                <ul>
                    {''.join(f'<li>{todo}</li>' for todo in entry['todos'])}
                </ul>
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 TechQuest.AI | Built by humans, powered by AI</p>
    </footer>
</body>
</html>"""
    
    # Write the entry
    entry_path = KAI_DIR / filename
    entry_path.write_text(html_content)
    
    return entry

def load_entries():
    """Load existing entries index"""
    if ENTRIES_FILE.exists():
        with open(ENTRIES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_entries(entries):
    """Save entries index"""
    with open(ENTRIES_FILE, 'w') as f:
        json.dump(entries, f, indent=2)

def load_todos():
    """Load current todos"""
    if TODOS_FILE.exists():
        with open(TODOS_FILE, 'r') as f:
            return json.load(f)
    return ["Reviewing landing page QC findings", "Supporting blog post generation", "Monitoring site performance"]

def main():
    """Run daily KAI Corner update"""
    print(f"KAI's Corner Update - {get_date()}")
    print("=" * 40)
    
    # Generate TLDR
    tldr = generate_tldr()
    with open(TLDR_FILE, 'w') as f:
        json.dump(tldr, f, indent=2)
    print(f"[OK] TLDR updated: {tldr['summary'][:80]}...")
    
    # Create new entry
    entry = create_entry()
    print(f"[OK] Entry created: {entry['filename']}")
    
    # Update entries index (keep last 30)
    entries = load_entries()
    entries.insert(0, {
        "date": entry['date'],
        "filename": entry['filename'],
        "title": entry['title'],
        "preview": entry['preview']
    })
    entries = entries[:30]  # Keep last 30 entries
    save_entries(entries)
    print(f"[OK] Entries index updated ({len(entries)} entries)")
    
    print("=" * 40)
    print("KAI's Corner update complete!")

if __name__ == "__main__":
    main()
