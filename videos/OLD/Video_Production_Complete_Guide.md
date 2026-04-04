# HypatiaX Video Production: Complete How-To Guide

## 🎬 Overview

This guide walks you through the **complete workflow** to record, edit, and publish your HypatiaX video tutorials using professional tools.

**Total Time Investment:**
- Setup: 2-3 hours (one time)
- Recording per tutorial: 30-60 minutes
- Editing per tutorial: 1-2 hours
- **Total for all 4 tutorials: ~15-20 hours**

---

## 📋 Required Tools

### 1. **Screen Recording: OBS Studio** (FREE)

**Why OBS Studio:**
- ✅ Professional-grade, industry standard
- ✅ Free and open-source
- ✅ Multi-platform (Windows, Mac, Linux)
- ✅ Supports 1080p/4K recording at 60fps
- ✅ Advanced scene management
- ✅ Built-in audio mixing

**Download:** https://obsproject.com/

**Installation:**
```bash
# Ubuntu/Debian
sudo apt install obs-studio

# macOS (with Homebrew)
brew install --cask obs

# Windows
# Download installer from obsproject.com
```

### 2. **Video Editing: DaVinci Resolve** (FREE)

**Why DaVinci Resolve:**
- ✅ Professional features in free version
- ✅ Better than iMovie/Windows Movie Maker
- ✅ Industry-standard color grading
- ✅ Built-in caption support
- ✅ Multi-platform

**Download:** https://www.blackmagicdesign.com/products/davinciresolve

**Alternatives:**
- **Shotcut** (simpler, also free): https://shotcut.org/
- **Kdenlive** (Linux): https://kdenlive.org/
- **Adobe Premiere Pro** (paid, $20/month student pricing)

### 3. **Audio Recording: Microphone**

**Recommended Options:**

| Budget | Microphone | Price | Quality |
|--------|------------|-------|---------|
| Budget | Blue Snowball | $50 | Good |
| Mid-range | Blue Yeti | $130 | Excellent |
| Pro | Audio-Technica AT2020USB+ | $150 | Professional |
| Phone | Headphone mic + Audacity | Free | Acceptable |

**Don't have a mic?** Use your phone's voice recorder and sync later!

### 4. **Supporting Tools**

```bash
# Terminal font increase
# Ubuntu: Preferences → Font size 16-18
# macOS: CMD+Plus to zoom
# Windows: Properties → Font → Size 18

# Code highlighting (for snippets)
sudo apt install highlight  # or use VS Code

# Image editing (for thumbnails)
sudo apt install gimp      # Free Photoshop alternative

# PDF creation (for cheat sheets)
sudo apt install pandoc
```

---

## 🎯 Step-by-Step Workflow

### **Phase 1: Setup (2-3 hours, one time)**

#### Step 1.1: Install OBS Studio

```bash
# Install OBS
sudo apt install obs-studio  # Ubuntu
# or download from obsproject.com

# Launch OBS
obs
```

#### Step 1.2: Configure OBS Settings

**Settings → Output:**
```
Output Mode: Advanced
Recording Format: mkv (change to mp4 later)
Encoder: x264
Rate Control: CRF
CRF: 18 (higher quality)
Keyframe Interval: 2
CPU Preset: veryfast
```

**Settings → Video:**
```
Base Resolution: 1920x1080
Output Resolution: 1920x1080
FPS: 60 (or 30 for slower machines)
```

**Settings → Audio:**
```
Sample Rate: 48kHz
Channels: Stereo
Desktop Audio: Default
Mic/Auxiliary Audio: Your microphone
```

#### Step 1.3: Create OBS Scenes

**Scene 1: "Terminal Full"**
- Source: Window Capture → Terminal
- Size: Full screen
- Add filter: Color Correction → Brightness +10%

**Scene 2: "Terminal + Webcam"** (optional)
- Source 1: Window Capture → Terminal (80% width)
- Source 2: Video Capture Device → Webcam (20% width, bottom right)
- Border: Add drop shadow

**Scene 3: "Code Editor"**
- Source: Window Capture → VS Code
- Size: Full screen

