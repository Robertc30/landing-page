#!/usr/bin/env python3
"""
Landing Page Automated QC + Editor Review Runner
Runs both QC check and editor review, then reports results.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_command(cmd: list, description: str) -> tuple:
    """Run a command and return success status and output."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out!")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False, str(e)


def main():
    """Main entry point."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\n🚀 Starting Automated Landing Page Review")
    print(f"📁 Working Directory: {base_path}")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_path": base_path,
        "qc_check": {"passed": False, "issues": 0, "errors": 0, "warnings": 0},
        "editor_review": {"passed": False, "issues": 0, "grade": "N/A", "readability": 0},
        "overall_status": "unknown"
    }
    
    # Run QC Check
    qc_script = os.path.join(base_path, "qc-check.py")
    if os.path.exists(qc_script):
        success, output = run_command([sys.executable, qc_script, base_path], "Quality Control Check")
        results["qc_check"]["passed"] = success
        
        # Parse QC report for stats
        qc_report_path = os.path.join(base_path, "qc-report.json")
        if os.path.exists(qc_report_path):
            with open(qc_report_path) as f:
                qc_report = json.load(f)
            results["qc_check"]["issues"] = qc_report.get("total_issues", 0)
            results["qc_check"]["errors"] = qc_report.get("errors", 0)
            results["qc_check"]["warnings"] = qc_report.get("warnings", 0)
    else:
        print(f"❌ QC script not found: {qc_script}")
    
    # Run Editor Review
    editor_script = os.path.join(base_path, "editor-review.py")
    if os.path.exists(editor_script):
        success, output = run_command([sys.executable, editor_script, base_path], "Editor Review")
        results["editor_review"]["passed"] = success
        
        # Parse Editor report for stats
        editor_report_path = os.path.join(base_path, "editor-report.json")
        if os.path.exists(editor_report_path):
            with open(editor_report_path) as f:
                editor_report = json.load(f)
            results["editor_review"]["issues"] = editor_report.get("total_issues", 0)
            results["editor_review"]["grade"] = editor_report.get("summary", {}).get("overall_grade", "N/A")
            results["editor_review"]["readability"] = editor_report.get("readability_scores", {}).get("average", 0)
    else:
        print(f"❌ Editor script not found: {editor_script}")
    
    # Determine overall status
    all_passed = results["qc_check"]["passed"] and results["editor_review"]["passed"]
    has_major_errors = results["qc_check"]["errors"] > 0
    
    if all_passed and not has_major_errors:
        results["overall_status"] = "healthy"
    elif has_major_errors:
        results["overall_status"] = "critical"
    else:
        results["overall_status"] = "needs_attention"
    
    # Final Summary
    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*60}")
    
    status_icon = {
        "healthy": "✅",
        "critical": "🔴",
        "needs_attention": "⚠️"
    }.get(results["overall_status"], "❓")
    
    print(f"{status_icon} Overall Status: {results['overall_status'].upper()}")
    print()
    
    print("QC Check:")
    print(f"   Passed: {results['qc_check']['passed']}")
    print(f"   Issues: {results['qc_check']['issues']} ({results['qc_check']['errors']} errors, {results['qc_check']['warnings']} warnings)")
    print()
    
    print("Editor Review:")
    print(f"   Passed: {results['editor_review']['passed']}")
    print(f"   Issues: {results['editor_review']['issues']}")
    print(f"   Grade: {results['editor_review']['grade']}")
    print(f"   Readability: {results['editor_review']['readability']:.1f}/100")
    print()
    
    # Save combined report
    combined_report_path = os.path.join(base_path, "combined-review-report.json")
    with open(combined_report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Combined report saved to: {combined_report_path}")
    
    print(f"\n{'='*60}")
    
    # Exit with appropriate code
    if results["overall_status"] == "critical":
        sys.exit(2)  # Critical errors
    elif results["overall_status"] == "needs_attention":
        sys.exit(1)  # Warnings
    else:
        sys.exit(0)  # All good


if __name__ == "__main__":
    main()
