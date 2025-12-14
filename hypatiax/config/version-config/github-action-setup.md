# 🤖 GitHub Actions - Automatic Version Management

## ⚡ What This Does (Automatically!)

- ✅ Creates snapshots when you push code
- ✅ Updates version numbers automatically
- ✅ Creates daily backups at 2 AM
- ✅ Stores backups as downloadable artifacts
- ✅ Commits version updates back to your repo

**You don't need to do anything manually!**

---

## 🚀 Setup (Just 3 Steps)

### Step 1: Create the workflow file

In your repository, create this file:

```
.github/workflows/version-management.yml
```

Copy the content from the **"Simple GitHub Actions"** artifact into this file.

### Step 2: Commit and push

```bash
cd ~/Downloads/LLM-HypatiaX-OLD/hypatiax

git add .github/workflows/version-management.yml
git commit -m "Add automatic version management"
git push
```

### Step 3: Enable GitHub Actions (if not already enabled)

1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Click **Save**

---

## ✅ That's It

Now every time you:

- **Push code** → Automatic snapshot + version update
- **Daily at 2 AM** → Automatic daily backup
- **Manual trigger** → Can trigger from GitHub UI anytime

---

## 📥 How to Download Backups

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click on any completed workflow run
4. Scroll down to **Artifacts**
5. Download `snapshot-xxxxx.zip`
6. Unzip to restore files

---

## 🎯 What Gets Created

After the workflow runs, you'll have:

```
your-repo/
├── .github/workflows/
│   └── version-management.yml    ← The automation
├── .versions/
│   └── metadata.json             ← Version tracking
├── scripts/version_management/
│   └── version_manager.py        ← Auto-created
└── .env.versions                 ← Version numbers
```

---

## 📊 Viewing Version Status

### On GitHub

1. Go to **Actions** tab
2. Click any workflow run
3. Look at the **Summary** - shows current versions!

### In Your Code

After the workflow runs, you can:

```bash
# Pull latest changes
git pull

# Load versions
source .env.versions

# Check what version you're on
echo $HYPATIAX_RULES_VERSION
echo $HYPATIAX_TRAINING_VERSION
echo $HYPATIAX_MODELS_VERSION
```

---

## 🔧 Manual Trigger (Optional)

Want to create a snapshot manually?

1. Go to **Actions** tab
2. Click **Auto Version Management**
3. Click **Run workflow**
4. Click **Run workflow** button
5. Done! Snapshot created.

---

## ⚙️ Configuration (Optional)

### Change backup schedule

Edit `.github/workflows/version-management.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Change '2' to your preferred hour (UTC)
```

### Change retention period

Edit the upload artifact step:

```yaml
retention-days: 30  # Change to 7, 90, etc.
```

---

## 🆘 Troubleshooting

### Workflow not running?

**Check:**

1. File is at `.github/workflows/version-management.yml`
2. File is valid YAML (no tabs, proper spacing)
3. Actions are enabled in Settings → Actions

### Permission errors?

**Fix:**

1. Go to Settings → Actions → General
2. Select "Read and write permissions"
3. Save

### Want to see what happened?

1. Go to Actions tab
2. Click on the failed/completed run
3. Click on the job name
4. Expand each step to see details

---

## 💡 Pro Tips

1. **Don't worry about .versions/ folder getting huge** - GitHub Actions uploads it as artifacts, not in your repo
2. **The workflow commits back** - It updates `.env.versions` and `metadata.json` automatically
3. **Artifacts expire** - Download important snapshots before they expire (default: 30 days)
4. **Manual triggers are your friend** - Use them before major changes!

---

## 🎉 That's Everything

Once set up, it just works automatically. No daily commands to remember!

**Set it and forget it!** 🚀More-guide.md
