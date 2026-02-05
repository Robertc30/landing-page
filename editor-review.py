#!/usr/bin/env python3
"""
Landing Page Editor Review
Content and design quality review for landing page HTML files.
"""

import os
import re
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys


@dataclass
class EditorIssue:
    """Represents a single editorial issue."""
    severity: str  # error, warning, suggestion
    category: str  # readability, vague_language, etc.
    file: str
    message: str
    suggestion: str = ""
    line: int = 0


@dataclass
class EditorReport:
    """Complete editor review report."""
    timestamp: str = ""
    base_path: str = ""
    total_files_analyzed: int = 0
    readability_scores: Dict[str, float] = field(default_factory=dict)
    total_issues: int = 0
    issues: List[Dict] = field(default_factory=list)
    suggestions: List[Dict] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)


class EditorReview:
    """Main editor review class."""
    
    # Words that indicate vague language
    VAGUE_WORDS = {
        'stuff', 'things', 'basically', 'really', 'very', 'quite', 'somewhat',
        'kind of', 'sort of', 'maybe', 'perhaps', 'probably', 'awesome', 'amazing',
        'fantastic', 'incredible', 'nice', 'good', 'bad', 'great', 'terrible',
        'awesome', 'cool', 'neat', 'interesting', 'various', 'several', 'many',
        'lots', 'heaps', 'tons', 'loads', 'masses', 'numerous'
    }
    
    # Common passive voice patterns (simplified)
    PASSIVE_PATTERNS = re.compile(
        r'\b(is|are|was|were|been|being)\s+\w+ed\b',
        re.IGNORECASE
    )
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.html_files: List[Path] = []
        self.issues: List[EditorIssue] = []
        
    def run_all_checks(self) -> EditorReport:
        """Run all editorial checks and return a report."""
        report = EditorReport(
            timestamp=datetime.now().isoformat(),
            base_path=str(self.base_path)
        )
        
        # Discover files
        self._discover_files()
        report.total_files_analyzed = len(self.html_files)
        
        # Run all checks
        self._check_readability()
        self._check_vague_language()
        self._check_passive_voice()
        self._check_heading_structure()
        self._check_images()
        self._check_links()
        self._check_seo_basics()
        self._check_typography()
        
        # Build report
        report.issues = [asdict(issue) for issue in self.issues]
        
        # Calculate overall readability
        if self.html_files:
            readability_scores = []
            for html_file in self.html_files:
                try:
                    content = html_file.read_text(encoding='utf-8', errors='ignore')
                    score = self._calculate_readability(content)
                    if score > 0:
                        readability_scores.append(score)
                except:
                    pass
            
            if readability_scores:
                report.readability_scores = {
                    'average': sum(readability_scores) / len(readability_scores),
                    'min': min(readability_scores),
                    'max': max(readability_scores),
                    'files_analyzed': len(readability_scores)
                }
        
        report.total_issues = len(self.issues)
        report.summary = {
            'overall_grade': self._calculate_grade(),
            'readability_avg': report.readability_scores.get('average', 0),
            'total_suggestions': len([i for i in self.issues if i.severity == 'suggestion']),
            'total_warnings': len([i for i in self.issues if i.severity == 'warning']),
            'total_errors': len([i for i in self.issues if i.severity == 'error']),
            'category_counts': self._count_by_category()
        }
        
        return report
    
    def _discover_files(self):
        """Discover all HTML files."""
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith('.html'):
                    self.html_files.append(Path(root) / file)
    
    def _extract_text(self, html: str) -> str:
        """Extract plain text from HTML."""
        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Decode common entities
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_readability(self, html: str) -> float:
        """Calculate Flesch Reading Ease score."""
        text = self._extract_text(html)
        
        if not text:
            return 0
        
        # Count sentences (basic approximation)
        sentences = len(re.split(r'[.!?]+', text))
        if sentences == 0:
            sentences = 1
        
        # Count words
        words = text.split()
        word_count = len(words)
        if word_count == 0:
            return 0
        
        # Count syllables (basic approximation)
        syllables = self._count_syllables(text)
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (word_count / sentences)) - (84.6 * (syllables / word_count))
        
        return max(0, min(100, score))
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (basic approximation)."""
        words = text.lower().split()
        total = 0
        
        for word in words:
            # Remove non-alphabetic characters
            word = re.sub(r'[^a-z]', '', word)
            if not word:
                continue
            
            # Count vowel groups
            vowel_groups = len(re.findall(r'[aeiouy]+', word))
            
            # Handle special cases
            if word.endswith('e') and not word.endswith('le'):
                syllable_count = max(1, vowel_groups - 1)
            elif word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
                syllable_count = vowel_groups
            else:
                syllable_count = max(1, vowel_groups)
            
            total += syllable_count
        
        return total
    
    def _check_readability(self):
        """Check overall readability of content."""
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                text = self._extract_text(content)
                
                if not text:
                    continue
                
                # Check sentence length
                sentences = re.split(r'[.!?]+', text)
                long_sentences = 0
                for sentence in sentences:
                    words = sentence.strip().split()
                    if len(words) > 25:
                        long_sentences += 1
                
                if long_sentences > 0:
                    ratio = long_sentences / max(1, len(sentences))
                    if ratio > 0.3:
                        self.issues.append(EditorIssue(
                            severity="warning",
                            category="readability",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"High percentage of long sentences ({ratio*100:.0f}%)",
                            suggestion="Consider breaking up long sentences for better readability",
                            line=0
                        ))
                
                # Check paragraph length
                paragraphs = re.split(r'\n\n+', content)
                long_paragraphs = 0
                for para in paragraphs:
                    para_text = self._extract_text(para)
                    if len(para_text.split()) > 100:
                        long_paragraphs += 1
                
                if long_paragraphs > 0:
                    ratio = long_paragraphs / max(1, len(paragraphs))
                    if ratio > 0.4:
                        self.issues.append(EditorIssue(
                            severity="warning",
                            category="readability",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"High percentage of long paragraphs ({ratio*100:.0f}%)",
                            suggestion="Consider breaking long paragraphs into smaller chunks",
                            line=0
                        ))
                        
            except Exception:
                pass
    
    def _check_vague_language(self):
        """Check for vague or weak language."""
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    
                    for word in self.VAGUE_WORDS:
                        if f' {word} ' in line_lower or f' {word}.' in line_lower or f' {word},' in line_lower:
                            self.issues.append(EditorIssue(
                                severity="suggestion",
                                category="vague_language",
                                file=str(html_file.relative_to(self.base_path)),
                                message=f"Vague word found: '{word}'",
                                suggestion=f"Consider using a more specific term instead of '{word}'",
                                line=i + 1
                            ))
                            
            except Exception:
                pass
    
    def _check_passive_voice(self):
        """Check for excessive passive voice usage."""
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                text = self._extract_text(content)
                lines = content.split('\n')
                
                passive_count = 0
                words = text.split()
                total_words = len(words)
                
                if total_words > 0:
                    for line in lines:
                        matches = self.PASSIVE_PATTERNS.findall(line)
                        passive_count += len(matches)
                    
                    if (passive_count / total_words) > 0.15:
                        self.issues.append(EditorIssue(
                            severity="suggestion",
                            category="passive_voice",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"High passive voice usage ({passive_count} instances)",
                            suggestion="Consider using active voice for more direct communication",
                            line=0
                        ))
                        
            except Exception:
                pass
    
    def _check_heading_structure(self):
        """Check heading hierarchy and structure."""
        heading_pattern = re.compile(r'<h([1-6])[^>]*>(.*?)</h\1>', re.IGNORECASE | re.DOTALL)
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                headings = heading_pattern.findall(content)
                
                if not headings:
                    self.issues.append(EditorIssue(
                        severity="warning",
                        category="heading_structure",
                        file=str(html_file.relative_to(self.base_path)),
                        message="No headings found in document",
                        suggestion="Add headings to improve document structure and SEO",
                        line=0
                    ))
                    continue
                
                levels = [int(h[0]) for h in headings]
                for i in range(len(levels) - 1):
                    if levels[i + 1] - levels[i] > 1:
                        self.issues.append(EditorIssue(
                            severity="suggestion",
                            category="heading_structure",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"Skipped heading level: h{levels[i]} to h{levels[i+1]}",
                            suggestion="Use consecutive heading levels (h1 → h2 → h3, etc.)",
                            line=0
                        ))
                        break
                
                h1_count = levels.count(1)
                if h1_count > 1:
                    self.issues.append(EditorIssue(
                        severity="suggestion",
                        category="heading_structure",
                        file=str(html_file.relative_to(self.base_path)),
                        message=f"Multiple h1 headings found ({h1_count})",
                        suggestion="Use only one h1 per page for better SEO",
                        line=0
                    ))
                        
            except Exception:
                pass
    
    def _check_images(self):
        """Check image alt tags and accessibility."""
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if '<img' in line.lower():
                        if 'alt=' not in line.lower():
                            self.issues.append(EditorIssue(
                                severity="error",
                                category="image_accessibility",
                                file=str(html_file.relative_to(self.base_path)),
                                message="Image missing alt attribute",
                                suggestion="Add alt text for accessibility and SEO",
                                line=i + 1
                            ))
                        else:
                            alt_match = re.search(r'alt=["\']([^"\']*)["\']', line, re.IGNORECASE)
                            if alt_match and not alt_match.group(1).strip():
                                self.issues.append(EditorIssue(
                                    severity="suggestion",
                                    category="image_accessibility",
                                    file=str(html_file.relative_to(self.base_path)),
                                    message="Image has empty alt text",
                                    suggestion="Consider adding descriptive alt text if the image conveys information",
                                    line=i + 1
                                ))
                        
                        if 'title=' not in line.lower():
                            self.issues.append(EditorIssue(
                                severity="suggestion",
                                category="image_accessibility",
                                file=str(html_file.relative_to(self.base_path)),
                                message="Image missing title attribute",
                                suggestion="Add title attribute for better tooltip behavior",
                                line=i + 1
                            ))
                        
                        if 'width=' not in line.lower() or 'height=' not in line.lower():
                            self.issues.append(EditorIssue(
                                severity="suggestion",
                                category="image_accessibility",
                                file=str(html_file.relative_to(self.base_path)),
                                message="Image missing width/height attributes",
                                suggestion="Add explicit width and height to prevent layout shifts",
                                line=i + 1
                            ))
                            
            except Exception:
                pass
    
    def _check_links(self):
        """Check link text quality."""
        weak_link_texts = {'click here', 'read more', 'learn more', 'here', 'more', 'link'}
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if '<a ' in line.lower():
                        link_match = re.search(r'>(.*?)</a>', line, re.IGNORECASE | re.DOTALL)
                        if link_match:
                            link_text = link_match.group(1).strip().lower()
                            
                            if link_text in weak_link_texts:
                                self.issues.append(EditorIssue(
                                    severity="suggestion",
                                    category="link_quality",
                                    file=str(html_file.relative_to(self.base_path)),
                                    message=f"Generic link text: '{link_text}'",
                                    suggestion="Use descriptive link text that indicates where the link goes",
                                    line=i + 1
                                ))
                            
                            if not link_text:
                                self.issues.append(EditorIssue(
                                    severity="error",
                                    category="link_quality",
                                    file=str(html_file.relative_to(self.base_path)),
                                    message="Empty link found",
                                    suggestion="Add meaningful text to the link",
                                    line=i + 1
                                ))
                            
                            if 'title=' not in line.lower() and 'aria-label=' not in line.lower():
                                if len(link_text) < 5:
                                    self.issues.append(EditorIssue(
                                        severity="suggestion",
                                        category="link_quality",
                                        file=str(html_file.relative_to(self.base_path)),
                                        message="Short link text without title/aria-label",
                                        suggestion="Add title or aria-label for accessibility",
                                        line=i + 1
                                    ))
                            
            except Exception:
                pass
    
    def _check_seo_basics(self):
        """Check basic SEO elements."""
        title_pattern = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)
        meta_pattern = re.compile(r'<meta[^>]+>', re.IGNORECASE)
        desc_pattern = re.compile(r'name=["\']description["\']', re.IGNORECASE)
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                title_match = title_pattern.search(content)
                if not title_match:
                    self.issues.append(EditorIssue(
                        severity="error",
                        category="seo",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Missing <title> tag",
                        suggestion="Add a descriptive title tag for SEO"
                    ))
                else:
                    title_text = title_match.group(1).strip()
                    if len(title_text) < 30:
                        self.issues.append(EditorIssue(
                            severity="suggestion",
                            category="seo",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"Title too short ({len(title_text)} chars)",
                            suggestion="Aim for 50-60 characters for optimal SEO"
                        ))
                    elif len(title_text) > 70:
                        self.issues.append(EditorIssue(
                            severity="suggestion",
                            category="seo",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"Title too long ({len(title_text)} chars)",
                            suggestion="Keep title under 70 characters to avoid truncation"
                        ))
                
                meta_tags = meta_pattern.findall(content)
                has_description = any(desc_pattern.search(tag) for tag in meta_tags)
                
                if not has_description:
                    self.issues.append(EditorIssue(
                        severity="warning",
                        category="seo",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Missing meta description",
                        suggestion="Add a 150-160 character meta description for SEO"
                    ))
                        
            except Exception:
                pass
    
    def _check_typography(self):
        """Check basic typography issues."""
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for double spaces
                if '  ' in content:
                    count = content.count('  ')
                    self.issues.append(EditorIssue(
                        severity="suggestion",
                        category="typography",
                        file=str(html_file.relative_to(self.base_path)),
                        message=f"Found {count} double spaces",
                        suggestion="Use single spaces between words"
                    ))
                
                # Check for missing space after punctuation
                missing_space = re.findall(r'[.!?][A-Za-z]', content)
                if len(missing_space) > 3:
                    self.issues.append(EditorIssue(
                        severity="suggestion",
                        category="typography",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Possible missing space after punctuation",
                        suggestion="Add a space after periods, exclamation marks, and question marks"
                    ))
                
                # Check for straight quotes (should be curly)
                if '"' in content or "'" in content:
                    self.issues.append(EditorIssue(
                        severity="suggestion",
                        category="typography",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Straight quotes found - consider using curly quotes",
                        suggestion="Use smart/curly quotes for professional typography"
                    ))
                        
            except Exception:
                pass
    
    def _count_by_category(self) -> Dict[str, int]:
        """Count issues by category."""
        counts = {}
        for issue in self.issues:
            counts[issue.category] = counts.get(issue.category, 0) + 1
        return counts
    
    def _calculate_grade(self) -> str:
        """Calculate overall grade based on issues."""
        errors = len([i for i in self.issues if i.severity == 'error'])
        warnings = len([i for i in self.issues if i.severity == 'warning'])
        suggestions = len([i for i in self.issues if i.severity == 'suggestion'])
        
        score = 100 - (errors * 5) - (warnings * 2) - (suggestions * 0.5)
        score = max(0, min(100, score))
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def print_summary(self, report: EditorReport):
        """Print a human-readable summary to console."""
        print("\n" + "=" * 60)
        print("LANDING PAGE EDITOR REVIEW")
        print("=" * 60)
        print(f"[DIR] Base Path: {report.base_path}")
        print(f"[FILE] Files Analyzed: {report.total_files_analyzed}")
        print(f"[STAT] Total Issues: {report.total_issues}")
        print()
        
        # Grade and readability
        grade = report.summary.get('overall_grade', 'N/A')
        readability = report.readability_scores.get('average', 0)
        
        print(f"[SCORE] Overall Grade: {grade}")
        print(f"[READ] Avg Readability: {readability:.1f}/100")
        print()
        
        # Issue breakdown
        print("[E] Errors:   ", report.summary.get('total_errors', 0))
        print("[W] Warnings: ", report.summary.get('total_warnings', 0))
        print("[S] Suggestions:", report.summary.get('total_suggestions', 0))
        print()
        
        # Category breakdown
        if report.summary.get('category_counts'):
            print("[LIST] Category Breakdown:")
            for cat, count in report.summary['category_counts'].items():
                print(f"   - {cat.replace('_', ' ').title()}: {count}")
        print()
        
        # Top issues
        if report.issues:
            print("[TARGET] Top Issues (first 5):")
            for issue in report.issues[:5]:
                icon = "[E]" if issue['severity'] == 'error' else ("[W]" if issue['severity'] == 'warning' else "[S]")
                print(f"   {icon} [{issue['category']}] {issue['file']}")
                print(f"      {issue['message']}")
                if issue['suggestion']:
                    print(f"      -> {issue['suggestion']}")
        print()
        
        print("=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    if not os.path.isdir(base_path):
        print(f"[ERROR] Directory not found: {base_path}")
        sys.exit(1)
    
    # Run editor review
    editor = EditorReview(base_path)
    report = editor.run_all_checks()
    
    # Print summary
    editor.print_summary(report)
    
    # Save JSON report
    report_path = os.path.join(base_path, "editor-report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(report), f, indent=2, ensure_ascii=False)
    print(f"[REPORT] Detailed report saved to: {report_path}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