**Scene 4: "Browser"** (for showing GitHub, docs)
- Source: Window Capture → Browser
- Size: Full screen

#### Step 1.4: Set Up Hotkeys

```
Settings → Hotkeys:
Start Recording: F9
Stop Recording: F10
Switch Scene: F1, F2, F3, F4
Mute/Unmute Mic: F6
```

#### Step 1.5: Audio Test

```bash
# Record 10-second test
# Speak: "Testing, testing, one two three"
# Play back
# Adjust mic gain until levels hit -12dB to -6dB (yellow zone)
```

---

### **Phase 2: Pre-Production (30 min per tutorial)**

#### Step 2.1: Prepare Clean Environment

```bash
# Option A: Docker (recommended)
docker run -it --name hypatiax-demo ubuntu:22.04 /bin/bash
# Then install everything fresh

# Option B: Virtual Machine
# Create Ubuntu 22.04 VM in VirtualBox
# Allocate 4GB RAM, 50GB disk

# Option C: Fresh Directory
mkdir ~/hypatiax-demo
cd ~/hypatiax-demo
# Delete ~/.cache, ~/.config/hypatiax if exists
```

#### Step 2.2: Test All Commands

```bash
# Open video_tutorial_guide.md
# Copy every command from Tutorial 1
# Run each one
# Note down exact outputs
# Fix any errors NOW, not during recording
```

**Critical:** Don't record until EVERY command works!

#### Step 2.3: Prepare Visual Assets

```bash
# Create title slide
# Use Google Slides or PowerPoint:
# - Title: "HypatiaX Tutorial 1: Setup"
# - Subtitle: "LLMs as Interfaces to Symbolic Discovery"
# - Duration: 10 minutes
# Export as PNG (1920x1080)

# Save to: ~/hypatiax-demo/assets/title_tutorial1.png
```

#### Step 2.4: Print Script

```bash
# Print video_tutorial_guide.md Tutorial 1 section
# Or open on second monitor/tablet
# Highlight key talking points
```

---

### **Phase 3: Recording (30-60 min per tutorial)**

#### Step 3.1: Pre-Flight Checklist

```
□ OBS scenes configured
□ Microphone tested, levels good
□ Terminal font size 16+
□ Terminal clear (run 'clear')
□ Environment clean (no old files)
□ Script printed or on second monitor
□ Water nearby (stay hydrated!)
□ Phone on silent
□ Close Slack, email, notifications
```

#### Step 3.2: Recording Workflow

**1. Start with Title Screen**
```bash
# Display title slide in full screen
# Press F9 to start recording
# Hold for 3 seconds
# Start speaking: "Welcome to HypatiaX..."
```

**2. Switch to Terminal**
```bash
# Press F1 to switch to Terminal scene
# Wait 1 second
# Start typing/speaking
```

**3. Follow the Script**
```bash
# Video Tutorial Guide Tutorial 1, Segment 1
# Speak naturally, don't rush
# After each command:
#   - Type it
#   - Press Enter
#   - Wait 2 seconds
#   - Describe what's happening
#   - Show output
```

**4. Handle Mistakes**
```bash
# If you make a mistake:
#   - KEEP RECORDING
#   - Pause for 3 seconds
#   - Clap once (makes editing easier)
#   - Start the sentence again

# Don't worry about perfection!
# You'll edit out mistakes later
```

**5. End Recording**
```bash
# After final command/output
# Speak: "Thanks for watching! See you in Tutorial 2."
# Pause 2 seconds
# Press F10 to stop
```

#### Step 3.3: Save Recording

```bash
# OBS saves to: ~/Videos/ (default)
# File: YYYY-MM-DD_HH-MM-SS.mkv

# Immediately rename:
mv ~/Videos/2024-01-15_10-30-45.mkv \
   ~/Videos/Tutorial1_Raw_Take1.mkv

# If you need to re-record:
# Tutorial1_Raw_Take2.mkv, etc.
```

---

### **Phase 4: Editing (1-2 hours per tutorial)**

#### Step 4.1: Import to DaVinci Resolve

```bash
# Launch DaVinci Resolve
# Create New Project: "HypatiaX Tutorial 1"
# File → Import Media → Select Tutorial1_Raw_Take1.mkv
# Drag to timeline
```

