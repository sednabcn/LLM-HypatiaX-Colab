# Adding HypatiaX Tutorials to Your Jekyll Blog

## 📁 Files Created

I've created these files for you:
1. `hypatiax-index.md` - Main tutorial series landing page
2. `hypatiax-tutorial-1.md` - Tutorial 1: Setup (template)

You also have these complete tutorials from earlier:
3. `2026-02-20-hypatiax-tutorial-1-setup.md`
4. `2026-02-21-hypatiax-tutorial-2-experiments.md`
5. `2026-02-22-hypatiax-tutorial-3-analysis.md`
6. `2026-02-23-hypatiax-tutorial-4-extensions.md`

---

## 🚀 Quick Integration Steps

### Option 1: Add as Tutorial Section (Recommended)

```bash
# Navigate to your blog directory
cd ~/Downloads/GITHUB/ai-llm-blog

# Create HypatiaX tutorial directory
mkdir -p _tutorials/hypatiax

# Copy the index file
cp /path/to/hypatiax-index.md _tutorials/hypatiax/index.md

# Copy individual tutorials
cp /path/to/2026-02-20-hypatiax-tutorial-1-setup.md _tutorials/hypatiax/setup.md
cp /path/to/2026-02-21-hypatiax-tutorial-2-experiments.md _tutorials/hypatiax/experiments.md
cp /path/to/2026-02-22-hypatiax-tutorial-3-analysis.md _tutorials/hypatiax/analysis.md
cp /path/to/2026-02-23-hypatiax-tutorial-4-extensions.md _tutorials/hypatiax/extensions.md
```

**Result:**
```
_tutorials/
├── hypatiax/
│   ├── index.md
│   ├── setup.md
│   ├── experiments.md
│   ├── analysis.md
│   └── extensions.md
├── advanced-features/
├── basic-customization/
└── ...
```

---

### Option 2: Add as Blog Posts

```bash
# Copy tutorials as blog posts (keep dates for ordering)
cp /path/to/2026-02-20-hypatiax-tutorial-1-setup.md _posts/
cp /path/to/2026-02-21-hypatiax-tutorial-2-experiments.md _posts/
cp /path/to/2026-02-22-hypatiax-tutorial-3-analysis.md _posts/
cp /path/to/2026-02-23-hypatiax-tutorial-4-extensions.md _posts/
```

---

## 📝 Format Adjustments Needed

The tutorial files I created use Jekyll blog post format. You need to adjust front matter for your tutorial structure.

### Current Blog Post Format (from tutorials):
```yaml
---
layout: post
title: "HypatiaX Tutorial 1: Environment Setup"
date: 2026-02-20
categories: [machine-learning, tutorials, symbolic-regression]
tags: [hypatiax, llm, symbolic-discovery, python]
author: HypatiaX Team
---
```

### Convert to Tutorial Page Format:
```yaml
---
layout: single
title: "Tutorial 1: Environment Setup"
permalink: /tutorials/hypatiax/setup/
sidebar:
  nav: "tutorials"
toc: true
toc_label: "Contents"
toc_icon: "cog"
header:
  overlay_image: /assets/images/tutorials/hypatiax-setup-banner.webp
  overlay_filter: 0.5
---
```

---

## 🎨 Add Banner Images (Optional)

Your blog uses banner images in `/assets/images/tutorials/`. Create banners:

```bash
cd ~/Downloads/GITHUB/ai-llm-blog/assets/images/tutorials

# You need these banners:
# - hypatiax-banner.webp (series landing page)
# - hypatiax-setup-banner.webp (Tutorial 1)
# - hypatiax-experiments-banner.webp (Tutorial 2)
# - hypatiax-analysis-banner.webp (Tutorial 3)
# - hypatiax-extensions-banner.webp (Tutorial 4)
```

**Option A:** Create custom banners (Canva, Figma, etc.)  
**Option B:** Use existing tutorial-banner.png as template  
**Option C:** Remove `header:` section from front matter (no banners)

---

## 🔗 Update Navigation (Optional)

If you want HypatiaX in your sidebar navigation:

Edit `_data/navigation.yml`:

