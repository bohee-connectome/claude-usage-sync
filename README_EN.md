# Claude Usage Tracker

> **Created by Bohee Lee** | [한국어 버전](./README.md)

A system for centrally managing Claude Code usage across multiple devices via Git.

## 🌐 Website

**Check your total usage in a browser:**

👉 **https://bohee-connectome.github.io/claude-usage-sync**

- ✅ **Real-time data fetching** - Directly retrieves latest data from GitHub
- ✅ **Auto-refresh** - Updates every 5 minutes (manual refresh also available)
- ✅ **Cache-free** - Reflects immediately after `ccusage-sync` execution
- ✅ **All devices combined** - View total statistics at a glance
- ✅ **Responsive design** - Mobile/tablet support
- ✅ **No login required** - Access from anywhere
- ✅ **Completely free** - Hosted on GitHub Pages

## 🎯 System Overview

Automatically sync local Claude Code usage from each computer (MacBook, Windows PC, etc.) to a Git repository and check combined usage from all devices.

```
MacBook A ──┐
MacBook B ──┼─→ Git Repo ─→ Total usage aggregation
Windows PC ─┘
```

## 📊 Usage Commands

| Method | Scope | Description |
|--------|-------|-------------|
| **[Website](https://bohee-connectome.github.io/claude-usage-sync)** | All devices combined | Real-time view in browser (from anywhere) |
| `ccusage` | Current computer only | Check local usage in terminal |
| `ccusage-sync` | Current computer → Git | Upload local usage to Git |
| `ccusage-total` | All devices combined | Show total usage in terminal |

## 🚀 MacBook Setup

```bash
# 1. Clone repository
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. Configuration file
mkdir -p ~/.claude
cat > ~/.claude/usage_sync_config.json << 'CONFIG'
{
  "repo_path": "$HOME/claude-usage-tracker",
  "data_dir": "$HOME/claude-usage-tracker/data"
}
CONFIG

# 3. Alias setup
cat >> ~/.zshrc << 'ALIASES'
alias ccusage='python3 ~/claude-usage-tracker/scripts/calculate_usage.py'
alias ccusage-sync='python3 ~/claude-usage-tracker/scripts/ccusage_sync.py'
alias ccusage-total='python3 ~/claude-usage-tracker/scripts/ccusage_total.py'
ALIASES
source ~/.zshrc

# 4. Git configuration
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. First sync
ccusage-sync
```

## 🪟 Windows PC Setup

**Using Git Bash (Recommended):**

```bash
# 1. Clone repository
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. Configuration file
mkdir -p ~/.claude
cat > ~/.claude/usage_sync_config.json << 'CONFIG'
{
  "repo_path": "$HOME/claude-usage-tracker",
  "data_dir": "$HOME/claude-usage-tracker/data"
}
CONFIG

# 3. Alias setup
cat >> ~/.bashrc << 'ALIASES'
alias ccusage='python ~/claude-usage-tracker/scripts/calculate_usage.py'
alias ccusage-sync='python ~/claude-usage-tracker/scripts/ccusage_sync.py'
alias ccusage-total='python ~/claude-usage-tracker/scripts/ccusage_total.py'
ALIASES
source ~/.bashrc

# 4. Git configuration
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. First sync
ccusage-sync
```

**Using PowerShell:**

```powershell
# 1. Clone repository
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. Configuration file
mkdir -Force $env:USERPROFILE\.claude
@"
{
  "repo_path": "$env:USERPROFILE\\claude-usage-tracker",
  "data_dir": "$env:USERPROFILE\\claude-usage-tracker\\data"
}
"@ | Out-File -FilePath $env:USERPROFILE\.claude\usage_sync_config.json -Encoding UTF8

# 3. Alias setup
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
Add-Content $PROFILE @"
function ccusage { python `$env:USERPROFILE\claude-usage-tracker\scripts\calculate_usage.py }
function ccusage-sync { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_sync.py }
function ccusage-total { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_total.py }
"@

# 4. Restart PowerShell, then configure Git
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. First sync
ccusage-sync
```

## 📖 How to Use

**Check local only:**
```bash
ccusage
```

**Weekly upload (every Monday):**
```bash
ccusage-sync
```

**Check total at month-end:**
```bash
ccusage-total
```

## 📁 Repository Structure

```
claude-usage-tracker/
├── README.md
├── index.html              # GitHub Pages website
├── scripts/
│   ├── calculate_usage.py   # Calculate local usage
│   ├── export_usage.py      # JSON export
│   ├── ccusage_sync.py      # Git sync
│   └── ccusage_total.py     # Total aggregation
└── data/
    ├── macbook.json
    ├── windows-pc.json
    └── ...
```

## 🎁 Using This Project for Yourself

To use this project in your own GitHub account:

### 1️⃣ Copy Repository

**Method A: Fork (Recommended)**
1. Click the "Fork" button on this repository's GitHub page
2. It will be copied to your account

**Method B: Create New Repository**
```bash
gh repo create my-claude-usage-sync --public
cd ~/my-claude-usage-sync
# Copy files from this repository
```

### 2️⃣ Modify index.html (Important!)

Open the `index.html` file and modify the configuration around **line 249**:

```javascript
// Change this to your GitHub account/repository
const GITHUB_REPO = 'bohee-connectome/claude-usage-sync';  // ❌ Original
const GITHUB_REPO = 'your-username/your-repo-name';        // ✅ Change to yours
```

**Example:**
```javascript
const GITHUB_REPO = 'john-doe/my-claude-tracker';
```

### 3️⃣ Enable GitHub Pages

1. GitHub repository → **Settings** tab
2. Click **Pages** in left menu
3. **Source** settings:
   - Branch: Select `main`
   - Folder: Select `/ (root)`
   - Click **Save**
4. After 1-2 minutes, check website URL:
   - `https://your-username.github.io/your-repo-name`

### 4️⃣ Install on Each Device

Follow the "MacBook Setup" or "Windows PC Setup" guide above, but clone **your repository**:

```bash
# Clone your repository
gh repo clone your-username/your-repo-name claude-usage-tracker

# Configure the rest the same way
```

### 5️⃣ Done!

- Terminal: Use `ccusage`, `ccusage-sync`, `ccusage-total`
- Website: Visit `https://your-username.github.io/your-repo-name`

---

## 🔧 Troubleshooting

**"No usage data found":**
- MacBook: Check `~/.claude/projects/`
- Windows: Check `%APPDATA%\Claude\projects\`

**Git push failure:**
```bash
gh auth status
gh auth login
```

**Python not found:**
```bash
# Windows
winget install Python.Python.3.12

# macOS (Homebrew)
brew install python3
```

---

## 👤 Credits

**Created & Directed by [Bohee Lee](https://github.com/bohee-connectome)**

Built with [Claude Code](https://claude.ai/code) 🤖

---

© 2025 Bohee Lee | [한국어 버전](./README.md)
