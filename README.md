# Claude Usage Tracker

멀티 디바이스 Claude Code 사용량을 Git으로 통합 관리하는 시스템입니다.

## 🎯 시스템 개요

각 컴퓨터(맥북, Windows PC 등)에서 로컬 Claude Code 사용량을 자동으로 Git 저장소에 동기화하고, 모든 기기의 사용량을 합산해서 확인할 수 있습니다.

```
맥북 A ──┐
맥북 B ──┼─→ Git Repo ─→ 전체 사용량 합산
윈도우 PC ─┘
```

## 📊 사용 명령어

| 명령어 | 범위 | 설명 |
|--------|------|------|
| `ccusage` | 현재 컴퓨터만 | 로컬 사용량 즉시 확인 |
| `ccusage-sync` | 현재 컴퓨터 → Git | 로컬 사용량을 Git에 업로드 |
| `ccusage-total` | 모든 컴퓨터 합산 | Git에서 받아서 전체 사용량 표시 |

## 🚀 맥북 설정

```bash
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. 설정 파일
mkdir -p ~/.claude
cat > ~/.claude/usage_sync_config.json << 'CONFIG'
{
  "repo_path": "$HOME/claude-usage-tracker",
  "data_dir": "$HOME/claude-usage-tracker/data"
}
CONFIG

# 3. Alias 설정
cat >> ~/.zshrc << 'ALIASES'
alias ccusage='python3 ~/claude-usage-tracker/scripts/calculate_usage.py'
alias ccusage-sync='python3 ~/claude-usage-tracker/scripts/ccusage_sync.py'
alias ccusage-total='python3 ~/claude-usage-tracker/scripts/ccusage_total.py'
ALIASES
source ~/.zshrc

# 4. Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. 첫 Sync
ccusage-sync
```

## 🪟 Windows PC 설정

**Git Bash 사용 (추천):**

```bash
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. 설정 파일
mkdir -p ~/.claude
cat > ~/.claude/usage_sync_config.json << 'CONFIG'
{
  "repo_path": "$HOME/claude-usage-tracker",
  "data_dir": "$HOME/claude-usage-tracker/data"
}
CONFIG

# 3. Alias 설정
cat >> ~/.bashrc << 'ALIASES'
alias ccusage='python ~/claude-usage-tracker/scripts/calculate_usage.py'
alias ccusage-sync='python ~/claude-usage-tracker/scripts/ccusage_sync.py'
alias ccusage-total='python ~/claude-usage-tracker/scripts/ccusage_total.py'
ALIASES
source ~/.bashrc

# 4. Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. 첫 Sync
ccusage-sync
```

**PowerShell 사용:**

```powershell
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. 설정 파일
mkdir -Force $env:USERPROFILE\.claude
@"
{
  "repo_path": "$env:USERPROFILE\\claude-usage-tracker",
  "data_dir": "$env:USERPROFILE\\claude-usage-tracker\\data"
}
"@ | Out-File -FilePath $env:USERPROFILE\.claude\usage_sync_config.json -Encoding UTF8

# 3. Alias 설정
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
Add-Content $PROFILE @"
function ccusage { python `$env:USERPROFILE\claude-usage-tracker\scripts\calculate_usage.py }
function ccusage-sync { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_sync.py }
function ccusage-total { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_total.py }
"@

# 4. PowerShell 재시작 후 Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. 첫 Sync
ccusage-sync
```

## 📖 사용 방법

**로컬만 확인:**
```bash
ccusage
```

**주간 업로드 (매주 월요일):**
```bash
ccusage-sync
```

**월말 전체 확인:**
```bash
ccusage-total
```

## 📁 저장소 구조

```
claude-usage-tracker/
├── README.md
├── scripts/
│   ├── calculate_usage.py   # 로컬 사용량 계산
│   ├── export_usage.py      # JSON export
│   ├── ccusage_sync.py      # Git sync
│   └── ccusage_total.py     # 전체 합산
└── data/
    ├── macbook.json
    ├── windows-pc.json
    └── ...
```

## 🔧 트러블슈팅

**"No usage data found":**
- 맥북: `~/.claude/projects/` 확인
- Windows: `%APPDATA%\Claude\projects\` 확인

**Git push 실패:**
```bash
gh auth status
gh auth login
```

**Python 없음:**
```bash
# Windows
winget install Python.Python.3.12

# macOS (Homebrew)
brew install python3
```

---

**Made with Claude Code** 🤖
