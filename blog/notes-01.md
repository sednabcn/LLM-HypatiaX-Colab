📁 Your Blog Structure
I can see you have:
ai-llm-blog/
├── _posts/           # Blog posts
├── _tutorials/       # Tutorial sections
└── assets/
    └── images/
        └── tutorials/ # Tutorial banners
Let me create a new tutorial section for HypatiaX!

🎯 Plan: Add HypatiaX Tutorials to Your Blog
I'll create:

New tutorial category: hypatiax/
4 tutorial pages (one for each tutorial)
Index page for the HypatiaX series
Banner images (optional)

Created 2 filesCreate HypatiaX tutorials index pagehypatiax-index.mdCreate setup tutorial page for Jekyll bloghypatiax-tutorial-1.mdDoneNow let me create a simple guide for you to integrate these into your blog:Created a file, read a fileCreate integration guide for adding tutorials to Jekyll blogINTEGRATION_GUIDE.mdPresented 3 filesDonePerfect! 🎉 I've created everything you need to add the HypatiaX tutorials to your Jekyll blog!

📦 What I've Created for You
1. Tutorial Series Landing Page (hypatiax-index.md)

Overview of all 4 tutorials
Learning path and prerequisites
Quick start guide
Links to all tutorials

2. Template Tutorial Page (hypatiax-tutorial-1.md)

Shows the Jekyll format needed
Proper front matter for your blog
Sidebar navigation setup

3. Complete Integration Guide (INTEGRATION_GUIDE.md)

Step-by-step instructions
Two integration options (tutorial section vs blog posts)
Banner image setup
Navigation configuration
Testing checklist


🚀 Quick Start Integration
From your blog directory:
bashcd ~/Downloads/GITHUB/ai-llm-blog

# Create tutorial directory
mkdir -p _tutorials/hypatiax

# Copy the 4 complete tutorials you already have
# (The ones I created earlier: 2026-02-20, 2026-02-21, etc.)
# Adjust file paths to where you downloaded them

✅ You Now Have Everything
Complete tutorial files (from earlier):

✅ Tutorial 1: Setup (complete content)
✅ Tutorial 2: Experiments (complete content)
✅ Tutorial 3: Analysis (complete content)
✅ Tutorial 4: Extensions (complete content)

New Jekyll-specific files:

✅ Series index page
✅ Format template
✅ Complete integration guide


🎯 Next Steps

Read the INTEGRATION_GUIDE.md - It has all the commands
Choose your option:

Option 1: Add as tutorial section (more organized)
Option 2: Add as blog posts (simpler)


Copy the files using the commands in the guide
Test locally with bundle exec jekyll serve
Deploy!


💡 Two Simple Options
Option A: Tutorial Section (Organized)
bashmkdir -p _tutorials/hypatiax
# Copy all 5 files there
# Update navigation
# Best for: Structured learning paths
Option B: Blog Posts (Simple)
bash# Just copy to _posts/
cp 2026-02-*.md _posts/
# Done! They appear in blog feed
# Best for: Quick integration

The INTEGRATION_GUIDE.md has complete step-by-step instructions! Everything is ready for you to integrate into your blog. 🚀
Need help with any specific part of the integration?

=======================================================================

📘 Tutorial Series Index

/tutorials/hypatiax/

---
layout: single
title: "HypatiaX Tutorial Series"
permalink: /tutorials/hypatiax/
sidebar:
  nav: "tutorials"
toc: true
toc_label: "Tutorial Series"
toc_icon: "flask"
header:
  overlay_image: /assets/images/tutorials/hypatiax-banner.webp
  overlay_filter: 0.5
  caption: "LLM-Guided Symbolic Discovery"
---


✅ Uses the main HypatiaX banner
✅ Semi-transparent overlay (0.5)
✅ TOC enabled with custom label + icon

🧪 Tutorial 1 – Environment Setup

/tutorials/hypatiax/setup/

---
layout: single
title: "Tutorial 1: Environment Setup and First Discovery"
permalink: /tutorials/hypatiax/setup/
sidebar:
  nav: "tutorials"
toc: true
toc_label: "Contents"
toc_icon: "cog"
header:
  overlay_image: /assets/images/tutorials/hypatiax-setup-banner.webp
  overlay_filter: 0.5
  caption: "Install and discover your first equation"
---


✅ Uses the setup-specific banner
✅ Same overlay strength for visual consistency
✅ Clear TOC for step-by-step tutorial flow

🔧 What I fixed vs your pasted text

Removed duplicate layout, title, header blocks

Normalized YAML indentation (critical for Jekyll)

Ensured overlay applies correctly to both tutorials

Separated series index vs individual tutorial

Kept everything compatible with Minimal Mistakes

If you want next:

📐 a shared include so all tutorials inherit the same header style

🎨 advice on contrast / readability for the overlay images

🧭 automatic “Next / Previous tutorial” navigation

Just say the word.

---
layout: single
title: "HypatiaX Tutorial Series"
permalink: /tutorials/hypatiax/
sidebar:
  nav: "tutorials"
toc: true
toc_label: "Tutorial Series"
toc_icon: "flask"
header:
  overlay_image: /assets/images/tutorials/hypatiax-banner.webp
  overlay_filter: 0.5
---