#### Step 4.2: Cut Dead Air & Mistakes

```bash
# Scrub through timeline
# Find sections with:
#   - Long pauses (>5 seconds)
#   - Mistakes followed by 3-second pause + clap
#   - Installation waits (>30 seconds)

# Cut these out:
#   - Select region with 'I' and 'O' keys
#   - Delete with 'Backspace'
#   - Or right-click → Ripple Delete
```

#### Step 4.3: Speed Up Long Operations

```bash
# Find sections like:
#   - "pip install" (30-60 seconds)
#   - "PySR compilation" (5-10 minutes)

# Speed them up:
#   - Select section
#   - Right-click → Retime → 400% speed
#   - Add text overlay: "⏩ Sped up 4x for video"
```

#### Step 4.4: Add Chapter Markers

```bash
# Add markers at major segments:
# 0:00 - Introduction
# 1:15 - Repository Clone
# 3:30 - Dependency Installation
# 6:00 - Verification
# 9:15 - Conclusion

# Markers → Add Marker (M key)
# Name each marker
```

#### Step 4.5: Color Correction (Optional)

```bash
# If terminal looks washed out:
# Select clip
# Color tab
# Lift (shadows): +5
# Gamma (midtones): +10
# Gain (highlights): -5
```

#### Step 4.6: Export Video

```bash
# Deliver tab
# Format: MP4
# Codec: H.264
# Resolution: 1920x1080
# Frame Rate: 60fps (or match source)
# Quality: High (bitrate ~8000 kbps)

# Filename: HypatiaX_Tutorial1_Setup.mp4
# Location: ~/Videos/Final/

# Click "Add to Render Queue"
# Click "Render All"
# Wait 5-15 minutes
```

---

### **Phase 5: Captions (30 min per tutorial)**

#### Step 5.1: Auto-Generate Captions

**Option A: YouTube Auto-Captions** (Easiest)
```bash
# Upload to YouTube (see Phase 6)
# YouTube generates captions automatically
# Then edit them (see Step 5.2)
```

**Option B: Locally with Whisper** (Better accuracy)
```bash
# Install OpenAI Whisper
pip install openai-whisper

# Generate captions
whisper HypatiaX_Tutorial1_Setup.mp4 \
    --model medium \
    --language English \
    --output_format srt

# Creates: HypatiaX_Tutorial1_Setup.srt
```

#### Step 5.2: Edit Captions

```bash
# Open .srt file in text editor
# Fix common errors:
#   "high patia X" → "HypatiaX"
#   "pi S R" → "PySR"
#   "RMSE" → "R-M-S-E" (spell out acronyms)
#   "R squared" → "R²"

# Example SRT format:
# 1
# 00:00:00,000 --> 00:00:03,500
# Welcome to HypatiaX, a hybrid framework
# 
# 2
# 00:00:03,500 --> 00:00:06,800
# combining LLMs with symbolic regression.
```

---

### **Phase 6: Thumbnail Creation (15 min per tutorial)**

#### Step 6.1: Design Thumbnail in GIMP

```bash
# Launch GIMP
gimp

# Create new image: 1920x1080
# Background: Dark blue gradient

# Add layers:
# 1. Screenshot of terminal (from video at interesting moment)
# 2. Text: "HypatiaX Tutorial 1"
# 3. Subtitle: "Setup & Installation"
# 4. Duration badge: "10 MIN"

# Export as PNG:
# File → Export As → HypatiaX_Tutorial1_Thumbnail.png
```

**Template Tips:**
- **Font:** Bold, sans-serif (Arial, Helvetica)
- **Size:** Title 72pt, Subtitle 48pt
- **Colors:** High contrast (white text on dark background)
- **Rule of thirds:** Place key elements on grid lines
- **Face:** If using webcam, include your face (increases clicks)

---

### **Phase 7: Upload to YouTube (30 min per tutorial)**

#### Step 7.1: Prepare Metadata

