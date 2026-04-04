# HypatiaX Video Tutorial Recording Guide

## Quick Setup (15 minutes)

### 1. Install Screen Recording Software

**Option A: OBS Studio (Recommended - Free & Professional)**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install obs-studio

# macOS
brew install --cask obs

# Windows: Download from https://obsproject.com/
```

**Option B: Simple Alternatives**
- **macOS**: Use built-in QuickTime Player (File → New Screen Recording)
- **Windows**: Use built-in Xbox Game Bar (Win+G)
- **Linux**: SimpleScreenRecorder, Kazam

### 2. Configure OBS Studio (Recommended Settings)

1. **Open OBS Studio**
2. **Scene Setup:**
   - Click "+" under "Scenes" → Name it "Tutorial"
   - Click "+" under "Sources" → Add "Screen Capture"
   - Select your main monitor

3. **Settings (Settings → Output):**
   - Output Mode: Simple
   - Recording Quality: High Quality, Medium File Size
   - Recording Format: mp4
   - Encoder: Software (x264)

4. **Settings (Settings → Video):**
   - Base Resolution: 1920x1080
   - Output Resolution: 1920x1080
   - FPS: 30 (or 60 if your system can handle it)

5. **Settings (Settings → Audio):**
   - Desktop Audio: Your speakers (for system sounds)
   - Mic/Auxiliary Audio: Your microphone

### 3. Test Your Setup

```bash
# Quick 30-second test:
# 1. Start recording in OBS (click "Start Recording")
# 2. Open a terminal
# 3. Type a few commands
# 4. Talk for 30 seconds
# 5. Stop recording
# 6. Watch the video to check quality
```

---

## Recording Workflow

### Before Each Tutorial:

1. **Prepare Your Environment**
   ```bash
   # Close unnecessary applications
   # Clear terminal history: history -c
   # Set terminal to comfortable font size (14-16pt)
   # Open all needed windows/files
   ```

2. **Recording Checklist:**
   - [ ] Close email, Slack, notifications
   - [ ] Clear desktop of sensitive/personal files
   - [ ] Test microphone volume
   - [ ] Have tutorial script open on second monitor (or printed)
   - [ ] Glass of water nearby
   - [ ] Do Not Disturb mode ON

3. **Start Recording:**
   - Take a deep breath
   - Start OBS recording
   - Count to 3 silently (gives you buffer to edit out)
   - Begin speaking

### During Recording:

**If you make a mistake:**
- PAUSE for 3 seconds of silence
- Restart the sentence/section
- Continue
- (You'll edit out mistakes later)

**Speaking Tips:**
- Speak slower than normal conversation
- Pause between major steps
- Describe what you're doing as you do it
- Use phrases like "Now we'll..." "Next, we'll..." "Notice that..."

### After Recording:

1. **Stop recording** in OBS
2. **Find your video** (usually in your Videos folder)
3. **Watch it through** - note timestamps of mistakes to edit out
4. **Basic editing** (if needed) - see Simple Editing section below

---

## Recording Each Tutorial

### Tutorial 1: Environment Setup (10 min)
**Script location:** tutorial_1_setup_script.md

**What to record:**
1. Start with clean system
2. Show installation steps
3. Verify installation
4. Run "hello world" test

**Key commands to demonstrate:**
```bash
# These will be in your detailed script
pip install hypatiax
python -c "import hypatiax; print('Success!')"
```

### Tutorial 2: Running Experiments (15 min)
**Script location:** tutorial_2_experiments_script.md

**What to record:**
1. Overview of test suite
2. Run a single domain
3. Interpret JSON output
4. Show results

### Tutorial 3: Analyzing Results (20 min)
**Script location:** tutorial_3_analysis_script.md

**What to record:**
1. Generate plots
2. Statistical validation
3. Interpret results
4. Export figures

### Tutorial 4: Extending to New Domains (25 min)
**Script location:** tutorial_4_extensions_script.md

**What to record:**
1. Add new domain example
2. Custom validation rules
3. Integration workflow
4. Test new domain

---

## Simple Video Editing

### Option A: No Editing (Quick & Easy)
Just upload the raw video! It's fine to have a few pauses or minor mistakes. Real tutorials are relatable.

### Option B: Basic Trim (5 minutes)
Use free tools to cut beginning/end:

**Online (No Install):**
- https://online-video-cutter.com/
- Trim first/last few seconds

**Desktop:**
```bash
# Using ffmpeg (if installed)
# Trim first 3 seconds and last 5 seconds:
ffmpeg -i input.mp4 -ss 00:00:03 -to 00:09:55 -c copy output.mp4
```

### Option C: Full Editing (If needed)
- **DaVinci Resolve** (Free, professional)
- **OpenShot** (Free, simple)
- **iMovie** (macOS, free)

---

## YouTube Upload Checklist

For each video:

### 1. Title Format:
```
HypatiaX Tutorial [#]: [Topic] - [Brief Description]

Examples:
HypatiaX Tutorial 1: Environment Setup - Installing and Verifying HypatiaX
HypatiaX Tutorial 2: Running Experiments - Your First Test Suite
```

### 2. Description Template:
```
This tutorial covers [main topic] for the HypatiaX framework from our JMLR paper "LLMs as Interfaces to Symbolic Discovery"

🎯 What You'll Learn:
• [Key point 1]
• [Key point 2]
• [Key point 3]

⏰ Timestamps:
0:00 - Introduction
1:00 - [Section 1]
3:30 - [Section 2]
...

📚 Resources:
• Paper: [link]
• Code: [github link]
• Documentation: [link]

📋 Next Tutorial: [Link to next video]
```

### 3. Tags:
```
machine learning, symbolic regression, LLM, research, tutorial, python, scientific computing, JMLR, reproducible research
```

### 4. Thumbnail:
Simple thumbnail ideas:
- Screenshot from video with large text overlay: "Tutorial 1: Setup"
- Your terminal with a command visible
- (Don't spend more than 5 minutes on this)

---

## Realistic Timeline

**Per Tutorial:**
- Preparation: 30 min
- Recording attempt 1: [Tutorial length]
- Watch & note edits: [Tutorial length]
- Recording attempt 2 (if needed): [Tutorial length]
- Basic editing: 15 min
- Upload & metadata: 10 min

**Total per tutorial: 2-3 hours**

**All 4 tutorials: 1-2 days of focused work**

---

## Pro Tips

✅ **DO:**
- Record in a quiet room
- Use a decent microphone (even earbuds are better than laptop mic)
- Speak clearly and at a moderate pace
- Pause between sections
- Test your setup with a 30-second recording first
- Keep tutorials focused and practical

❌ **DON'T:**
- Worry about perfection - authentic is better
- Edit excessively - viewers appreciate real tutorials
- Rush through complex steps
- Forget to show the output/results
- Record when tired or rushed

---

## Troubleshooting

**Problem: Audio is too quiet**
- Move microphone closer
- Increase input volume in OBS Audio Mixer
- Use Audacity to normalize volume after recording

**Problem: Terminal text is too small**
- Increase font to 14-16pt
- Use high contrast color scheme
- Zoom in if needed

**Problem: Video file is huge**
```bash
# Compress with ffmpeg (minimal quality loss):
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 output.mp4
```

**Problem: Made too many mistakes**
- That's normal! Either:
  - Edit them out
  - Re-record that section
  - Or leave them in - it's relatable!

---

## Ready to Start?

1. ✅ Install OBS Studio (or alternative)
2. ✅ Do 30-second test recording
3. ✅ Read Tutorial 1 script (tutorial_1_setup_script.md)
4. ✅ Record Tutorial 1
5. ✅ Upload to YouTube
6. ✅ Repeat for tutorials 2-4

**You've got this! 🎬**
