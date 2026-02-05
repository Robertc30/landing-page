#!/usr/bin/env python3
"""
Landing Page QC Checker
Comprehensive quality control for landing page HTML files, images, and links.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys


@dataclass
class QCIssue:
    """Represents a single QC issue."""
    severity: str  # error, warning, info
    category: str  # broken_link, missing_image, etc.
    file: str
    message: str
    details: str = ""
    line: int = 0


@dataclass
class QCReport:
    """Complete QC report."""
    timestamp: str = ""
    base_path: str = ""
    total_files_scanned: int = 0
    total_issues: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0
    issues: List[Dict] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class QCChecker:
    """Main QC checker class."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.html_files: List[Path] = []
        self.image_files: Set[str] = set()
        self.all_files: Set[str] = set()
        self.issues: List[QCIssue] = []
        
    def run_all_checks(self) -> QCReport:
        """Run all QC checks and return a report."""
        report = QCReport(
            timestamp=datetime.now().isoformat(),
            base_path=str(self.base_path)
        )
        
        # Phase 1: Discovery
        self._discover_files()
        
        # Phase 2: Content checks
        self._check_broken_links()
        self._check_missing_images()
        self._check_orphaned_images()
        self._check_todo_markers()
        self._check_empty_files()
        self._check_html_structure()
        self._check_javascript_errors()
        
        # Build report
        report.total_files_scanned = len(self.html_files)
        report.issues = [asdict(issue) for issue in self.issues]
        
        for issue in self.issues:
            report.total_issues += 1
            if issue.severity == "error":
                report.errors += 1
            elif issue.severity == "warning":
                report.warnings += 1
            else:
                report.info += 1
        
        report.summary = {
            "passed": report.errors == 0,
            "score": max(0, 100 - (report.errors * 10) - (report.warnings * 2)),
            "check_counts": {
                "broken_links": len([i for i in self.issues if i.category == "broken_link"]),
                "missing_images": len([i for i in self.issues if i.category == "missing_image"]),
                "orphaned_images": len([i for i in self.issues if i.category == "orphaned_image"]),
                "todo_markers": len([i for i in self.issues if i.category == "todo_marker"]),
                "empty_files": len([i for i in self.issues if i.category == "empty_file"]),
                "html_structure": len([i for i in self.issues if i.category == "html_structure"]),
            }
        }
        
        return report
    
    def _discover_files(self):
        """Discover all HTML and image files."""
        for root, dirs, files in os.walk(self.base_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.html'):
                    path = Path(root) / file
                    self.html_files.append(path)
                    self.all_files.add(str(path.relative_to(self.base_path)))
                elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico')):
                    path = Path(root) / file
                    self.image_files.add(str(path.relative_to(self.base_path)))
    
    def _check_broken_links(self):
        """Check for broken internal links."""
        link_pattern = re.compile(r'href=["\']([^"\']+)["\']')
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                for match in link_pattern.finditer(content):
                    href = match.group(1)
                    
                    # Skip external links and special links
                    if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'javascript:')):
                        continue
                    
                    # Handle fragment-only links (same page anchors)
                    if href.startswith('#'):
                        anchor = href[1:]
                        if anchor:
                            # Check if anchor exists in the page
                            anchor_pattern = re.compile(r'id=["\']' + re.escape(anchor) + r'["\']|name=["\']' + re.escape(anchor) + r'["\']', re.IGNORECASE)
                            if not anchor_pattern.search(content):
                                self.issues.append(QCIssue(
                                    severity="error",
                                    category="broken_link",
                                    file=str(html_file.relative_to(self.base_path)),
                                    message=f"Broken anchor link: #{anchor}",
                                    details=f"Anchor '{anchor}' not found in the page",
                                    line=content[:match.start()].count('\n') + 1
                                ))
                        continue
                    
                    # Normalize the link relative to the source file's directory
                    link_path = href.lstrip('/')
                    
                    # Resolve relative to the source file's directory, not base_path
                    source_dir = html_file.parent
                    link_full = source_dir / link_path
                    link_full = link_full.resolve()
                    
                    # Normalize back to relative path from base_path for reporting
                    try:
                        rel_path = link_full.relative_to(self.base_path)
                        rel_path_str = str(rel_path)
                    except ValueError:
                        # Link points outside base_path - check if it exists
                        if not link_full.exists():
                            self.issues.append(QCIssue(
                                severity="error",
                                category="broken_link",
                                file=str(html_file.relative_to(self.base_path)),
                                message=f"Broken link: {href}",
                                details=f"Target file does not exist",
                                line=content[:match.start()].count('\n') + 1
                            ))
                        continue
                    
                    if not link_full.exists() and not link_full.is_dir():
                        # Maybe it's an index file?
                        if link_full.suffix == '' and not (link_full.parent / (link_full.name + ".html")).exists():
                            self.issues.append(QCIssue(
                                severity="error",
                                category="broken_link",
                                file=str(html_file.relative_to(self.base_path)),
                                message=f"Broken link: {href}",
                                details=f"Target file does not exist",
                                line=content[:match.start()].count('\n') + 1
                            ))
                            
            except Exception as e:
                self.issues.append(QCIssue(
                    severity="warning",
                    category="file_read",
                    file=str(html_file.relative_to(self.base_path)),
                    message=f"Could not read file: {e}"
                ))
    
    def _check_missing_images(self):
        """Check for missing or referenced but non-existent images."""
        img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                for match in img_pattern.finditer(content):
                    src = match.group(1)
                    
                    # Skip data URIs and external images
                    if src.startswith(('data:', 'http://', 'https://')):
                        continue
                    
                    # Normalize the image path relative to the source file's directory
                    img_path = src.lstrip('/')
                    source_dir = html_file.parent
                    img_full = source_dir / img_path
                    img_full = img_full.resolve()
                    
                    if not img_full.exists():
                        self.issues.append(QCIssue(
                            severity="error",
                            category="missing_image",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"Missing image: {src}",
                            details=f"Image file does not exist",
                            line=content[:match.start()].count('\n') + 1
                        ))
                    else:
                        # Check if file is empty
                        if img_full.stat().st_size == 0:
                            self.issues.append(QCIssue(
                                severity="error",
                                category="missing_image",
                                file=str(html_file.relative_to(self.base_path)),
                                message=f"Empty image file: {src}",
                                details=f"Image file exists but is empty (0 bytes)",
                                line=content[:match.start()].count('\n') + 1
                            ))
                            
            except Exception as e:
                self.issues.append(QCIssue(
                    severity="warning",
                    category="file_read",
                    file=str(html_file.relative_to(self.base_path)),
                    message=f"Could not read file: {e}"
                ))
    
    def _check_orphaned_images(self):
        """Check for image files not referenced in any HTML."""
        referenced_images = set()
        
        img_ref_pattern = re.compile(r'src=["\']([^"\']+)["\']', re.IGNORECASE)
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                for match in img_ref_pattern.finditer(content):
                    src = match.group(1)
                    
                    # Skip data URIs and external images
                    if src.startswith(('data:', 'http://', 'https://')):
                        continue
                    
                    # Normalize the image path
                    img_path = src.lstrip('/').lower()
                    referenced_images.add(img_path)
                    
                    # Also check for case-insensitive matches
                    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico']:
                        if img_path.endswith(ext):
                            base = img_path[:-len(ext)]
                            referenced_images.add(base + ext)
                            break
                            
            except Exception:
                pass
        
        # Find orphaned images
        for img in self.image_files:
            img_lower = img.lower()
            img_normalized = img_lower
            
            # Check if this image is referenced
            is_referenced = False
            for ref in referenced_images:
                if img_lower == ref.lower() or img_normalized == ref.lower():
                    is_referenced = True
                    break
            
            if not is_referenced:
                self.issues.append(QCIssue(
                    severity="info",
                    category="orphaned_image",
                    file="global",
                    message=f"Orphaned image: {img}",
                    details="Image file exists but is not referenced in any HTML file"
                ))
    
    def _check_todo_markers(self):
        """Check for TODO, FIXME, or other development markers."""
        todo_patterns = re.compile(
            r'(TODO|FIXME|HACK|XXX|BUG|REVIEW|CUSTOMIZE|PENDING|OPTIMIZE)\s*[:\-]?\s*(.*)',
            re.IGNORECASE
        )
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    match = todo_patterns.search(line)
                    if match:
                        self.issues.append(QCIssue(
                            severity="warning",
                            category="todo_marker",
                            file=str(html_file.relative_to(self.base_path)),
                            message=f"Development marker found: {match.group(1)}",
                            details=match.group(2).strip()[:200],
                            line=i + 1
                        ))
                        
            except Exception:
                pass
    
    def _check_empty_files(self):
        """Check for empty or nearly empty files."""
        min_content_size = 50  # Minimum meaningful content size
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                stripped = content.strip()
                
                if len(stripped) < min_content_size:
                    self.issues.append(QCIssue(
                        severity="warning",
                        category="empty_file",
                        file=str(html_file.relative_to(self.base_path)),
                        message=f"File appears to have minimal content ({len(stripped)} chars)",
                        details="File may be incomplete or placeholder"
                    ))
                    
            except Exception:
                pass
    
    def _check_html_structure(self):
        """Check for proper HTML structure."""
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for DOCTYPE
                if '<!DOCTYPE' not in content.upper() and '<!doctype' not in content.lower():
                    self.issues.append(QCIssue(
                        severity="warning",
                        category="html_structure",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Missing DOCTYPE declaration",
                        details="File should start with <!DOCTYPE html>"
                    ))
                
                # Check for html tag
                if '<html' not in content.lower():
                    self.issues.append(QCIssue(
                        severity="error",
                        category="html_structure",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Missing <html> tag"
                    ))
                
                # Check for head and body
                if '<head' not in content.lower():
                    self.issues.append(QCIssue(
                        severity="info",
                        category="html_structure",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Missing <head> section"
                    ))
                
                if '<body' not in content.lower():
                    self.issues.append(QCIssue(
                        severity="info",
                        category="html_structure",
                        file=str(html_file.relative_to(self.base_path)),
                        message="Missing <body> section"
                    ))
                    
            except Exception:
                pass
    
    def _check_javascript_errors(self):
        """Check for common JavaScript syntax issues."""
        script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                for match in script_pattern.finditer(content):
                    script_content = match.group(1)
                    
                    # Skip external scripts
                    if 'src=' in content[max(0, match.start()-100):match.start()]:
                        continue
                    
                    # Check for common issues
                    # Unclosed brackets (basic check)
                    open_braces = script_content.count('{')
                    close_braces = script_content.count('}')
                    if open_braces != close_braces:
                        self.issues.append(QCIssue(
                            severity="error",
                            category="javascript",
                            file=str(html_file.relative_to(self.base_path)),
                            message="Possible unclosed braces in JavaScript",
                            details=f"Open braces: {open_braces}, Close braces: {close_braces}"
                        ))
                    
                    open_parens = script_content.count('(')
                    close_parens = script_content.count(')')
                    if open_parens != close_parens:
                        self.issues.append(QCIssue(
                            severity="error",
                            category="javascript",
                            file=str(html_file.relative_to(self.base_path)),
                            message="Possible unclosed parentheses in JavaScript",
                            details=f"Open parens: {open_parens}, Close parens: {close_parens}"
                        ))
                        
            except Exception:
                pass
    
    def print_summary(self, report: QCReport):
        """Print a human-readable summary to console."""
        print("\n" + "=" * 60)
        print("LANDING PAGE QC REPORT")
        print("=" * 60)
        print(f"[DIR] Base Path: {report.base_path}")
        print(f"[FILE] Files Scanned: {report.total_files_scanned}")
        print(f"[STAT] Total Issues: {report.total_issues}")
        print()
        
        # Severity breakdown
        print("[E] Errors:   ", report.errors)
        print("[W] Warnings: ", report.warnings)
        print("[I] Info:     ", report.info)
        print()
        
        # Score
        score = report.summary.get("score", 0)
        passed = report.summary.get("passed", False)
        status = "[PASS]" if passed else "[FAIL]"
        print(f"[SCORE] QC Score: {score}/100 {status}")
        print()
        
        # Check counts
        if report.summary.get("check_counts"):
            print("[LIST] Check Details:")
            for check, count in report.summary["check_counts"].items():
                if count > 0:
                    icon = "[E]" if check in ["broken_links", "missing_images"] else "[W]"
                    print(f"   {icon} {check.replace('_', ' ').title()}: {count}")
        print()
        
        # Recent issues
        if report.issues:
            print("[NOTE] Sample Issues (first 5):")
            for issue in report.issues[:5]:
                icon = "[E]" if issue["severity"] == "error" else ("[W]" if issue["severity"] == "warning" else "[I]")
                print(f"   {icon} [{issue['category']}] {issue['file']}:{issue['line'] or '?'} - {issue['message']}")
        print()
        
        print("=" * 60)


def main():
    """Main entry point."""
    # Default to current directory or use command line argument
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    if not os.path.isdir(base_path):
        print(f"[ERROR] Directory not found: {base_path}")
        sys.exit(1)
    
    # Run QC
    checker = QCChecker(base_path)
    report = checker.run_all_checks()
    
    # Print summary
    checker.print_summary(report)
    
    # Save JSON report
    report_path = os.path.join(base_path, "qc-report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(report), f, indent=2, ensure_ascii=False)
    print(f"[REPORT] Detailed report saved to: {report_path}")
    
    # Exit with appropriate code
    sys.exit(0 if report.errors == 0 else 1)


if __name__ == "__main__":
    main()