```bash
# Create file: tutorial1_metadata.txt

Title:
HypatiaX Tutorial 1: Setting up the Environment

Description:
This tutorial demonstrates how to install and configure HypatiaX, 
a hybrid framework combining LLMs with symbolic regression for 
scientific equation discovery.

🎯 What You'll Learn:
• Install Python, Julia, and PySR
• Clone the HypatiaX repository
• Configure environment variables
• Run your first "Hello World" experiment

⏱️ Timestamps:
0:00 - Introduction
1:15 - Prerequisites Check
2:30 - Repository Clone
3:45 - Dependency Installation
6:00 - Julia/PySR Setup
8:15 - First Experiment
9:30 - Conclusion

📚 Resources:
• Paper: https://arxiv.org/abs/XXXX.XXXXX
• Code: https://github.com/your-org/hypatiax
• Cheat Sheet: [link to PDF]

🔗 Tutorial Series:
• Tutorial 2: Running Experiments
• Tutorial 3: Analyzing Results
• Tutorial 4: Extending Domains

#MachineLearning #ScientificComputing #SymbolicRegression #LLM

Tags:
machine learning, scientific computing, symbolic regression, 
LLM, Python, Julia, PySR, equation discovery, HypatiaX
```

#### Step 7.2: Upload Process

```bash
1. Go to: https://studio.youtube.com
2. Click "Create" → "Upload videos"
3. Select: HypatiaX_Tutorial1_Setup.mp4
4. While uploading:
   
   Details tab:
   - Title: [paste from metadata.txt]
   - Description: [paste from metadata.txt]
   - Thumbnail: Upload HypatiaX_Tutorial1_Thumbnail.png
   - Playlist: Create "HypatiaX Tutorials"
   - Audience: Not made for kids
   - Age restriction: No
   
   Video elements tab:
   - Add End screen: Link to Tutorial 2
   - Add Cards: At key moments, link to resources
   
   Checks tab:
   - Review copyright issues
   - Check for content issues
   
   Visibility tab:
   - Set to "Unlisted" initially (for testing)
   - Or "Public" when ready
   
5. Click "Publish"
```

#### Step 7.3: Add Captions

```bash
# After upload completes:
# YouTube Studio → Subtitles
# Click "Add Language" → English
# Upload HypatiaX_Tutorial1_Setup.srt
# Review auto-sync
# Publish
```

---

## 🎯 Quick Reference: Tools Comparison

| Task | Tool | Free? | Difficulty | Output Quality |
|------|------|-------|------------|----------------|
| Screen Recording | OBS Studio | ✅ Yes | Medium | Excellent |
| Screen Recording | QuickTime (Mac) | ✅ Yes | Easy | Good |
| Screen Recording | Xbox Game Bar (Win) | ✅ Yes | Easy | Good |
| Video Editing | DaVinci Resolve | ✅ Yes | Medium | Excellent |
| Video Editing | Shotcut | ✅ Yes | Easy | Good |
| Video Editing | iMovie (Mac) | ✅ Yes | Easy | Good |
| Captions | YouTube Auto | ✅ Yes | Easy | Fair |
| Captions | Whisper AI | ✅ Yes | Medium | Excellent |
| Thumbnails | GIMP | ✅ Yes | Medium | Excellent |
| Thumbnails | Canva | ✅ Free tier | Easy | Good |

---

## 📊 Complete Timeline: One Tutorial

| Phase | Time | Cumulative |
|-------|------|------------|
| 1. OBS Setup (one-time) | 2 hours | 2h |
| 2. Pre-production | 30 min | 2.5h |
| 3. Recording | 45 min | 3.25h |
| 4. Editing | 1.5 hours | 4.75h |
| 5. Captions | 30 min | 5.25h |
| 6. Thumbnail | 15 min | 5.5h |
| 7. Upload | 30 min | 6h |

**First tutorial:** ~6 hours  
**Tutorials 2-4:** ~4 hours each (no setup)  
**Total for all 4:** ~18 hours

---

## 💡 Pro Tips

### Recording Tips

✅ **Do:**
- Record in 10-15 minute segments (easier to edit)
- Use a quiet room (closet with blankets works!)
- Speak 20% slower than normal
- Zoom terminal to 150-200%
- Take breaks every 30 minutes