```yaml
tutorials:
  - title: "Getting Started"
    children:
      - title: "Setup"
        url: /tutorials/setup/
      - title: "Python Setup"
        url: /tutorials/setup/python-setup/
  
  - title: "HypatiaX" # Add this section
    children:
      - title: "Overview"
        url: /tutorials/hypatiax/
      - title: "1. Setup"
        url: /tutorials/hypatiax/setup/
      - title: "2. Experiments"
        url: /tutorials/hypatiax/experiments/
      - title: "3. Analysis"
        url: /tutorials/hypatiax/analysis/
      - title: "4. Extensions"
        url: /tutorials/hypatiax/extensions/
  
  - title: "Advanced Features"
    children:
      - title: "Overview"
        url: /tutorials/advanced-features/
```

---

## 🧪 Test Locally

```bash
cd ~/Downloads/GITHUB/ai-llm-blog

# Install Jekyll if not already installed
bundle install

# Run local server
bundle exec jekyll serve

# Open in browser
firefox http://localhost:4000/tutorials/hypatiax/
```

---

## 📋 Checklist

- [ ] Create `_tutorials/hypatiax/` directory
- [ ] Copy all 5 tutorial files
- [ ] Update front matter (layout, permalink, etc.)
- [ ] Create/add banner images (or remove header sections)
- [ ] Update `_data/navigation.yml` (optional)
- [ ] Test locally with `jekyll serve`
- [ ] Commit and push to GitHub
- [ ] Verify on live site

---

## 🎯 Quick Command Summary

Here's everything in one script:

```bash
#!/bin/bash
# Run from your blog root directory

# Create directory
mkdir -p _tutorials/hypatiax

# Copy files (adjust paths to where you downloaded them)
TUTORIAL_DIR="/path/to/downloaded/tutorials"

cp "$TUTORIAL_DIR/hypatiax-index.md" _tutorials/hypatiax/index.md
cp "$TUTORIAL_DIR/2026-02-20-hypatiax-tutorial-1-setup.md" _tutorials/hypatiax/setup.md
cp "$TUTORIAL_DIR/2026-02-21-hypatiax-tutorial-2-experiments.md" _tutorials/hypatiax/experiments.md
cp "$TUTORIAL_DIR/2026-02-22-hypatiax-tutorial-3-analysis.md" _tutorials/hypatiax/analysis.md
cp "$TUTORIAL_DIR/2026-02-23-hypatiax-tutorial-4-extensions.md" _tutorials/hypatiax/extensions.md

echo "✅ Files copied!"
echo "⚠️  Don't forget to update front matter!"
echo "🎨 Optional: Add banner images to assets/images/tutorials/"
echo "🧪 Test with: bundle exec jekyll serve"
```

---

## 🔄 Alternative: Keep as Blog Posts

If you prefer tutorials as blog posts instead of separate section:

```bash
# Just copy to _posts/
cp 2026-02-20-hypatiax-tutorial-1-setup.md _posts/
cp 2026-02-21-hypatiax-tutorial-2-experiments.md _posts/
cp 2026-02-22-hypatiax-tutorial-3-analysis.md _posts/
cp 2026-02-23-hypatiax-tutorial-4-extensions.md _posts/

# They'll show up in your blog chronologically
# No structure changes needed!
```

---

## 💡 Which Option Should You Choose?

### **Tutorial Section (Option 1) - Recommended if:**
- ✅ You want organized, structured learning path
- ✅ You want sidebar navigation between tutorials
- ✅ You want persistent tutorial presence (not buried in blog archives)

### **Blog Posts (Option 2) - Recommended if:**
- ✅ You want simpler integration (no structure changes)
- ✅ You want tutorials to appear in blog feed
- ✅ You want date-based organization

---

## 🆘 Need Help?

If you get stuck:

1. **Front matter issues:** Compare with existing tutorials in `_tutorials/`
2. **Permalinks broken:** Check `_config.yml` for permalink settings
3. **Images not showing:** Verify paths in `assets/images/tutorials/`
4. **Navigation not working:** Check `_data/navigation.yml` syntax

---

## 📚 Next Steps After Integration

1. **Test all links** - Click through all 4 tutorials
2. **Check formatting** - Code blocks, images, tables
3. **Verify navigation** - Sidebar, breadcrumbs, next/prev links
4. **Mobile test** - Check responsive design
5. **Deploy** - Push to GitHub Pages or your hosting

---

**Ready to integrate?** Choose your option and run the commands! 🚀
