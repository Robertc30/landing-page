# Landing Page

A simple, professional landing page deployed to GitHub Pages.

## Quick Start

### Option 1: Manual GitHub Setup (Recommended)

If you already have a GitHub account with a personal access token:

```bash
# Set your GitHub username
git config user.name "YourGitHubUsername"

# Create the repository on GitHub and add remote
gh repo create landing-page --public --description "A professional landing page deployed to GitHub Pages"

# Add remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/landing-page.git

# Push to GitHub
git push -u origin main

# Enable GitHub Pages:
# 1. Go to https://github.com/YOUR_USERNAME/landing-page/settings/pages
# 2. Under "Build and deployment", select "main" as the branch
# 3. Click Save
# 4. Your site will be live at: https://YOUR_USERNAME.github.io/landing-page/
```

### Option 2: Manual Repository Creation

1. Go to https://github.com/new
2. Repository name: `landing-page`
3. Description: "A professional landing page deployed to GitHub Pages"
4. Set as Public
5. Do NOT initialize with README (we already have one)
6. Click "Create repository"
7. Run these commands:

```bash
cd "C:\Users\newta\.openclaw\workspace\landing-page"
git remote add origin https://github.com/YOUR_USERNAME/landing-page.git
git push -u origin main
```

Then enable GitHub Pages:
- Go to https://github.com/YOUR_USERNAME/landing-page/settings/pages
- Source: Select "main"
- Your site will be live at: `https://YOUR_USERNAME.github.io/landing-page/`

## Customization

Edit `index.html` to customize:

- **Logo**: Find `YourLogo` and replace with your brand name
- **Hero Section**: Update the `<h1>` headline and `<p>` description
- **CTA Button**: Change the button text and link
- **Features**: Edit the `.feature-card` sections
- **About Section**: Update the text and image placeholder
- **Footer**: Modify links and company info
- **Colors**: Edit CSS variables and color codes in the `<style>` section

## Files

- `index.html` - Complete landing page with embedded CSS

## Tech Stack

- Pure HTML5 + CSS3
- No external dependencies
- Fully responsive design
- Mobile-friendly

## License

MIT License