❌ **Don't:**
- Type too fast (viewers can't follow)
- Forget to unmute microphone
- Record at night (different lighting)
- Edit while recording (do it later)

### Editing Tips

✅ **Do:**
- Cut liberally (shorter is better)
- Add 2-second fade in/out
- Speed up long operations (2-4x)
- Add text callouts for key points

❌ **Don't:**
- Leave >5 second pauses
- Forget chapter markers
- Over-edit (some pauses are natural)
- Add too many effects (distracting)

### YouTube Tips

✅ **Do:**
- Upload on same day/time each week
- Reply to comments within 24 hours
- Pin helpful comments
- Create playlist of all tutorials
- Cross-link in descriptions

❌ **Don't:**
- Use copyrighted music
- Clickbait thumbnails
- Ignore comments
- Forget timestamps in description

---

## 🚀 Automated Workflow (Advanced)

If you want to streamline the process:

```bash
#!/bin/bash
# record_tutorial.sh

TUTORIAL_NUM=$1

# 1. Setup recording environment
./setup_demo_env.sh

# 2. Launch OBS with specific scene
obs --scene "Tutorial $TUTORIAL_NUM" --start-recording &

# 3. Run tutorial script (interactive)
cat video_tutorial_guide.md | grep "Tutorial $TUTORIAL_NUM" -A 200

# 4. Stop recording when done (manual)
# Press F10 in OBS

# 5. Auto-convert mkv to mp4
VIDEO=$(ls -t ~/Videos/*.mkv | head -1)
ffmpeg -i "$VIDEO" -c:v libx264 -crf 18 -c:a aac \
    "Tutorial${TUTORIAL_NUM}_Raw.mp4"

# 6. Generate auto-captions
whisper "Tutorial${TUTORIAL_NUM}_Raw.mp4" \
    --model medium --language English

echo "✓ Recording complete!"
echo "✓ Captions generated"
echo "Next: Edit in DaVinci Resolve"
```

---

## 📝 Checklist Template

Print this for each tutorial:

```
Tutorial #: _____
Date: _________

PRE-PRODUCTION
□ OBS configured
□ Microphone tested
□ Clean environment prepared
□ All commands tested
□ Script reviewed
□ Title slide created

RECORDING
□ Phone on silent
□ Notifications off
□ Good audio levels
□ Recording started (F9)
□ Followed script
□ Recording stopped (F10)
□ File renamed

EDITING
□ Imported to DaVinci
□ Cut dead air
□ Sped up long operations
□ Added chapter markers
□ Color corrected
□ Exported MP4

POST-PRODUCTION
□ Captions generated
□ Captions edited
□ Thumbnail created
□ Metadata prepared

UPLOAD
□ Video uploaded
□ Captions added
□ Thumbnail set
□ Playlist updated
□ Published
□ Posted to social media

NOTES:
_________________________________
_________________________________
_________________________________
```

---

## 🎬 Final Thoughts

**Start simple!** Your first tutorial doesn't need to be perfect:
- Use whatever mic you have (even phone headphones)
- Use QuickTime/Xbox Game Bar if OBS is too complex
- Use iMovie/Shotcut if DaVinci is overwhelming
- Let YouTube auto-generate captions

**Then improve:**
- Tutorial 2: Better mic
- Tutorial 3: Better editing
- Tutorial 4: Better thumbnail

The most important thing is to **just start recording!**

---

## 📚 Additional Resources

**OBS Tutorials:**
- https://www.youtube.com/watch?v=EuSUPpoi0Vs (OBS Setup)
- https://www.youtube.com/watch?v=HtEw-5SJTsM (Best Settings)

**DaVinci Resolve Tutorials:**
- https://www.youtube.com/watch?v=63Ln33O4p4c (Beginner's Guide)
- https://www.youtube.com/watch?v=wPEI8-MdH3k (Quick Cuts)

**YouTube Best Practices:**
- https://creatoracademy.youtube.com/ (Official YouTube Guides)
- https://vidiq.com/ (Analytics and optimization)

---

**Ready to start? Begin with Tutorial 1 and iterate from there! 🚀**
