# Site Cleanup Todo List

## High Priority (SEO & Accessibility)

### Missing Meta Descriptions (8 pages need this)
- [x] `reviews/ffmpeg.html` - Add meta description
- [x] `reviews/gemini.html` - Add meta description  
- [x] `reviews/google-colab.html` - Add meta description
- [x] `reviews/index.html` - Add meta description
- [x] `reviews/itemfits.html` - Add meta description
- [x] `reviews/minimax.html` - Add meta description
- [x] `reviews/notebooklm.html` - Add meta description
- [x] `reviews/openai-whisper.html` - Add meta description
- [x] `reviews/openclaw.html` - Add meta description

### Image Accessibility (24 images)
- [x] `blog/2026-02-02-openclaw-setup.html` - Add title/width/height to images (lines 41, 111)
- [x] `blog/2026-02-03-landing-page-updates.html` - Add title/width/height to images (lines 45, 87, 96-98)
- [x] `blog/2026-02-04-rolling-day-three.html` - Add title/width/height to image (line 42)
- [x] `blog/index.html` - Add title/width/height to image (line 41)
- [x] `blog/openclaw-anti-gravity-walkthrough.html` - Add title/width/height to image (line 57)
- [x] `reviews/itemfits.html` - Add title/width/height to image (line 47)
- [x] `reviews/minimax.html` - Add title/width/height to image (line 60)

## Medium Priority (Typography & Links)

### Typography Issues (57 files)
- [ ] Fix double spaces in all HTML files
- [ ] Fix straight quotes → curly quotes
- [ ] Fix missing spaces after punctuation

### Link Quality (36 links need aria-labels)
- [ ] Add aria-labels to short link texts in navigation

## Low Priority (Suggestions)

### SEO Titles (short titles)
- [ ] `tools.html` - Expand title (27 chars → 50-60)
- [ ] `blog/index.html` - Expand title (19 chars → 50-60)
- [ ] `blog/walkthroughs.html` - Expand title (27 chars → 50-60)
- [ ] `reviews/ffmpeg.html` - Expand title (28 chars → 50-60)
- [ ] `reviews/gemini.html` - Expand title (28 chars → 50-60)
- [ ] `reviews/index.html` - Expand title (22 chars → 50-60)
- [ ] `reviews/minimax.html` - Expand title (29 chars → 50-60)

### Vague Language (17 instances)
- [ ] Replace "good", "things", "interesting", "nice", "really", etc.

### Readability
- [ ] `blog/index.html` - Break up long paragraphs (50% long)
- [ ] `reviews/notebooklm.html` - Break up long sentences (38%)

## QC Markers (102 instances - mostly legitimate)
The TODO/REVIEW/BUG markers flagged by QC are mostly legitimate navigation links and development notes. Review individually:
- [ ] `index.html` - Lines 54, 117, 139, 142, 149, 156, 163
- [ ] `tools.html` - Lines 27, 53, 71, 81, 84, 89, 92, 97, 100, 105, 108, 127, 135, 143
- [ ] Blog posts - Various lines
- [ ] Reviews pages - Various lines

## Completed
- [x] Delete obsolete `TechQuestv1.png` logo
- [x] Document orphaned image decisions
